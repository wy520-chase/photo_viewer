import io
import os
import re
import json
import time
import random
import bisect
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from threading import Lock, Thread, Semaphore
from myapp.function.basic import app_logger

# 预编译正则表达式
_digit_splitter = re.compile(r'(\d+)')
def natural_sort_key(integer):
    """
    生成自然排序的键值，使得字符串中的数字部分按照自然数字顺序进行排序。

    :param integer: 需要排序的字符串
    :return: 一个由元组组成的列表，用于排序
    """
    # 使用预编译正则表达式进行分割
    parts = _digit_splitter.split(integer)

    # 将数字部分转换为整数，其他部分保持原样
    return [(int(part), '') if part.isdigit() else (0, part.lower()) for part in parts if part]

def get_image_size(path):
    try:
        with open(path, 'rb') as f:
            data = f.read(4096)
            if data.startswith(b'\xff\xd8'):
                result = get_jpeg_size(data)
                if result is not None:
                    return path, result
            elif data.startswith(b'\x89PNG\r\n\x1a\n'):
                result = get_png_size(data)
                if result is not None:
                    return path, result
            elif data.startswith(b'BM'):
                result = get_bmp_size(data)
                if result is not None:
                    return path, result
            # 如果前面的方法都未能获取尺寸，继续读取剩下的文件内容
            # 并组合成完整的文件内容
            # print(f'使用PIL打开图片{path}')
            remaining_data = f.read()
            full_data = data + remaining_data
            # 使用 PIL 打开图片
            img_stream = io.BytesIO(full_data)
            img = Image.open(img_stream)
            return path, img.width / img.height
    except Exception as e:
        app_logger.info(f'获取图片{path}尺寸失败：{e}')
        return path, 1

def get_jpeg_size(data):
    try:
        idx = 2  # 跳过JPEG文件标识 (FFD8)
        while idx < len(data):
            if data[idx] != 0xff:  # 寻找标记前缀 0xFF
                idx += 1
                continue
            marker = data[idx + 1]
            idx += 2
            if 0xc0 <= marker <= 0xcf:  # 查找 SOF 标记 (0xFFC0 - 0xFFC3)
                if idx + 5 < len(data):  # 确保数据足够进行大小解析
                    h = int.from_bytes(data[idx + 3:idx + 5], 'big')  # Height
                    w = int.from_bytes(data[idx + 5:idx + 7], 'big')  # Width
                    return w / h
            segment_length = int.from_bytes(data[idx:idx + 2], 'big')
            idx += segment_length
        return None
    except Exception as e:
        app_logger.debug(f'获取jpg图像尺寸异常:{e}')
        return None

def get_png_size(data):
    try:
        if data[12:16] == b'IHDR':
            width = int.from_bytes(data[16:20], 'big')
            height = int.from_bytes(data[20:24], 'big')
            return width / height
        return None
    except Exception as e:
        app_logger.debug(f'获取png图像尺寸异常:{e}')
        return None

def get_bmp_size(data):
    try:
        width = int.from_bytes(data[18:22], 'little')
        height = int.from_bytes(data[22:26], 'little')
        return width / height
    except Exception as e:
        app_logger.debug(f'获取bmp图像尺寸异常:{e}')
        return None

def get_cached_info(path, current_tree):
    """
    :param current_tree: 指定要搜索的缓存字典(可选)
    :param path: 相对root的目录路径-字符串
    :return: 获取给定路径在文件树中的信息:字典或数字或None;如果路径在文件树中不存在，则返回None。
    """
    # 规范化路径
    if path == '.' or path == '':
        return current_tree
    normalized_path = os.path.normpath(path)
    # 分割路径
    parts = normalized_path.split(os.sep)
    # 遍历路径片段
    for part in parts:
        if part == '':
            continue  # 跳过空字符串
        if part not in current_tree:
            return None  # 如果路径片段不存在，则返回None
        current_tree = current_tree[part]
    return current_tree

class FileTree:
    def __init__(self, json_path, root_directory):
        self._lock = Lock()
        self._file_path = json_path
        self._root_directory = root_directory
        self._file_tree = {}  # 存储文件树
        self._new_image_paths = []  # 存储新图片路径
        self._saved_tree = []  # 存储缓存数据
        self._futures = []  # 存储异步任务
        # 检查缓存并加载
        if os.path.isfile(json_path):
            app_logger.info('发现缓存的数据，开始读取')
            time1 = time.time()
            with open(json_path, 'r', encoding='utf-8') as file:
                self._saved_tree = json.load(file)
            time2 = time.time()
            app_logger.info(f'读取缓存数据耗时{(time2 - time1) * 1000:.2f} ms')
        # 构建目录结构
        app_logger.info('开始读取目录结构')
        time1 = time.time()
        self._build_file_tree(self._root_directory, self._file_tree)
        time2 = time.time()
        app_logger.info(f'构建目录树耗时{(time2 - time1) * 1000:.2f} ms')
        
        # 收集所有图片路径并计算随机概率
        app_logger.info('开始收集图片路径并计算随机概率')
        time1 = time.time()
        # 预计算所有直接包含图片的目录及其图片数量
        self.directories = self._precompute_directories(self._file_tree)
        # 计算累积概率分布
        self.cumulative_probabilities, self.directory_list = self._compute_cumulative_probabilities(self.directories)
        time2 = time.time()
        app_logger.info(f'收集图片路径耗时{(time2 - time1) * 1000:.2f} ms')
        
        if self._new_image_paths:
            # 有要更新的数据，启动异步更新线程
            updater_thread = Thread(target=self._update_and_save_async)
            updater_thread.start()
        else:
            # 没有要更新的数据，直接保存到文件
            app_logger.info('没有要更新的数据')
            self._save_to_file()

    def _build_file_tree(self, node_path, node_tree):
        stack = [(node_path, node_tree)]
        max_queue_length = os.cpu_count() *2
        semaphore = Semaphore(max_queue_length)  # 用信号量来限制最大并发任务数

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            while stack:
                current_path, current_tree = stack.pop()
                entries = list(os.scandir(current_path))
                directories = [entry.name for entry in entries if entry.is_dir()]
                files = [entry.name for entry in entries if
                         entry.is_file() and entry.name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]

                directories.sort(key=natural_sort_key)

                for directory in directories:
                    sub_tree = {}
                    current_tree[directory] = sub_tree
                    stack.append((os.path.normpath(os.path.join(current_path, directory)), sub_tree))

                if files:
                    semaphore.acquire()  # 获取可用信号，确保队列不会超出限制
                    future = executor.submit(self._process_cached_info_bulk, files, current_path, current_tree)
                    self._futures.append(future)
                    future.add_done_callback(lambda f: (self._futures.remove(f), semaphore.release()))

            wait(self._futures)
            self._futures = []

    def _process_cached_info_bulk(self, files, current_path, current_tree):
        local_updates = {}
        paths_to_append = []
        current_relpath = os.path.relpath(current_path, self._root_directory)
        common_tree = get_cached_info(current_relpath, self._saved_tree)

        if common_tree is None:
            for file_name in files:
                local_updates[file_name] = None
                paths_to_append.append(os.path.join(current_path, file_name))
        else:
            for file_name in files:
                size_info = common_tree.get(file_name)
                if size_info is None:
                    paths_to_append.append(os.path.join(current_path, file_name))
                else:
                    local_updates[file_name] = size_info

        # 合并并加锁更新
        if local_updates or paths_to_append:
            # 自然序列排序
            local_updates = {key: local_updates[key] for key in sorted(local_updates, key=natural_sort_key)}
            with self._lock:
                current_tree.update(local_updates)
                self._new_image_paths.extend(paths_to_append)

    def _update_and_save_async(self):
        app_logger.info('开始异步更新图片信息并保存')
        time1 = time.time()
        max_workers = os.cpu_count()
        wait_queue_size = 3
        local_updates = {}
        if len(self._new_image_paths) < wait_queue_size:
            wait_queue_size = len(self._new_image_paths)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            # 初始提交一些任务
            for path in self._new_image_paths[:wait_queue_size]:
                future = executor.submit(get_image_size, path)
                futures.append(future)
            next_index = wait_queue_size
            # 处理已提交的任务，并继续提交新的任务
            while futures:
                for future in as_completed(futures):
                    path, size_info = future.result()
                    # 更新local_updates结构
                    if size_info:
                        normalized_path = os.path.normpath(os.path.relpath(path, self._root_directory))
                        parts = normalized_path.split(os.sep)
                        node = local_updates
                        for part in parts[:-1]:
                            node = node.setdefault(part, {})
                        node[parts[-1]] = size_info
                    # 移除已完成任务
                    futures = [f for f in futures if f != future]
                    # 提交新的任务以保持队列中有等待任务
                    if next_index < len(self._new_image_paths):
                        new_path = self._new_image_paths[next_index]
                        new_future = executor.submit(get_image_size, new_path)
                        futures.append(new_future)
                        next_index += 1
        with self._lock:
            self._merge_updates(self._file_tree, local_updates)
        # 释放内存
        self._new_image_paths = []
        self._futures = []
        time2 = time.time()
        app_logger.info(f'更新图片信息耗时{(time2 - time1) * 1000:.2f} ms')
        # 保存到文件
        self._save_to_file()

    def _merge_updates(self, tree, updates):
        for key, value in updates.items():
            if isinstance(value, dict):
                node = tree.setdefault(key, {})
                self._merge_updates(node, value)
            else:
                tree[key] = value

    def _save_to_file(self):
        app_logger.info(f'开始保存结果到文件')
        time1 = time.time()
        with open(self._file_path, 'w', encoding='utf-8') as f:
            with self._lock:
                json.dump(self._file_tree, f, ensure_ascii=False, indent=4)
        time2 = time.time()
        app_logger.info(f'保存结果到文件耗时{(time2 - time1) * 1000:.2f} ms')

    def read(self):
        with self._lock:
            return self._file_tree.copy()
    
    # 获取所有包含图片的目录及其图片数量
    def _precompute_directories(self, tree, current_path=""):
        directories = {}
        for key, value in tree.items():
            if isinstance(value, dict):
                # 检查当前目录是否直接包含图片
                image_count = sum(1 for k in value if isinstance(value[k], float))
                if image_count > 0:
                    directories[current_path + "/" + key if current_path else key] = image_count
                # 递归检查子目录
                directories.update(self._precompute_directories(value, current_path + "/" + key if current_path else key))
        return directories

    def _compute_cumulative_probabilities(self, directories):
        total_images = sum(directories.values())
        if total_images == 0:
            return [], []
        # 计算累积概率
        cumulative_probabilities = []
        directory_list = []
        cumulative_sum = 0
        for directory, count in directories.items():
            cumulative_sum += count / total_images
            cumulative_probabilities.append(cumulative_sum)
            directory_list.append(directory)
        return cumulative_probabilities, directory_list
    
    # 获取随机图片路径
    def random_directory(self):
        if not self.cumulative_probabilities:
            return None
        # 使用二分查找快速选择目录
        random_value = random.random()
        index = bisect.bisect_left(self.cumulative_probabilities, random_value)
        return self.directory_list[index]


if __name__ == "__main__":
    root = 'myapp/static/images'
    file_path = 'myapp/file_tree.json'
    FT = FileTree(file_path, root)
    # 获取目录树
    file_tree = FT.read()
    time.sleep(2)
    # 随机获取一张图片
    n = 0
    for i in range(1000):
        r = FT.random_directory()
        # print('随机获取一张图片', r)
        if r == '3':
            n += 1
    print('3出现概率', n/1000)

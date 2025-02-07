import os

from myapp.config import root
from myapp.function.basic import app_logger
from PIL import Image
from myapp.function.maintain_file_tree import get_cached_info, FileTree
from pathlib import Path
import time




class DiskIO:
    def __init__(self, json_path, root_directory):
        self._FileTree = FileTree(json_path, root_directory)
        self._file_tree = self._FileTree.read()

    def is_directory(self, path_relative_root):
        """
            :param path_relative_root: 相对root的目录路径
            :type path_relative_root: str
            :return: 根据路径是否是目录返回：True,False
            :rtype: bool
        """
        # 规范化路径
        normalized_path = os.path.normpath(path_relative_root)
        # 分割路径
        parts = normalized_path.split(os.sep)
        # 初始化当前树节点
        current_tree = self._file_tree
        # 遍历路径片段
        for part in parts:
            if part == '.' or part == '':
                return True  # 根目录
            if part not in current_tree:
                return False  # 路径不存在
            current_tree = current_tree[part]
        return isinstance(current_tree, dict)

    def is_empty(self, path_relative_root):
        """
            :param path_relative_root: 相对root的目录路径
            :type path_relative_root: str
            :return: 空目录True,不存在None，其他False
            :rtype: bool
        """
        # 标准化路径
        normalized_path = os.path.normpath(path_relative_root)
        # 分割路径
        parts = normalized_path.split(os.sep)
        # 初始化当前树节点
        current_tree = self._file_tree
        # 遍历路径片段
        for part in parts:
            if part == '':
                continue  # 空字符串
            if part not in current_tree:
                app_logger.info(f'来自is_empty_directory:路径({path_relative_root})不存在')
                return None  # 路径不存在
            current_tree = current_tree[part]
        # 检查子树是否为空字典
        return isinstance(current_tree, dict) and not current_tree

    def get_directory_contents(self, path_relative_root):
        """
        :param path_relative_root: 相对root的目录路径-字符串
        :type path_relative_root: str
        :return: 两个列表，第一个是子目录，第二个是图片。{'1.jpg': 'Path(1/1.jpg)','2.jpg': 'Path(1/2.jpg)'}
        :rtype: list,list
        """
        # 获取当前路径节点的信息
        # app_logger.debug(f'path_relative_root:{path_relative_root},self._file_tree:{self._file_tree}')
        current_tree = get_cached_info(path_relative_root, self._file_tree)

        if current_tree is None or not isinstance(current_tree, dict):
            return {}, {}
        else:
            current_folders = []
            current_images = []
            # 标准化路径
            normalized_path = os.path.normpath(path_relative_root)
            current_path = Path(normalized_path)
            for key, value in current_tree.items():
                # app_logger.debug(f'key:{key},{type(value)}')

                if isinstance(value, dict):
                    folder_name = key
                    folder_relative_root = current_path / key
                    preview_image_info = self.get_first_image(folder_relative_root)
                    # app_logger.debug(f'folder_name:{folder_name},path:{folder_relative_root.as_posix()},preview_image:{preview_image_info}')
                    folder_info = {
                        'name': folder_name,
                        'path': folder_relative_root.as_posix(),
                        'preview_image':preview_image_info
                    }
                    current_folders.append(folder_info)
                elif isinstance(value, float):
                    image_name = key
                    image_relative_root = current_path / key
                    aspect_ratio = value
                    image_info = {
                        'name': image_name,
                        'path': image_relative_root.as_posix(),
                        'is_pic': 1,
                        'aspect_ratio': aspect_ratio
                    }
                    current_images.append(image_info)
                elif isinstance(value, type(None)):
                    image_name = key
                    image_relative_root = current_path / key
                    aspect_ratio = self.get_image_size(image_relative_root)

                    image_info = {
                        'name': image_name,
                        'path': image_relative_root.as_posix(),
                        'is_pic': 1,
                        'aspect_ratio': aspect_ratio
                    }

                    current_images.append(image_info)
            directory_contents =current_folders + current_images

            return directory_contents

    def get_image_size(self, path_relative_root):
        """
        :param path_relative_root: 图像文件的路径,如"WindowsPath('123/photo/(642).jpg')"
        :type path_relative_root: str
        :return: 返回图像的尺寸比例width/height
        :rtype: float
        """
        # 获取缓存的信息
        cached_size = get_cached_info(path_relative_root, self._file_tree)
        if isinstance(cached_size, float):
            return cached_size
        else:
            app_logger.debug(f'来自get_image_size函数：重新计算{path_relative_root}的大小')
            try:
                with Image.open(Path(root) / path_relative_root) as img:
                    return img.width / img.height
            except Exception as e:
                app_logger.error(f'获取图片{path_relative_root}尺寸失败：{e}')
                return 1

    def get_first_image(self,path_relative_root):
      """
      获取目录中的第一张图片
      :param path_relative_root: 目录路径
      :return: 图片相对于root的路径，图片分辨率
      """
      # 获取当前路径节点的信息
      current_tree = get_cached_info(path_relative_root, self._file_tree)

      def get_first_image_info(nested_dict, current_path=""):
          # 首先查找当前字典层级的所有图片信息
          # print(f'当前层级字典:{nested_dict}')
          for key, value in nested_dict.items():
              full_path = Path(current_path) / key  if current_path else key
              # print(f'初次循环full_path:{full_path}, value:{value}')
              if not isinstance(value, dict):
                  if isinstance(value, float):
                      return full_path, value
                  else:
                      return full_path, self.get_image_size(full_path)
          # 如果未找到图片信息，则递归进入子字典
          for key, value in nested_dict.items():
              if isinstance(value, dict) and value:
                  result = get_first_image_info(value, Path(current_path) / key if current_path else key)
                  if result:
                      return result
          return None, None
      image_relative_root, aspect_ratio = get_first_image_info(current_tree, path_relative_root)
      if image_relative_root:
          image = {
              'path': image_relative_root.as_posix(),
              'aspect_ratio': aspect_ratio
          }
          return image
      else:
          return None

    def get_directory_images(self, path_relative_root):
        """
        :param path_relative_root: 相对root的目录路径-字符串
        :type path_relative_root: str
        :return: 每个元素是一个元组的列表，元组第一个元素是文件名，第二个元素是文件路径
        :rtype: list
        """
        # 获取当前路径节点的信息
        current_tree = get_cached_info(path_relative_root, self._file_tree)
        current_images = []
        if current_tree is None or not isinstance(current_tree, dict):
            return current_images
        else:
            # 标准化路径
            normalized_path = os.path.normpath(path_relative_root)
            current_path = Path(normalized_path)
            for key, value in current_tree.items():
                if isinstance(value, float) or isinstance(value, type(None)):
                    image_name = key
                    image_relative_root = current_path / key
                    image_info =(image_name, image_relative_root.as_posix())
                    current_images.append(image_info)
            return current_images

    def find_new_images_in_directory(self, path_relative_root, blacklisted_directories):
        """
        查找目录中的所有图片并返回图片路径列表和所在的文件夹名。
        :param blacklisted_directories: 已经查找过的相对目录列表
        :param path_relative_root: 相对root的目录路径-字符串
        :type path_relative_root: str
        :return: 包含 'images' (图片路径列表) 和 'directory' (所在文件夹名) 的字典。
        :rtype: dict
        """
        # app_logger.debug(f'{self._file_tree}')
        path_relative_root = Path(path_relative_root).as_posix()
        # app_logger.debug(f'开始查找{path_relative_root}下的图片，黑名单为{blacklisted_directories}')
        if path_relative_root not in blacklisted_directories:
            # 查找当前目录中的图片，元组(文件名，文件路径构成的列表)
            images_result = self.get_directory_images(path_relative_root)
            images = [_image_path for _, _image_path in images_result]
            blacklisted_directories.add(path_relative_root)
            # app_logger.debug(f'images_result:{images_result}')
            if images_result:
                app_logger.debug(f'返回路径{path_relative_root}, 图片列表{images}, 黑名单{blacklisted_directories}')
                return {'images':images , 'directory': path_relative_root}, blacklisted_directories

        current_tree = get_cached_info(path_relative_root, self._file_tree)
        # app_logger.debug(f'path_relative_root:{path_relative_root},current_tree:{current_tree}')
        if current_tree:
            for key, value in current_tree.items():
                if isinstance(value, dict):
                    folder_relative_root = (Path(path_relative_root) / key).as_posix()
                    if folder_relative_root not in blacklisted_directories:
                        # 递归查找不在黑名单的子目录
                        images_result, blacklisted_directories = self.find_new_images_in_directory(folder_relative_root, blacklisted_directories)
                        blacklisted_directories.add(folder_relative_root)
                        if images_result['images']:
                            app_logger.debug(f'找到了{folder_relative_root}的子目录下的图片')
                            return images_result, blacklisted_directories
        app_logger.debug(f'在{path_relative_root}下没有找到图片')
        # 避免重复查找根目录
        if path_relative_root == '' or path_relative_root == '.':
            app_logger.debug('为空目录的判断触发啦**********************************************************')
            return {'images': [], 'directory': path_relative_root}, blacklisted_directories
        # 获取父目录的路径
        parent_path_relative_root = os.path.dirname(path_relative_root)
        images_result, blacklisted_directories = self.find_new_images_in_directory(parent_path_relative_root, blacklisted_directories)
        if images_result['images']:
            app_logger.debug(f'找到了{parent_path_relative_root}的子目录下的图片')
            return images_result, blacklisted_directories
        else:
            return {'images': [], 'directory': path_relative_root}, blacklisted_directories

    def delete_item(self, path_relative_root):
        """
        从目录字典中删除指定路径下的子目录或文件信息，并从磁盘删除文件或目录。

        :param path_relative_root: 要删除的路径，例如 'root/subdir1/file1.txt'
        """
        # 拆分路径
        normalized_path = os.path.normpath(path_relative_root)
        parts = normalized_path.split(os.sep)
        current_dir = self._file_tree

        # 遍历路径
        for part in parts[:-1]:  # 不包含最后一个部分（即要删除的文件或目录名）
            if part not in current_dir:
                app_logger.info(f"目录不存在: {path_relative_root}")
                return False
            current_dir = current_dir[part]

        # 获取最后一个部分，即要删除的文件或目录名
        last_part = parts[-1]

        # 删除文件或目录
        if last_part in current_dir:
            item_path = Path(root) / path_relative_root

            # 检查路径是否为目录
            if self.is_directory(path_relative_root):
                # 检查目录是否为空或仅包含文件
                directory_contents = self.get_directory_contents(path_relative_root)
                for item in directory_contents:
                    app_logger.debug(f'item:{item}')
                    if 'preview_image' in item:
                        app_logger.error(f"目录包含子目录，不允许删除: {path_relative_root}")
                        return False
                # 删除目录
                try:
                    # 删除目录中的所有文件
                    for item in directory_contents:
                        full_path = Path(root) / item['path']
                        # app_logger.debug(f'要删除的item_path:{full_path}')
                        if os.path.isfile(full_path):
                            os.remove(full_path)
                            app_logger.info(f"已删除文件: {full_path}")
                    # 删除空目录
                    os.rmdir(item_path)
                    app_logger.info(f"已删除目录: {path_relative_root}")
                    del current_dir[last_part]
                    # 更新随机路径信息
                    self._FileTree.update_cumulative_probabilities(self._file_tree)
                    return True
                except OSError as e:
                    app_logger.error(f"删除目录失败: {path_relative_root} - {e}")
                    return False
            else:
                # 删除文件
                try:
                    os.remove(item_path)
                    del current_dir[last_part]
                    app_logger.info(f"已删除文件: {path_relative_root}")
                    return True
                except OSError as e:
                    app_logger.error(f"删除文件失败: {path_relative_root} - {e}")
                    return False
        else:
            app_logger.info(f"项目不在字典里: {path_relative_root}")
            return False

    def random_dir(self):
        """
        :return: 一个随机目录的路径。
        """
        return self._FileTree.random_directory()



if __name__ == "__main__":
    root = '../static/images'
    file_path = '../file_tree.json'
    diskio = DiskIO(file_path,root)
    diskio.delete_item('123/photo/超多图片/(113).jpg')


    '''
    blacklisted_directories = set()

    current_directory = 'PDL'
    while True:

        result, blacklisted_directories = diskio.find_new_images_in_directory(current_directory, blacklisted_directories)
        app_logger.debug(f'result:{result}')
        if result['images']:

            image_path = result['images'][0]
            current_directory = os.path.dirname(image_path)
            app_logger.debug(f'image_path:{image_path},current_directory:{current_directory}')
            app_logger.debug(f'从图片{image_path}计算出的所在目录是{current_directory}')
        else:
            break
    '''
    time.sleep(2)



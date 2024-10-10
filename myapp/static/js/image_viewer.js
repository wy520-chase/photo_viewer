let startX = 0;
let endX = 0;
let isDragging = false;
let dragDistance = 0;
let dragDistanceY = 0;
let threshold = window.innerWidth / 64; // 定义切换阈值
let intervalId;
let isDoubleTap = false;
let isNotZooming = true
let doubleTapTimeout = null;
let CarouselFpsList = [0.1, 0.3, 1, 3, 10, 24, 60];
CarouselFps = parseFloat(CarouselFps, 10)
// console.log('整合后:',CarouselFps)
if (! CarouselFpsList.includes(CarouselFps)) {
    // 如果不是有效的浮点数，则使用默认值
    CarouselFps = CarouselFpsList[3];
}
// console.log('CarouselFps:', CarouselFps, 'type:', typeof(CarouselFps))
let reverseCarousel = 0
// 假设我们限制缓存中最多保留100张图片
const MAX_CACHE_SIZE = 1000;
// 初始化图片引用
const loadedImages = {};
// console.log(imagesJson)
let images = JSON.parse(imagesJson);
// console.log(images)
const messageElement = document.getElementById('Message');
const imageContainer = document.getElementById('imageContainer');
const optionBar = document.getElementById('optionBar');
const optionText = document.getElementById('filename');
const topBarRight = document.getElementById('topBarRight');
// 计算另外两张图片位置
let leftImageIndex = (currentImageIndex - 1 + images.length) % images.length;
let rightImageIndex = (currentImageIndex + 1) % images.length;

// 获取最后一个斜杠的位置
const lastSlashIndex = images[0].lastIndexOf('/');
// 如果找不到斜杠，则返回空字符串（意味着文件位于根目录）
if (lastSlashIndex === -1) {
    folderPath = '';
} else {
    // 返回斜杠之前的字符串（即目录路径）
    folderPath = images[0].substring(0, lastSlashIndex);
}


// 页面加载完成之后触发
document.addEventListener('DOMContentLoaded', function() {
    // 添加对删除和点击按钮的监听
    document.getElementById('currentImage').addEventListener('click', () => {
        // 隐藏状态栏

        event.stopPropagation(); // 阻止事件冒泡
        // console.log('准备隐藏状态栏')
        document.getElementById('optionBar').classList.add('hidden');
        document.getElementById('rightImage').classList.add('image-enter-from-right');
        document.getElementById('currentImage').classList.add('image-exit-to-left');
        // 等待动画结束后刷新图片
        setTimeout(() => {
            // console.log('更新索引，全部左移，原索引:', leftImageIndex, currentImageIndex, rightImageIndex)
            // console.log('当前页面为:',currentImageIndex)
            // console.log('images总长度是:',images.length)
            if (currentImageIndex == images.length -1 ) {
                url = 'image_viewer_recursively?current_path=' + encodeURIComponent(folderPath) + '&carousel_fps=' + CarouselFps;
                location.replace(url)
            }
            leftImageIndex = currentImageIndex;
            currentImageIndex = rightImageIndex;
            rightImageIndex = (rightImageIndex + 1) % images.length;
            // 更新图片引用
            updateImages();
            // console.log('新的当前页面，供刷新使用:', currentImageIndex)
            sessionStorage.setItem('currentImageIndex', currentImageIndex);
        }, 100); // 假设动画时间为0.1秒

    })
    imageContainer.addEventListener('click', () => {
        // console.log('点击了图片容器')
        document.getElementById('optionBar').classList.toggle('hidden');
    })
    document.getElementById('deleteButton').addEventListener('click', handleClick);
    document.getElementById('subOptionButton').addEventListener('click', handleClick);
    document.getElementById('carouselButton').addEventListener('click', handleClick);
    optionText.addEventListener('click', handleClick);
    currentImage.addEventListener('dblclick', () => {
        event.stopPropagation(); // 阻止事件冒泡
        toggleImageZoom();
    });
    showMessage(folderName)
    updateImages()
    if (carousing){
        console.log('自动启动')
        handleCarousel();
    }
});

// 动态调整文本显示
function updateOptionText(imageName) {
    // 设置初始文本
    leftBarText = imageName + ' [' + (currentImageIndex + 1) + '/' + images.length + ']';
    optionText.textContent = leftBarText;
    console.log(leftBarText)
    // 获取容器的高度
    const containerHeight = optionText.offsetHeight;
    // 获取当前文本的高度
    const textHeight = optionText.scrollHeight;
    // 如果文本高度大于容器高度，则截断文本
    if (textHeight > containerHeight) {
        let truncatedText = '';
        // 计算最大允许长度
        let maxLength = leftBarText.length;
        while (maxLength > 0) {
            truncatedText = '...' + leftBarText.substring(leftBarText.length - maxLength);
            optionText.textContent = truncatedText;
            if (optionText.scrollHeight <= containerHeight) {
                break;
            }
            maxLength--;
        }
    }
}

function debounceImmediate(func, wait) {
  let timeoutId;
  let isFirstCall = true;

  return function(...args) {
    const context = this;

    // 第一次调用立即执行
    if (isFirstCall) {
      isFirstCall = false;
      func.apply(context, args);
    } else {
      // 清除之前的定时器
      clearTimeout(timeoutId);
      // 设置新的定时器
      timeoutId = setTimeout(() => {
        func.apply(context, args);
      }, wait);
    }
  };
}

// 显示提示文本
function showMessage(messageText) {
    messageElement.textContent = messageText; // 设置新的消息文本
    messageElement.classList.add('visible');
    setTimeout(() => hideMessage(), 2000);
}
// 隐藏加载中提示
function hideMessage() {
    messageElement.classList.remove('visible');
}

const debouncedShowMessage = debounceImmediate(showMessage, 10000); // 10秒
// 双击图片放大或还原
function toggleImageZoom() {
    // console.log('准备缩放图片')
    if (currentImage.style.transform === 'translate(-50%, -50%)') {
        currentImage.style.transform = 'scale(2) translate(-25%, -25%)';
        isNotZooming = false
        // onsole.log('isNotZooming:',isNotZooming)
        // 隐藏选项栏
        document.getElementById('optionBar').classList.add('hidden');
    } else {
        currentImage.style.transform = 'translate(-50%, -50%)';
        isNotZooming = true
    }
}

// 模拟 click 事件
function simulateClick(e) {
    const target = e.target;
    if (target.tagName.toLowerCase() === 'button' || target.tagName.toLowerCase() === 'div') {
        target.click();
    }
}

// 区分删除和轮播事件，隐藏时无动作
function handleClick(event) {
    // console.log('点击了', event.target.id)
    if (optionBar.classList.contains('hidden')) return;
    event.stopPropagation(); // 阻止事件冒泡
    const id = event.target.id;
    if (id === 'deleteButton') {
        handleDelete('image');
    } else if (id === 'carouselButton') {
        handleCarousel();
    } else if (id == 'filename') {
        handleBack()
    } else if (id == 'subOptionButton') {
        handleSubOption()
    }
}

function handleBack() {
    if (document.getElementById('delFolder')) {
        // 清空容器
        while (topBarRight.firstChild) {
            topBarRight.removeChild(topBarRight.firstChild);
        }
        // 添加回原有html文档
        topBarRight.innerHTML = `
            <button class="top-bar-button delete" id="deleteButton">🗑</button>
            <button class="top-bar-button sub-option" id="subOptionButton">⋮</button>
            <button class="top-bar-button carouse" id="carouselButton">▶</button>
        `;
        // 重新添加监听
        document.getElementById('deleteButton').addEventListener('click', handleClick);
        document.getElementById('subOptionButton').addEventListener('click', handleClick);
        document.getElementById('carouselButton').addEventListener('click', handleClick);
    } else {
        url = '/' + encodeURIComponent(folderPath) + '?from_viewer=true';
        location.replace(url);
    }
}

function handleSubOption() {
    // 移除监听
    document.getElementById('deleteButton').removeEventListener('click', handleClick);
    document.getElementById('subOptionButton').removeEventListener('click', handleClick);
    document.getElementById('carouselButton').removeEventListener('click', handleClick);
    // 清空容器
    while (topBarRight.firstChild) {
        topBarRight.removeChild(topBarRight.firstChild);
    }
    // 添加新的按钮
    const delFolder = document.createElement('button');
    delFolder.className = 'top-bar-button del-folder';
    delFolder.innerHTML = '<span class="icon">📁</span><span class="icon" id="delFolder">❌</span>'; // 使用 HTML 片段插入图标
    delFolder.onclick = function() {
        event.stopPropagation(); // 阻止事件冒泡
        handleDelete('folder');
    };
    topBarRight.appendChild(delFolder);
    // 减慢
    const slower = document.createElement('button');
    slower.className = 'top-bar-button slower';
    slower.textContent = '⏪';
    slower.onclick = function() {
        event.stopPropagation(); // 阻止事件冒泡
        let speedIndex = CarouselFpsList.indexOf(CarouselFps);
        if (speedIndex === 0) {
            CarouselFps = CarouselFpsList[0]; // 已经是第一个元素，返回头部结果
        } else {
            CarouselFps = CarouselFpsList[speedIndex - 1];
        }
       showMessage(`每秒刷新${CarouselFps}次`)
    };
    topBarRight.appendChild(slower);
    // 加快
    const faster = document.createElement('button');
    faster.className = 'top-bar-button faster';
    faster.textContent = '⏩';
    faster.onclick = function() {
        event.stopPropagation(); // 阻止事件冒泡
        let speedIndex = CarouselFpsList.indexOf(CarouselFps);
        if (speedIndex === CarouselFpsList.length -1) {
            CarouselFps = CarouselFpsList[CarouselFpsList.length -1]; // 已经是最后一个元素，返回尾部结果
        } else {
            CarouselFps = CarouselFpsList[speedIndex + 1];
        }
       showMessage(`每秒刷新${CarouselFps}次`)
    };
    topBarRight.appendChild(faster);
}

function handleDelete(type){
    // 删除图片
    if (type === 'image') {
        image_path = images[currentImageIndex]
        fetch('/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: image_path }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('网络错误 ' + response.statusText);
            }
            return response.json(); // 解析JSON响应
        })
        .then(data => {
            if (data.success) {
                showMessage('删除成功',image_path);
                // 隐藏选项栏
                document.getElementById('optionBar').classList.add('hidden');
                // 如果图片是文件夹下的唯一一张，把文件夹也一并删除
                if (currentImageIndex == images.length -1 && currentImageIndex == 0) {
                    handleDelete('folder')
                } else if (currentImageIndex == images.length -1 ) {
                    // 删除最后一张图片后返回上一张
                    images = images.filter(image => image !== images[currentImageIndex]);
                    rightImageIndex = currentImageIndex;
                    currentImageIndex = leftImageIndex;
                    leftImageIndex = (leftImageIndex - 1 + images.length) % images.length;
                    // console.log('索引更新完成:', leftImageIndex, currentImageIndex, rightImageIndex)
                    // 更新图片引用
                    updateImages();
                    // console.log('新的当前页面，供刷新使用:', currentImageIndex)
                    sessionStorage.setItem('currentImageIndex', currentImageIndex);
                } else {
                    // 从image中删除当前图片
                    images = images.filter(image => image !== images[currentImageIndex]);
                    updateImages();
                }
            } else {
                showMessage('删除失败',image_path);
            }
        })
        .catch(error => {
            showMessage('请求失败:', error);
        });
    } else if (type === 'folder') {
        fetch('/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: folderPath }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('网络错误 ' + response.statusText);
            }
            return response.json(); // 解析JSON响应
        })
        .then(data => {
            if (data.success) {
                showMessage('删除成功',folderPath);
                url = 'image_viewer_recursively?current_path=' + encodeURIComponent(folderPath) + '&carousel_fps=' + CarouselFps;
                location.replace(url)
            } else {
                showMessage('删除失败',folderPath);
            }
        })
        .catch(error => {
            showMessage('请求失败:', error);
        });
    }
}


function handleCarousel(){
    // 停止原有监听，此时动作不一样了
    imageContainer.removeEventListener('touchstart', touchStart);
    // 隐藏选项栏
    document.getElementById('optionBar').classList.add('hidden');
    // 定义轮播图片的方法
    function CarouselImage() {
        // console.log('当前位置:',currentImageIndex ,images[currentImageIndex],'数组总长度:', images.length)
        // 如果右边图片加载完就启动轮播
        if (loadedImages[images[rightImageIndex]]) {
            // 到达最后一张图片，停止轮播，切换到下一个页面
            if (currentImageIndex == images.length -1 ) {
				stopCarousel();
                url = 'image_viewer_recursively?current_path=' + encodeURIComponent(folderPath) + '&carousel_fps=' + CarouselFps + '&Carousing=true';
                location.replace(url)
            }
            leftImageIndex = currentImageIndex;
            currentImageIndex = rightImageIndex;
            rightImageIndex = (rightImageIndex + 1) % images.length;
            // 更新当前图片
            const currentImageElement = document.getElementById('currentImage');
            updateImage(currentImageElement, images[currentImageIndex]);
            // 如果可能，继续加载第十二张图片
            if (rightImageIndex + 11 < images.length){
                // console.log('补充加载:', images[rightImageIndex + 11])
                fetchImageAndWriteCache(images[rightImageIndex + 11])
            }
        }else {
            debouncedShowMessage('loading...');
        }
        // console.log('继续循环')
    }
    function reverseCarouselImage() {
        // console.log('当前位置:',currentImageIndex ,images[currentImageIndex],'数组总长度:', images.length)
        // 如果当前已经是0，结束轮播
        if (currentImageIndex == 0) {
            stopCarousel();
            showMessage('到达第一张图片');
        } else if (loadedImages[images[leftImageIndex]]) {
            // 如果左边图片加载完就启动轮播
            rightImageIndex = currentImageIndex;
            currentImageIndex = leftImageIndex;
            leftImageIndex = (leftImageIndex - 1 + images.length) % images.length;
            // 更新当前图片
            const currentImageElement = document.getElementById('currentImage');
            updateImage(currentImageElement, images[currentImageIndex]);
            fetchImageAndWriteCache(images[leftImageIndex])
            } else {
                debouncedShowMessage('loading...');
            }
        }
    // 启动定时更新图片
    function startCarousel() {
        clearInterval(intervalId);
        if (!reverseCarousel) {
            // showMessage(`正向每秒${CarouselFps}次`)
            intervalId = setInterval(CarouselImage, 1000/CarouselFps); // 更新时间是1000ms/每秒更新次数
        } else {
            // showMessage(`反向每秒${CarouselFps}次`)
            intervalId = setInterval(reverseCarouselImage, 1000/CarouselFps); // 更新时间是1000ms/每秒更新次数
        }
    }
    // 停止自动播放
    function stopCarousel() {
        clearInterval(intervalId);
        // 显示状态栏开始鼠标监听
        imageContainer.removeEventListener('touchstart', stopCarousel);
        imageContainer.removeEventListener('click', stopCarousel);
        document.getElementById('currentImage').removeEventListener('click', () => {
            event.stopPropagation(); // 阻止事件冒泡
            stopCarousel();
        })
        // console.log('触发了停止自动播放，显示状态栏')
        document.getElementById('optionBar').classList.remove('hidden');
        imageContainer.addEventListener('touchstart', touchStart, { passive: true });
    }
    imageContainer.addEventListener('touchstart', stopCarousel);
    imageContainer.addEventListener('click', stopCarousel);
    document.getElementById('currentImage').addEventListener('click', () => {
        event.stopPropagation(); // 阻止事件冒泡
        stopCarousel();
    }, { once: true })
    // 从rightImageIndex开始数12个元素
    dozenImages = images.slice(rightImageIndex + 1, rightImageIndex + 12);
    // 使用for循环获取数组的后12个元素或获取元素直到末尾
    for (let i = 0; i < dozenImages.length; i++) {
        // 连续加载一打图片
        // console.log('初次加载了',dozenImages[i])
        fetchImageAndWriteCache(dozenImages[i])
    }

    startCarousel();
}

function touchStart(e) {
    dragDistance = 0
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    lastX = e.touches[0].clientX;
    dragDistanceLeft = 0;
    dragDistanceRight = 0;
    isDragging = true;
    imageContainer.addEventListener('touchmove', touchMove, { passive: false });
    imageContainer.addEventListener('touchend', touchEnd);
    clearTimeout(doubleTapTimeout); // 清除之前的计时器
    doubleTapTimeout = setTimeout(() => {
        isDoubleTap = false;
    }, 300); // 等待 300ms 后重置 isDoubleTap
}

function touchMove(e) {
    // 移动就隐藏选项栏
    document.getElementById('optionBar').classList.add('hidden');
    if (e.cancelable) {
        e.preventDefault(); // 尝试取消默认动作
    }
    // console.log('startX:',startX,'endX:',endX)
    endX = e.changedTouches[0].clientX;
    endY = e.touches[0].clientY;
    dragDistance = endX - startX;
    dragDistanceY = endY - startY;
    singleDragDistance = endX - lastX;
    lastX = endX;
    // console.log('isNotZooming:',isNotZooming)
    if (isNotZooming) {
        // 计算往左和往右的最大距离
        if (singleDragDistance < 0) {
            // 左滑
            if (dragDistanceLeft<Math.abs(singleDragDistance)) {
                dragDistanceLeft = Math.abs(singleDragDistance);
            }
            // 如果右边图片没有加载完
            if (!loadedImages[images[rightImageIndex]]) {
                // 提示图片正在加载
                showMessage('loading...');
                dragDistance = 0
            }
        } else {
            // 右滑
            if (dragDistanceRight<Math.abs(singleDragDistance)) {
                dragDistanceRight = Math.abs(singleDragDistance);
            }
            // 如果左边图片没有加载完
            if (!loadedImages[images[leftImageIndex]]) {
                // 提示图片正在加载
                showMessage('loading...');
                dragDistance = 0
            }
        }
        const currentImageTransform = dragDistance / window.innerWidth * 100 + 50;
        // 平移所有图片
        // console.log('开始平移所有图片')
        document.getElementById('currentImage').style.left = `${currentImageTransform}%`;
        document.getElementById('leftImage').style.left = `${currentImageTransform - 100}%`;
        document.getElementById('rightImage').style.left = `${currentImageTransform + 100}%`;

    } else {
        const currentImageTransform = dragDistance / window.innerWidth * 100;
        // console.log('currentImageTransform:',currentImageTransform)
        const currentImageTransformY = dragDistanceY / window.innerHeight * 100;
        // console.log('currentImageTransformY:',currentImageTransformY)

        // console.log('开始平移放大状态图片')
        document.getElementById('currentImage').style.transform = `scale(2) translate(${currentImageTransform - 25}% , ${currentImageTransformY - 25}%)`;

        // 左滑到最大值，切换到下一张图片，停止缩放
        if (currentImageTransform - 25 < -62.5) {
            reverseCarousel = 0
            if (currentImageIndex == images.length -1 ) {
                url = 'image_viewer_recursively?current_path=' + encodeURIComponent(folderPath) + '&carousel_fps=' + CarouselFps;
                location.replace(url)
            }
            leftImageIndex = currentImageIndex;
            currentImageIndex = rightImageIndex;
            rightImageIndex = (rightImageIndex + 1) % images.length;
            updateImages();
            isNotZooming = true
        }
        // 右滑到最大值，切换到前一张图片，停止缩放
        if (currentImageTransform - 25 > 12.5) {
            reverseCarousel = 1
            rightImageIndex = currentImageIndex;
            currentImageIndex = leftImageIndex;
            leftImageIndex = (leftImageIndex - 1 + images.length) % images.length;
            updateImages();
            isNotZooming = true
        }
    }
}

function touchEnd(e) {
    e.preventDefault()
    isDragging = false;
    // console.log('拖动距离为',dragDistance)
    imageContainer.removeEventListener('touchmove', touchMove);
    imageContainer.removeEventListener('touchend', touchEnd);

    if (dragDistance == 0) {
        if (!isDoubleTap) {
            isDoubleTap = true;
            doubleTapTimeout = setTimeout(() => {
                isDoubleTap = false; // 如果没有第二次点击，则重置 isDoubleTap
            }, 300); // 等待 300ms 后重置 isDoubleTap
            // console.log('拖动为0，显示状态栏')
            document.getElementById('optionBar').classList.remove('hidden');
            // imageContainer.removeEventListener('touchstart', touchStart);
            // 如果没有拖动，则模拟 click 事件
            simulateClick(e);
        } else {
            toggleImageZoom();
        }
    }
    // 在非缩放情况下才执行切换
    if (isNotZooming) {
        // 如果拖动距离超过阈值，则不切换图片
        console.log('dragDistanceLeft:',dragDistanceLeft,'dragDistanceRight:',dragDistanceRight)
        if (dragDistanceLeft > threshold && dragDistanceRight > threshold) {
            // console.log('不切换，所有图片复位')
            // 加动画
            document.getElementById('currentImage').style.transition = 'transform 0.1s ease-in-out';
            document.getElementById('leftImage').style.transition = 'transform 0.1s ease-in-out';
            document.getElementById('rightImage').style.transition = 'transform 0.1s ease-in-out';
            // 还原位置
            document.getElementById('currentImage').style.left = `50%`;
            document.getElementById('leftImage').style.left = `-50%`;
            document.getElementById('rightImage').style.left = `150%`;
            // 等待动画结束
            setTimeout(() => {
                // 删除动画
                document.getElementById('currentImage').style.transition = '';
                document.getElementById('leftImage').style.transition = '';
                document.getElementById('rightImage').style.transition = '';
            }, 100); // 假设动画时间为0.1秒
        } else{
            if (dragDistance > 0) {
                reverseCarousel = 1
                // console.log('往右移动')
                document.getElementById('leftImage').classList.add('image-enter-from-left');
                document.getElementById('currentImage').classList.add('image-exit-to-right');
                // 等待动画结束后刷新图片
                setTimeout(() => {
                    // console.log('更新索引，全部右移，原索引:', leftImageIndex, currentImageIndex, rightImageIndex)
                    rightImageIndex = currentImageIndex;
                    currentImageIndex = leftImageIndex;
                    leftImageIndex = (leftImageIndex - 1 + images.length) % images.length;
                    // console.log('索引更新完成:', leftImageIndex, currentImageIndex, rightImageIndex)
                    // 更新图片引用
                    updateImages();
                    // console.log('新的当前页面，供刷新使用:', currentImageIndex)
                    sessionStorage.setItem('currentImageIndex', currentImageIndex);
                }, 100); // 假设动画时间为0.1秒
            }

            if (dragDistance < 0) {
                reverseCarousel = 0
                // console.log('往左移动，中间显示右边的图片')
                // 执行动画
                document.getElementById('rightImage').classList.add('image-enter-from-right');
                document.getElementById('currentImage').classList.add('image-exit-to-left');
                // 等待动画结束后刷新图片
                setTimeout(() => {
                    // console.log('更新索引，全部左移，原索引:', leftImageIndex, currentImageIndex, rightImageIndex)
                    if (currentImageIndex == images.length -1 ) {
                        url = 'image_viewer_recursively?current_path=' + encodeURIComponent(folderPath) + '&carousel_fps=' + CarouselFps;
                        location.replace(url)
                    }
                    leftImageIndex = currentImageIndex;
                    currentImageIndex = rightImageIndex;
                    rightImageIndex = (rightImageIndex + 1) % images.length;
                    // 更新图片引用
                    updateImages();
                    // console.log('新的当前页面，供刷新使用:', currentImageIndex)
                    sessionStorage.setItem('currentImageIndex', currentImageIndex);
                }, 100); // 假设动画时间为0.1秒
            }
        }
    }
}



// 异步从网络请求获取图片并写入缓存
async function fetchImageAndWriteCache(src) {
    // 发起网络请求
    try {
        // console.log('请求网络路径：', src)
        const response = await fetch(encodeURIComponent(src));
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.status}`);
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        // 写入缓存
        loadedImages[src] = { src: url, element: null };
        // 缓存已满时删除最早添加的图片
        if (Object.keys(loadedImages).length > MAX_CACHE_SIZE) {
            console.log('缓存已满,删除最早添加的图片');
            const firstKey = Object.keys(loadedImages)[0];
            delete loadedImages[firstKey];
        }
    } catch (error) {
        console.error('Error fetching image:', error);
    }
    // 返回一个空的 Promise 表示完成
    return Promise.resolve();
}

// 异步更新单个图片
async function updateImage(imageElement, src) {
    // console.log(src)
    if (loadedImages[src]) {
        imageElement.src = loadedImages[src].src;
    } else {
        // console.log('从网络请求获取图片：', src);
        // 从网络请求获取图片并写入缓存
        await fetchImageAndWriteCache(src);
        // console.log('缓存增加新图片：', src);
        // 从缓存中读取数据并显示到页面上
        imageElement.src = loadedImages[src].src;
    }
    // 监听图片加载完成事件
    return new Promise((resolve) => {
        imageElement.onload = () => {
            resolve(); // 解析 Promise 表示图片加载完成
        };
    });
}

// 更新图片引用
async function updateImages() {
    // 获取当前图片元素
    // console.log('更新图片引用:', leftImageIndex, currentImageIndex, rightImageIndex);
    const leftImageElement = document.getElementById('leftImage');
    const currentImageElement = document.getElementById('currentImage');
    const rightImageElement = document.getElementById('rightImage');

    // 异步更新图片
    // console.log('开始异步更新:', images[leftImageIndex], images[currentImageIndex], images[rightImageIndex]);
    updateImage(leftImageElement, images[leftImageIndex]);

    updateImage(rightImageElement, images[rightImageIndex]);

    // 等待当前图片处理完成
    // console.log('等待当前图片:', images[currentImageIndex]);
    await updateImage(currentImageElement, images[currentImageIndex]);
    // 隐藏提示
    messageElement.classList.remove('visible');
    // 显示图片，应用样式
    updateOptionText(images[currentImageIndex]);
    currentImage.style.transform = 'translate(-50%, -50%)';
    currentImageElement.style.left = `50%`;
    currentImageElement.classList.add('visible');
    leftImageElement.style.left = `-50%`;
    leftImageElement.classList.add('visible');
    rightImageElement.style.left = `150%`;
    rightImageElement.classList.add('visible');
    // 清除滑动标志
    document.getElementById('rightImage').classList.remove('image-enter-from-right');
    document.getElementById('currentImage').classList.remove('image-exit-to-left');
    document.getElementById('leftImage').classList.remove('image-enter-from-left');
    document.getElementById('currentImage').classList.remove('image-exit-to-right');
    // console.log('更新完成，开始监听触摸事件');
    imageContainer.addEventListener('touchstart', touchStart, { passive: true });
}
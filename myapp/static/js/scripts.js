const filePath = items[0]['path'];

document.addEventListener("DOMContentLoaded", function() {
    // 设置占位符高度
    setPlaceholderHeight();
    // 检查屏幕宽度，确定要显示的sub-container数量
    adjustImages();
    // 手动触发检查初始图片状态
    checkInitialVisibility();
    lazyLoad(); // 开始懒加载
    // 监视左滑操作
    console.log('添加事件监听,当前路径是:', filePath)
    // 事件监听器
    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchmove', handleTouchMove);
    document.addEventListener('touchend', handleTouchEnd);

    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
});

window.addEventListener('resize', () => {
    setPlaceholderHeight();
    adjustImages();
})


function setPlaceholderHeight() {
    const placeholders = document.querySelectorAll('.placeholder');
    placeholders.forEach(placeholder => {
        const aspectRatio = parseFloat(placeholder.getAttribute('data-aspect-ratio'));
        if (aspectRatio && !isNaN(aspectRatio)) {
            placeholder.style.paddingBottom = `${(1 / aspectRatio) * 100}%`;
        }
    });
}

function lazyLoad() {
    const lazyImages = document.querySelectorAll('img.lazy');

    if ('IntersectionObserver' in window) {
        const options = {
            root: null,
            rootMargin: '0px 0px 500px 0px',
            threshold: 0.01
        };

        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.dataset.src;
                    if (src) {
                        img.src = src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);

                        img.onload = () => {
                            img.classList.add('loaded'); // 添加加载完成的类
                            const placeholder = img.previousElementSibling;
                            if (placeholder) {
                                placeholder.style.display = 'none'; // 隐藏占位符
                                img.nextElementSibling.classList.remove('hidden'); // 显示文字
                                placeholder.style.paddingBottom = '0'; // 为了防止占位符影响布局
                            }
                        };
                    }
                }
            });
        }, options);

        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        lazyImages.forEach(img => {
            const src = img.dataset.src;
            if (src) {
                img.src = src;
                img.classList.remove('lazy');
                img.onload = () => {
                    img.classList.add('loaded'); // 添加加载完成的类
                    const placeholder = img.previousElementSibling;
                    if (placeholder) {
                        placeholder.style.display = 'none'; // 隐藏占位符
                        img.nextElementSibling.classList.remove('hidden'); // 显示文字
                        placeholder.style.paddingBottom = '0'; // 为了防止占位符影响布局
                    }
                };
            }
        });
    }
}

function navigateTo(url) {
    location.replace(url);
}

// 检查图片是否在初始视口内，并手动触发加载
function checkInitialVisibility() {
    const lazyImages = document.querySelectorAll('img.lazy');
    lazyImages.forEach(img => {
        if (isElementInViewport(img)) {
            const src = img.dataset.src;
            if (src) {
                img.src = src;
                img.classList.remove('lazy');
                img.onload = () => {
                    img.classList.add('loaded'); // 添加加载完成的类
                    const placeholder = img.previousElementSibling;
                    if (placeholder) {
                        placeholder.style.display = 'none'; // 隐藏占位符
                        img.nextElementSibling.classList.remove('hidden'); // 显示文字
                        placeholder.style.paddingBottom = '0'; // 为了防止占位符影响布局
                    }
                };
            }
        };
    })
};

// 判断元素是否在视口内
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// 分配图片到两个或三个sub-container
function adjustImages() {
    const container = document.querySelector('.container');
    const subContainers = container.querySelectorAll('.sub-container');
    const items1 = Array.from(subContainers[0].querySelectorAll('.item'));
    const items2 = Array.from(subContainers[1].querySelectorAll('.item'));
    const items3 = Array.from(subContainers[2].querySelectorAll('.item'));
    const items = [];
    for (let i = 0; i < items1.length; i++) {
        if (items1[i]) items.push(items1[i]);
        if (items2[i]) items.push(items2[i]);
        if (items3[i]) items.push(items3[i]);
    }
    if (window.innerWidth < window.innerHeight) {
        // 分配图片到两个 sub-container
        for (let i = 0; i < items.length; i++) {
            const containerIndex = i % 2; // 使用取模运算确定容器编号
            subContainers[containerIndex].appendChild(items[i]); // 将图片添加到对应的容器
        }
    }
    else{
        // 分配图片到三个 sub-container
        for (let i = 0; i < items.length; i++) {
            const containerIndex = i % 3; // 使用取模运算确定容器编号
            subContainers[containerIndex].appendChild(items[i]); // 将图片添加到对应的容器
        }
    }
};


let startX, endX, isDragging = false, screenWidth;

// 手势开始
function handleTouchStart(event) {
    startX = event.touches[0].clientX;
    screenWidth = window.innerWidth;
    isDragging = true;
}

// 手势移动
function handleTouchMove(event) {
    if (isDragging) {
        endX = event.touches[0].clientX;
    }
}

// 手势结束
function handleTouchEnd(event) {
    if (isDragging) {
        isDragging = false;
        triggerSwipeAction();
    }
}

// 鼠标按下
function handleMouseDown(event) {
    startX = event.clientX;
    screenWidth = window.innerWidth;
    isDragging = true;
}

// 鼠标移动
function handleMouseMove(event) {
    if (isDragging) {
        endX = event.clientX;
    }
}

// 鼠标松开
function handleMouseUp(event) {
    if (isDragging) {
        isDragging = false;
        triggerSwipeAction();
    }
}

// 触发滑动操作
function triggerSwipeAction() {
    const distanceX = endX - startX;
    if (distanceX > screenWidth/3) {
        // 用户向右滑动，并且滑动距离超过屏幕宽度的三分之二
        console.log("Swipe right");
        backPage();
    }
}

function backPage() {
    // 获取最后一个斜杠的位置
    const lastSlashIndex = filePath.lastIndexOf('/');
    let folderPath = '';
    // 如果找不到斜杠，则返回空字符串（意味着文件位于根目录）
    if (lastSlashIndex === -1) {
        folderPath = '';
        return
    } else {
        // 获取倒数第二个斜杠的位置
        const secondLastSlashIndex = filePath.substring(0, lastSlashIndex).lastIndexOf('/');
        // 如果找到了倒数第二个斜杠
        if (secondLastSlashIndex !== -1) {
            // 返回倒数第二个斜杠之前的字符串（即目录路径）
            folderPath = filePath.substring(0, secondLastSlashIndex);
        } else {
            // 如果没有找到倒数第二个斜杠，说明只有一个斜杠
            folderPath = '';
        }
    }
    url = '/' + encodeURIComponent(folderPath);
    window.location.href = url;
}


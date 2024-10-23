document.addEventListener('DOMContentLoaded', () => {
    // 为返回按钮添加事件监听器
    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.addEventListener('click', (event) => {
            event.preventDefault(); // 阻止默认链接行为
            history.back();         // 调用浏览器的后退功能
        });
    }

    // 为所有删除按钮添加事件监听器
    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', event => {
            const listItem = event.target.closest('li');
            if (listItem) {
                const commentId = listItem.dataset.commentId;

                fetch(`/delete-comment/${commentId}`, {
                    method: 'DELETE',
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        listItem.remove();
                    } else {
                        console.error('删除评论失败');
                    }
                })
                .catch(error => {
                    console.error('请求失败:', error);
                });
            }
        });
    });
});
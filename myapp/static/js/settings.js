document.querySelectorAll('.delete-button').forEach(button => {
button.addEventListener('click', event => {
    const listItem = event.target.closest('li');
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
});
});
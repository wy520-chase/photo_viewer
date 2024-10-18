from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from myapp import db, Comment
from datetime import datetime

settings_blueprint = Blueprint('settings', __name__)

@settings_blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # 获取当前时间
        current_time = datetime.now()
        text = request.form.get('comment')
        if text:
            text = f'[{current_time.strftime("%Y-%m-%d %H:%M:%S")}] - {text}'
            new_comment = Comment(text=text)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('settings.settings'))

    comments = Comment.query.all()
    return render_template('settings.html', comments=comments)

@settings_blueprint.route('/delete-comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    # 在这里处理评论删除逻辑，例如从数据库中删除评论
    # 成功删除后可以返回一个成功状态码
    try:
        Comment.delete(comment_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
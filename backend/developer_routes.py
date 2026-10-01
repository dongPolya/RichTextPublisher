from flask import Blueprint, jsonify, request, current_app, session
from flask_login import login_required, current_user
from .models import db, User, Post, Question, Community, user_community
from datetime import datetime
import json

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


dev_bp = Blueprint('developer', __name__, url_prefix='/api')


# ⭐ 新增：开发者权限检查装饰器
def developer_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查是否登录
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        # 检查是否是开发者邮箱
        if current_user.email != '2398554859@qq.com':
            return jsonify({'error': 'Developer access required'}), 403

        return f(*args, **kwargs)

    return decorated_function


# Developer authentication
@dev_bp.route('/developer/verify', methods=['POST'])
def developer_verify():
    data = request.get_json()
    password = data.get('password')

    # Developer password verification
    if password == 'abXY12':
        session['developer_authenticated'] = True
        return jsonify({'message': 'Developer authentication successful'}), 200
    else:
        return jsonify({'error': 'Invalid developer password'}), 401


# Search functionality
@dev_bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'post')  # post, log, quiz
    search_mode = request.args.get('mode', 'title')  # title, id

    try:
        results = []

        if search_type == 'post' or search_type == 'all':
            if search_mode == 'id' and query.isdigit():
                posts = Post.query.filter(Post.id == int(query)).all()
            else:
                posts = Post.query.filter(
                    db.or_(
                        Post.title.contains(query),
                        Post.content.contains(query)
                    )
                ).all()
            for post in posts:
                post_data = post.to_dict()
                post_data['item_type'] = 'post'  # ⭐ 修复：使用 item_type 避免冲突
                results.append(post_data)


        if search_type == 'quiz' or search_type == 'all':
            if search_mode == 'id' and query.isdigit():
                questions = Question.query.filter(Question.id == int(query)).all()
            else:
                questions = Question.query.filter(
                    Question.question.contains(query)
                ).all()
            for q in questions:
                q_data = q.to_dict()
                q_data['item_type'] = 'quiz'  # ⭐ 修复：使用 item_type 避免冲突
                results.append(q_data)

        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500


# ⭐ 新增：获取社区详情（包含成员列表）
@dev_bp.route('/communities/<int:community_id>', methods=['GET'])
@login_required
def get_community_detail(community_id):
    community = Community.query.get_or_404(community_id)

    # 获取成员列表
    members = [member.to_dict() for member in community.members]

    community_data = community.to_dict()
    community_data['members'] = members

    return jsonify(community_data)


# Question delete route
@dev_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@developer_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)

    try:
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting question: {str(e)}")
        return jsonify({'error': 'Failed to delete question'}), 500


# Community update route
@dev_bp.route('/communities/<int:community_id>', methods=['PUT'])
@developer_required
def update_community(community_id):
    community = Community.query.get_or_404(community_id)

    # 检查是否是文件上传
    if request.content_type and 'multipart/form-data' in request.content_type:
        # 处理表单数据和文件
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')

        if name:
            community.name = name
        if description:
            community.description = description
        if category:
            community.category = category

        # 处理图像上传
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                from werkzeug.utils import secure_filename
                import os

                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                if not os.path.isabs(upload_folder):
                    upload_folder = os.path.join(current_app.root_path, upload_folder)

                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                filename = secure_filename(file.filename)
                # 添加时间戳避免文件名冲突
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    filename = f"{filename}_{timestamp}"

                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)

                # 生成访问 URL
                base_url = current_app.config['BASE_URL'].rstrip('/')
                community.avatar = f'{base_url}/uploads/{filename}'
    else:
        # 处理 JSON 数据
        data = request.get_json()

        if 'name' in data:
            community.name = data['name']
        if 'description' in data:
            community.description = data['description']
        if 'category' in data:
            community.category = data['category']
        if 'avatar' in data:
            community.avatar = data['avatar']

    try:
        db.session.commit()
        return jsonify(community.to_dict())
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating community: {str(e)}")
        return jsonify({'error': 'Failed to update community'}), 500


# Community delete route
@dev_bp.route('/communities/<int:community_id>', methods=['DELETE'])
@developer_required
def delete_community(community_id):
    community = Community.query.get_or_404(community_id)

    try:
        # Remove all associations first
        db.session.execute(
            user_community.delete().where(user_community.c.community_id == community_id)
        )
        db.session.delete(community)
        db.session.commit()
        return jsonify({'message': 'Community deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting community: {str(e)}")
        return jsonify({'error': 'Failed to delete community'}), 500


# Remove member from community
@dev_bp.route('/communities/<int:community_id>/members/<int:user_id>', methods=['DELETE'])
@developer_required
def remove_member_from_community(community_id, user_id):
    community = Community.query.get_or_404(community_id)
    user = User.query.get_or_404(user_id)

    if user not in community.members:
        return jsonify({'error': 'User is not a member of this community'}), 404

    try:
        community.members.remove(user)
        community.member_count = max(0, community.member_count - 1)
        db.session.commit()
        return jsonify({'message': 'Member removed successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing member: {str(e)}")
        return jsonify({'error': 'Failed to remove member'}), 500


# Get all users (for developer page)
@dev_bp.route('/users/all', methods=['GET'])
@developer_required
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


# Delete user account (developer function)
@dev_bp.route('/developer/users/<int:user_id>', methods=['DELETE'])
@developer_required
def developer_delete_user(user_id):
    user = User.query.get_or_404(user_id)

    try:
        # Delete user-related data
        Post.query.filter_by(user_id=user_id).delete()
        from .models import Comment
        Comment.query.filter_by(user_id=user_id).delete()
        Log.query.filter_by(user_id=user_id).delete()

        # Remove from communities
        db.session.execute(user_community.delete().where(user_community.c.user_id == user_id))

        # Delete user
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User account deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Failed to delete user account'}), 500


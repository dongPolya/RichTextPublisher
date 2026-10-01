from flask import Blueprint, jsonify, request, current_app, session, render_template_string

from flask_cors import cross_origin
from .models import db, User, Post, Comment, Community, Question,Cover
from datetime import datetime, timedelta
import json, os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os, random, re, logging
from functools import wraps
# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MUSIC_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def allowed_music_file(filename):
    """检查是否为允许的音乐文件格式"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_MUSIC_EXTENSIONS

bp = Blueprint('api', __name__, url_prefix='/api')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 邮件模板
VERIFICATION_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }
        .code { font-size: 32px; font-weight: bold; text-align: center; color: #667eea; margin: 20px 0; }
        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Travel Community</h1>
            <p>Email Verification</p>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Thank you for registering with Travel Community. Please use the following verification code to complete your registration:</p>
            <div class="code">{{ verification_code }}</div>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this verification, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 Travel Community. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }
        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Travel Community!</h1>
        </div>
        <div class="content">
            <p>Hello {{ username }},</p>
            <p>Welcome to Travel Community! We're excited to have you join our community of travel enthusiasts.</p>
            <p>Start exploring:</p>
            <ul>
                <li>Share your travel experiences</li>
                <li>Join communities based on your interests</li>
                <li>Connect with fellow travelers</li>
                <li>Plan your next adventure</li>
            </ul>
            <p>Happy traveling!</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 Travel Community. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
# Session键名
VERIFICATION_SESSION_KEY = 'email_verification'
# 装饰器
def login_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def register_step_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return jsonify({'error': 'Already logged in'}), 400
        return f(*args, **kwargs)
    return decorated_function

def get_verification_session_key(email):
    return f"{VERIFICATION_SESSION_KEY}:{email}"


def create_verification_code(email):
    """生成并存储验证码到session"""
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # 存储到session
    session[get_verification_session_key(email)] = {
        'code': verification_code,
        'expires_at': expires_at.isoformat(),
        'attempts': 0  # 验证尝试次数
    }
    session.permanent = True  # 使session持久化

    return verification_code


def verify_code_session(email, code):
    """验证session中的验证码"""
    session_key = get_verification_session_key(email)
    verification_data = session.get(session_key)

    if not verification_data:
        return False, "Verification code not found or expired"

    # 检查是否过期
    expires_at = datetime.fromisoformat(verification_data['expires_at'])
    if datetime.utcnow() > expires_at:
        # 清理过期session
        session.pop(session_key, None)
        return False, "Verification code expired"

    # 检查尝试次数（防止暴力破解）
    if verification_data.get('attempts', 0) >= 5:
        session.pop(session_key, None)
        return False, "Too many failed attempts"

    # 验证代码
    if verification_data['code'] != code:
        # 增加尝试次数
        verification_data['attempts'] = verification_data.get('attempts', 0) + 1
        session[session_key] = verification_data
        return False, "Invalid verification code"

    # 验证成功，清理session
    session.pop(session_key, None)
    return True, "Verification successful"



def cleanup_expired_verifications():
    """清理过期的验证session（可选）"""
    current_time = datetime.utcnow()
    keys_to_remove = []

    for key, value in session.items():
        if key.startswith(VERIFICATION_SESSION_KEY):
            expires_at = datetime.fromisoformat(value.get('expires_at', '1970-01-01'))
            if current_time > expires_at:
                keys_to_remove.append(key)

    for key in keys_to_remove:
        session.pop(key, None)

# 邮件发送函数
def send_verification_email(email, verification_code):
    try:
        from flask_mail import Message
        msg = Message(
            subject='Travel Community - Email Verification',
            recipients=[email],
            html=render_template_string(VERIFICATION_EMAIL_TEMPLATE, verification_code=verification_code)
        )
        from flask import current_app
        mail = current_app.extensions.get('mail')
        if mail:
            mail.send(msg)
            current_app.logger.info(f"Verification email sent to {email}")
            return True
        else:
            current_app.logger.error("Mail extension not found")
            return False
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False

def send_welcome_email(email, username):
    try:
        from flask_mail import Message
        msg = Message(
            subject='Welcome to Travel Community!',
            recipients=[email],
            html=render_template_string(WELCOME_EMAIL_TEMPLATE, username=username)
        )
        from flask import current_app
        mail = current_app.extensions.get('mail')
        if mail:
            mail.send(msg)
            current_app.logger.info(f"Welcome email sent to {email}")
            return True
        else:
            current_app.logger.error("Mail extension not found")
            return False
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False

# 密码验证函数
def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one number or special character"
    return True, "Password is valid"
# 修改认证路由
@bp.route('/auth/register/send-code', methods=['POST'])
@register_step_required
def send_verification_code():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # 验证邮箱格式
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'error': 'Invalid email format'}), 400

    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400

    try:
        # 生成验证码并存储到session
        verification_code = create_verification_code(email)

        # 发送验证邮件
        if current_app.config.get('TESTING') or current_app.config.get('MAIL_SUPPRESS_SEND'):
            # 测试环境下直接返回验证码
            return jsonify({
                'message': 'Verification code sent (development mode)',
                'code': verification_code
            }), 200
        else:
            # 生产环境发送邮件
            if send_verification_email(email, verification_code):
                return jsonify({'message': 'Verification code sent to your email'}), 200
            else:
                return jsonify({'error': 'Failed to send verification email'}), 500

    except Exception as e:
        current_app.logger.error(f"Error sending verification code: {str(e)}")
        return jsonify({'error': 'Failed to send verification code'}), 500
@bp.route('/test-email', methods=['GET'])
def test_email():
    """测试邮件发送功能"""
    config_info = {
        'MAIL_SERVER': current_app.config.get('MAIL_SERVER'),
        'MAIL_PORT': current_app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': current_app.config.get('MAIL_USE_TLS'),
        'MAIL_USE_SSL': current_app.config.get('MAIL_USE_SSL'),
        'MAIL_USERNAME': current_app.config.get('MAIL_USERNAME'),
        'MAIL_PASSWORD': '***' if current_app.config.get('MAIL_PASSWORD') else None,
    }
    try:
        from flask_mail import Message
        msg = Message(
            subject='Test Email from Travel Community',
            recipients=['Cmbself@163.com'],  # 替换为你的测试邮箱
            body='This is a test email from your Flask application.'
        )
        mail = current_app.extensions.get('mail')
        mail.send(msg)
        return jsonify({'message': 'Test email sent successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Test email failed: {str(e)}")
        return jsonify({'error': f'Failed to send test email: {str(e)}'}), 500

@bp.route('/auth/register/verify-code', methods=['POST'])
@register_step_required
def verify_registration_code():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return jsonify({'error': 'Email and code are required'}), 400

    is_valid, message = verify_code_session(email, code)

    if is_valid:
        # 验证成功，在session中标记该邮箱已验证
        session[f'email_verified:{email}'] = True
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 400


@bp.route('/auth/register', methods=['POST'])
@register_step_required
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not all([email, username, password]):
        return jsonify({'error': 'All fields are required'}), 400

    # 检查是否已经通过邮箱验证
    if not session.get(f'email_verified:{email}'):
        return jsonify({'error': 'Email verification required'}), 400

    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # 验证密码强度
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({'error': message}), 400

    try:
        # 创建用户
        user = User(
            username=username,
            email=email,
            avatar='https://randomuser.me/api/portraits/lego/1.jpg',
            email_verified=True,
            last_login=datetime.utcnow()
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # 发送欢迎邮件
        send_welcome_email(email, username)

        # 清理验证session
        session.pop(f'email_verified:{email}', None)

        # 自动登录
        login_user(user, remember=True)

        return jsonify(user.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during registration: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@bp.route('/auth/login', methods=['POST'])
@register_step_required
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', True)

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401

    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()

    login_user(user, remember=remember)
    return jsonify(user.to_dict())


@bp.route('/auth/logout', methods=['POST'])
@login_required_api
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})


@bp.route('/auth/me', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify(current_user.to_dict())
    return jsonify({'user': None})


@bp.route('/auth/delete-account', methods=['DELETE'])
@login_required_api
def delete_account():
    user_id = current_user.id
    username = current_user.username
    email = current_user.email

    try:
        # 删除用户相关数据
        Post.query.filter_by(user_id=user_id).delete()
        Comment.query.filter_by(user_id=user_id).delete()

        # 从社区中移除用户
        from .models import user_community
        db.session.execute(user_community.delete().where(user_community.c.user_id == user_id))

        # 删除用户
        User.query.filter_by(id=user_id).delete()

        db.session.commit()
        logout_user()

        current_app.logger.info(f"User account deleted: {username} ({email})")
        return jsonify({'message': 'Account deleted successfully'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting account: {str(e)}")
        return jsonify({'error': 'Failed to delete account'}), 500


# User routes
@bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required_api
def update_user(user_id):
    # 验证权限 - 只能修改自己的信息
    if current_user.id != user_id:
        return jsonify({'error': 'Permission denied'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # 更新允许的字段
    if 'username' in data:
        # 检查用户名是否已被其他用户使用
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']

    if 'title' in data:
        user.title = data['title']

    if 'bio' in data:
        user.bio = data['bio']

    if 'avatar' in data:
        user.avatar = data['avatar']

    try:
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user: {str(e)}")
        return jsonify({'error': 'Failed to update user information'}), 500


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        avatar=data.get('avatar', 'https://randomuser.me/api/portraits/lego/1.jpg')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@bp.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    try:
        posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
        return jsonify([post.to_dict() for post in posts])
    except Exception as e:
        print(f"Error fetching user posts: {e}")
        return jsonify({'error': 'Failed to fetch user posts'}), 500


# 获取用户加入的社区
@bp.route('/users/<int:user_id>/communities', methods=['GET'])
def get_user_communities(user_id):
    try:
        user = User.query.get_or_404(user_id)
        communities = user.communities if hasattr(user, 'communities') else []
        return jsonify([community.to_dict() for community in communities])
    except Exception as e:
        print(f"Error fetching user communities: {e}")
        return jsonify({'error': 'Failed to fetch user communities'}), 500
# Post routes
@bp.route('/posts', methods=['GET'])
def get_posts():
    sub = request.args.get('sub')
    mode = request.args.get('mode')
    if sub and mode:
        posts = Post.query.filter(
            db.or_(Post.sub == sub, Post.mode == mode)
        ).order_by(Post.created_at.desc()).all()
    elif sub:
        posts = Post.query.filter_by(sub=sub).order_by(Post.created_at.desc()).all()
    elif mode:
        posts = Post.query.filter_by(mode=mode).order_by(Post.created_at.desc()).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()

    return jsonify([post.to_dict() for post in posts])


@bp.route('/posts/<int:post_id>', methods=['GET'])

def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())


@bp.route('/posts', methods=['POST'])

def create_post():
    try:
        logger.debug(f"Request content type: {request.content_type}")
        logger.debug(f"Request headers: {dict(request.headers)}")

        # 检查是否是文件上传
        if request.content_type and 'multipart/form-data' in request.content_type:
            logger.debug("Processing multipart/form-data request")

            # 处理表单数据
            title = request.form.get('title')
            content = request.form.get('content')
            sub = request.form.get('sub')
            user_id = request.form.get('user_id')
            mode = request.form.get('mode','普通')

            # 检查必需字段
            if not title or not content or not user_id:
                logger.error("Missing required fields in form data")
                return jsonify({'error': 'Missing required fields: title, content, or user_id'}), 400

            logger.debug(f"Form data - title: {title}, content: {content}, sub: {sub}, user_id: {user_id}")

            image_url = None
            # 检查是否有文件部分
            if 'image' in request.files:
                file = request.files['image']
                logger.debug(f"File received: {file.filename if file else 'None'}")

                if file and file.filename != '' and allowed_file(file.filename):
                    # 确保上传目录存在
                    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)

                    # 安全地保存文件
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        logger.debug(f"File successfully saved: {file_path}, size: {file_size} bytes")
                    else:
                        logger.error(f"File save failed: {file_path}")
                        return jsonify({'error': 'File save failed'}), 500

                    # 生成访问 URL
                    base_url = current_app.config['BASE_URL']  # 获取当前请求的基础 URL
                    image_url = f'{base_url}uploads/{filename}'
                    logger.debug(f"File saved to: {file_path}, URL: {image_url}")
                else:
                    logger.debug("No valid file provided or file type not allowed")

            # 创建帖子
            post = Post(
                title=title,
                content=content,
                sub=sub,
                mode=mode,
                image=image_url,
                user_id=int(user_id)
            )
            db.session.add(post)
            db.session.commit()
            logger.debug("Post created successfully with file upload")
            return jsonify(post.to_dict()), 201

        else:
            # 处理 JSON 数据（原有逻辑）
            logger.debug("Processing JSON request")
            data = request.get_json()

            # 检查必需字段
            if not data or 'title' not in data or 'content' not in data or 'user_id' not in data:
                logger.error("Missing required fields in JSON data")
                return jsonify({'error': 'Missing required fields: title, content, or user_id'}), 400

            logger.debug(f"JSON data: {data}")

            post = Post(
                title=data['title'],
                content=data['content'],
                sub=data.get('sub'),
                mode=data.get('mode', '普通'),
                image=data.get('image'),
                user_id=data['user_id'],
                community_id=data.get('community_id')
            )
            db.session.add(post)
            db.session.commit()
            logger.debug("Post created successfully from JSON")
            return jsonify(post.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating post: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to create post', 'details': str(e)}), 500


@bp.route('/posts/<int:post_id>', methods=['PUT'])
@login_required_api
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    # 验证用户权限 - 只有作者可以编辑自己的文章
    if post.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.get_json()

    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']
    if 'image' in data:
        post.image = data['image']
    if 'likes' in data:
        post.likes = data['likes']
    if 'mode' in data:
        post.mode = data['mode']

    db.session.commit()
    return jsonify(post.to_dict())


@bp.route('/posts/<int:post_id>', methods=['DELETE'])

def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'})
@bp.route('/posts/<int:post_id>/like', methods=['POST'])
@login_required_api
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes = (post.likes or 0) + 1
    db.session.commit()
    return jsonify({'message': 'Liked', 'likes': post.likes})


# Comment routes
@bp.route('/posts/<int:post_id>/comments', methods=['GET'])

def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    return jsonify([comment.to_dict() for comment in comments])


@bp.route('/posts/<int:post_id>/comments', methods=['POST'])

def create_comment(post_id):
    data = request.get_json()
    comment = Comment(
        content=data['content'],
        user_id=data['user_id'],
        post_id=post_id
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201


@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required_api
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment deleted successfully'})



# Community routes
@bp.route('/communities', methods=['GET'])
def get_communities():
    communities = Community.query.all()

    # 改动4: 为每个社区动态计算帖子数
    result = []
    for community in communities:
        comm_dict = community.to_dict()
        comm_dict['post_count'] = Post.query.filter_by(community_id=community.id).count()
        result.append(comm_dict)

    return jsonify(result)


@bp.route('/communities/<int:community_id>', methods=['GET'])


def get_community(community_id):
    community = Community.query.get_or_404(community_id)

    # 改动3: 动态计算帖子数量
    post_count = Post.query.filter_by(community_id=community_id).count()

    result = community.to_dict()
    result['post_count'] = post_count  # 更新为实际帖子数

    return jsonify(result)


@bp.route('/communities', methods=['POST'])

def create_community():
    data = request.get_json()
    community = Community(
        name=data['name'],
        description=data.get('description'),
        avatar=data.get('avatar'),
        category=data.get('category'),
        member_count=data.get('member_count', 0),
        post_count=data.get('post_count', 0),
        activity_score=data.get('activity_score', 0)
    )
    db.session.add(community)
    db.session.commit()
    return jsonify(community.to_dict()), 201


@bp.route('/communities/<int:community_id>/join', methods=['POST'])
@login_required_api
def join_community(community_id):
    community = Community.query.get_or_404(community_id)
    user = current_user

    if user not in community.members:
        community.members.append(user)
        community.member_count += 1
        db.session.commit()

    return jsonify(community.to_dict())


# Question routes
@bp.route('/questions', methods=['GET'])

def get_questions():
    questions = Question.query.all()
    return jsonify([question.to_dict() for question in questions])


@bp.route('/questions/random', methods=['GET'])

def get_random_question():
    total_questions = Question.query.count()
    print(f"数据库中的题目总数: {total_questions}")
    question = Question.query.order_by(db.func.random()).first()
    if not question:
        return jsonify({'error': 'No questions available'}), 404
    print(f"返回的题目ID: {question.id}")
    return jsonify(question.to_dict())


@bp.route('/questions', methods=['POST'])

def create_question():
    data = request.get_json()
    question = Question(
        question=data['question'],
        options=json.dumps(data['options']),
        correct_answer=data['correct_answer'],
        type=data.get('type', 'single'),
        sub=data.get('sub', '人文自然'),
        likes=data.get('likes', 0)
    )
    db.session.add(question)
    db.session.commit()
    return jsonify(question.to_dict()), 201


@bp.route('/questions/<int:question_id>/check', methods=['POST'])

def check_answer(question_id):
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    user_answer = data.get('answer')

    is_correct = user_answer == question.correct_answer
    return jsonify({
        'correct': is_correct,
        'correct_answer': question.correct_answer
    })


@bp.route('/communities/<int:community_id>/posts', methods=['GET'])
def get_community_posts(community_id):
    try:
        from sqlalchemy import case

        posts = Post.query.filter_by(community_id=community_id) \
            .order_by(
            case(
                (Post.mode == '置顶', 0),
                else_=1
            ),
            Post.created_at.desc()
        ).all()
        return jsonify([post.to_dict() for post in posts])
    except Exception as e:
        print(f"Error fetching community posts: {e}")
        return jsonify({'error': 'Failed to fetch community posts'}), 500


# 获取特定帖子详情
@bp.route('/posts/<int:post_id>/detail', methods=['GET'])
def get_post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()

    result = post.to_dict()
    result['comments'] = [comment.to_dict() for comment in comments]

    return jsonify(result)




# 添加评论
@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data = request.get_json()
    comment = Comment(
        content=data['content'],
        user_id=data['user_id'],
        post_id=post_id
    )
    db.session.add(comment)
    db.session.commit()

    # 更新帖子的评论计数
    post = Post.query.get(post_id)
    if post:
        # 这里假设Post模型有一个comments_count字段，如果没有需要添加
        # 或者可以通过关系动态计算
        pass

    return jsonify(comment.to_dict()), 201


# 获取特定主题的问题
@bp.route('/questions/sub/<string:sub>', methods=['GET'])
def get_questions_by_sub(sub):
    questions = Question.query.filter_by(sub=sub).all()
    return jsonify([question.to_dict() for question in questions])



@bp.route('/covers', methods=['GET'])
def get_covers():
    """获取所有主页样式"""
    try:
        covers = Cover.query.order_by(Cover.created_at.desc()).all()
        return jsonify([cover.to_dict() for cover in covers])
    except Exception as e:
        logger.error(f"Error fetching covers: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/covers/random', methods=['GET'])
def get_random_cover():
    """随机获取一个主页样式"""
    try:
        cover = Cover.query.order_by(db.func.random()).first()
        if not cover:
            return jsonify({'message': 'No covers available', 'cover': None}), 200
        return jsonify(cover.to_dict())
    except Exception as e:
        logger.error(f"Error fetching random cover: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/covers', methods=['POST'])
@login_required_api
def create_cover():
    """创建新的主页样式（支持文件上传）"""
    try:
        logger.debug(f"Create cover request content type: {request.content_type}")

        # 处理文件上传
        if request.content_type and 'multipart/form-data' in request.content_type:
            background_url = None
            music_url = None

            # 处理背景图片
            if 'background' in request.files:
                bg_file = request.files['background']
                if bg_file and bg_file.filename != '' and allowed_file(bg_file.filename):
                    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)

                    filename = secure_filename(bg_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_bg_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    bg_file.save(file_path)

                    base_url = current_app.config['BASE_URL']
                    background_url = f'{base_url}uploads/{unique_filename}'
                    logger.debug(f"Background saved: {file_path}, URL: {background_url}")

            # 处理背景音乐
            if 'music' in request.files:
                music_file = request.files['music']
                if music_file and music_file.filename != '' and allowed_music_file(music_file.filename):
                    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)

                    filename = secure_filename(music_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_music_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    music_file.save(file_path)

                    base_url = current_app.config['BASE_URL']
                    music_url = f'{base_url}uploads/{unique_filename}'
                    logger.debug(f"Music saved: {file_path}, URL: {music_url}")

            # 获取表单数据
            motto = request.form.get('motto', '')

            # 创建封面记录
            cover = Cover(
                background_image=background_url or '',
                motto=motto,
                music=music_url
            )
            db.session.add(cover)
            db.session.commit()
            logger.debug("Cover created successfully")
            return jsonify(cover.to_dict()), 201

        else:
            # 处理 JSON 数据
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            cover = Cover(
                background_image=data.get('background_image', ''),
                motto=data.get('motto', ''),
                music=data.get('music')
            )
            db.session.add(cover)
            db.session.commit()
            return jsonify(cover.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating cover: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/covers/<int:cover_id>', methods=['DELETE'])
@login_required_api
def delete_cover(cover_id):
    """删除主页样式"""
    try:
        cover = Cover.query.get_or_404(cover_id)

        # 删除关联的文件（可选）
        if cover.background_image:
            try:
                filename = cover.background_image.split('/uploads/')[-1]
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                file_path = os.path.join(upload_folder, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Deleted background file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete background file: {e}")

        if cover.music:
            try:
                filename = cover.music.split('/uploads/')[-1]
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                file_path = os.path.join(upload_folder, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Deleted music file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete music file: {e}")

        db.session.delete(cover)
        db.session.commit()
        return jsonify({'message': 'Cover deleted successfully'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting cover: {str(e)}")
        return jsonify({'error': str(e)}), 500
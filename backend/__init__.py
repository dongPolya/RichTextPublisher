from flask import Flask, send_from_directory
from flask_cors import CORS
from .models import db
from flask_migrate import Migrate
from . import routes
from . import developer_routes
import os
from flask_login import LoginManager
from flask_mail import Mail


def create_app():
    app = Flask(__name__)
    app.config.from_object('backend.config.Config')

    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'api.login'
    login_manager.session_protection = "strong"

    mail = Mail()
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # Session 配置（必须在 CORS 之前配置）
    # 生产环境自动启用 Secure Cookie（要求 HTTPS）
    app.config['SESSION_COOKIE_SECURE'] = not app.config.get('DEBUG', False)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24小时

    # 获取 CORS 允许的源列表（支持字符串或列表）
    cors_origins = app.config.get('CORS_ORIGINS', ['http://localhost:5173'])
    if isinstance(cors_origins, str):
        cors_origins = [origin.strip() for origin in cors_origins.split(',')]

    # 启用 CORS - 仅依靠 Flask-CORS 扩展，不再需要自定义 after_request
    CORS(app, resources={r"/api/*": {
        "origins": cors_origins,
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Disposition"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }}, supports_credentials=True)

    # 静态文件服务路由（上传文件）
    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.isabs(upload_folder):
            upload_folder = os.path.join(app.root_path, upload_folder)

        file_path = os.path.join(upload_folder, filename)
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            return "File not found", 404
        return send_from_directory(upload_folder, filename)

    # 注册蓝图
    app.register_blueprint(routes.bp)
    app.register_blueprint(developer_routes.dev_bp)

    # 确保上传目录存在
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(app.root_path, upload_folder)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        app.logger.info(f"Created upload folder: {upload_folder}")

    # 创建数据库表和种子数据（仅开发环境建议保留，生产环境可注释）
    with app.app_context():
        db.create_all()
        from .seed import seed_data
        seed_data()  # 注意：数据模型更改迁移时需要先注释掉这行代码

    return app
import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'WYHlovezc'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///travel_community.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS 配置：允许的前端源，多个用逗号分隔
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    # Session配置
    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'filesystem')  # 或者 "sqlalchemy", "redis" 等
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)  # Session过期时间

    # 邮件配置 - 163邮箱
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.163.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))  # 163邮箱SSL端口
    MAIL_USE_TLS = False  # 163邮箱使用SSL，不使用TLS
    MAIL_USE_SSL = True  # 强制设置为 True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'Cmbself@163.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'LJWOVPSZVAGPRVNT')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'Cmbself@163.com')

    # 安全配置
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'your-password-salt-here')

    # 生产环境特定配置
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    # 基础URL（用于生成上传文件的完整URL）
    #BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000/')
    BASE_URL = os.environ.get('BASE_URL', 'https://fbll.asia/')
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()



class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    title = db.Column(db.String(64))
    bio=db.Column(db.String(128))
    score=db.Column(db.Integer, default=0)
    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    communities = db.relationship('Community', secondary='user_community', backref='members')

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat(),
            'email_verified': self.email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'title':self.title,
            'bio':self.bio,
            'score':self.score
        }


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sub = db.Column(db.String(50))  # 分类: communication, log, community, etc.
    mode = db.Column(db.String(50))
    image = db.Column(db.String(200))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), nullable=True)

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'sub': self.sub,
            'mode': self.mode,
            'image': self.image,
            'likes': self.likes,
            'created_at': self.created_at.isoformat(),
            'author': self.author.to_dict(),
            'comments_count': self.comments.count()
        }


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'author': self.author.to_dict()
        }



class Community(db.Model):
    __tablename__ = 'communities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    avatar = db.Column(db.String(200))
    category = db.Column(db.String(50))
    member_count = db.Column(db.Integer, default=0)
    post_count = db.Column(db.Integer, default=0)
    activity_score = db.Column(db.Integer, default=0)  # 0-100 percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    posts = db.relationship('Post', backref='community', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'avatar': self.avatar,
            'category': self.category,
            'member_count': self.member_count,
            'post_count': self.post_count,
            'activity_score': self.activity_score,
            'created_at': self.created_at.isoformat()
        }


# Association table for many-to-many relationship between User and Community
user_community = db.Table('user_community',
                          db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                          db.Column('community_id', db.Integer, db.ForeignKey('communities.id'), primary_key=True),
                          db.Column('joined_at', db.DateTime, default=datetime.utcnow)
                          )


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON string of options list
    correct_answer = db.Column(db.Integer, nullable=False)  # index of correct option
    sub = db.Column(db.String(50), default='general')  # 新增主题字段
    type = db.Column(db.String(20), default='single')  # single or multiple
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'options': json.loads(self.options) if self.options else [],
            'correct_answer': self.correct_answer,
            'type': self.type,
            'likes': self.likes,
            'sub': self.sub,
            'created_at': self.created_at.isoformat()
        }

class Cover(db.Model):
    """主页封面表 - 存储主页背景图片、副标题和背景音乐"""
    __tablename__ = 'covers'

    id = db.Column(db.Integer, primary_key=True)
    background_image = db.Column(db.String(200), nullable=False)  # 背景图片URL
    motto = db.Column(db.Text)  # 副标题/座右铭
    music = db.Column(db.String(200))  # 背景音乐URL (mp3格式)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'background_image': self.background_image,
            'motto': self.motto,
            'music': self.music,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
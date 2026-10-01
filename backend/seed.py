from .models import db, User, Community, Post, Question
from datetime import datetime, date
import json

def seed_data():
    # 检查是否已有数据
    if User.query.first() is not None:
        return  # 如果已有数据，不再添加

    # 创建默认用户
    user1 = User(
        username='travel_lover',
        email='travel@example.com',
        avatar='https://randomuser.me/api/portraits/men/22.jpg',
        email_verified=True,
        last_login=datetime.utcnow()
    )
    user1.set_password('password123')

    user2 = User(
        username='adventure_seeker',
        email='adventure@example.com',
        avatar='https://randomuser.me/api/portraits/women/32.jpg',
        email_verified=True,
        last_login=datetime.utcnow()
    )
    user2.set_password('password123')

    db.session.add_all([user1, user2])
    db.session.commit()

    # 创建社区
    community1 = Community(
        name='旅行社',
        description='专业的旅行服务社区，提供最新的旅游资讯和优惠活动',
        avatar='https://images.unsplash.com/photo-1590649880760-2d4b0f523de7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=774&q=80',
        category='出行交流',
        member_count=342,
        post_count=128,
        activity_score=78
    )

    community2 = Community(
        name='电子音乐',
        description='电子音乐爱好者聚集地，分享音乐节信息和演出资讯',
        avatar='https://images.unsplash.com/photo-1470225620780-dba8ba36b745?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1740&q=80',
        category='电子音乐',
        member_count=278,
        post_count=156,
        activity_score=85
    )

    db.session.add_all([community1, community2])
    db.session.commit()

    # 创建帖子
    post1 = Post(
        title='西藏之旅：心灵的洗礼',
        content='这次西藏之行让我感受到了前所未有的宁静与平和。布达拉宫的庄严，纳木错的纯净，还有那些虔诚的信徒，都让我对生活有了新的认识。',
        sub='communication',
        image='https://images.unsplash.com/photo-1544735716-392fe2489ffc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        likes=42,
        user_id=user1.id
    )

    post2 = Post(
        title='日本樱花季旅行攻略',
        content='分享今年樱花季的日本旅行经验，包括最佳观赏地点、住宿推荐和交通指南。',
        sub='log',
        image='https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        likes=28,
        user_id=user2.id,
        community_id=community1.id
    )

    db.session.add_all([post1, post2])
    db.session.commit()


    # 创建问题
    questions = [
        Question(
            question='下列哪一项不是世界文化遗产？',
            options=json.dumps([
                'A. 中国的长城',
                'B. 印度的泰姬陵',
                'C. 美国的自由女神像',
                'D. 埃及的金字塔'
            ]),
            correct_answer=2,
            type='single',
            sub='自然人文',
            likes=15
        ),
        Question(
            question='世界上最大的珊瑚礁系统是？',
            options=json.dumps([
                'A. 大堡礁',
                'B. 马尔代夫珊瑚礁',
                'C. 红海珊瑚礁',
                'D. 佛罗里达珊瑚礁'
            ]),
            correct_answer=0,
            type='single',
            sub='自然人文',
            likes=12
        )
    ]

    for question in questions:
        db.session.add(question)
    db.session.commit()

    print("Seed data created successfully!")
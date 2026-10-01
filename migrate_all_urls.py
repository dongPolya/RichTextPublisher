"""
生产环境 URL 迁移脚本（支持试运行和安全提交）
用途：将数据库中所有存储的本地开发 URL (http://localhost:5000) 替换为生产域名。
适用表：covers, posts, communities, users
执行前请务必备份数据库！

使用方法：
    # 试运行（只输出变更，不修改数据库）
    python migrate_all_urls.py

    # 实际执行（需要二次确认）
    python migrate_all_urls.py --commit
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app, db
from backend.models import Cover, Post, Community, User


def migrate_urls(dry_run=True):
    app = create_app()
    with app.app_context():
        # 生产域名（从配置读取，并去除尾部斜杠）
        new_base = app.config['BASE_URL'].rstrip('/')
        # 开发环境旧域名（不带尾部斜杠）
        old_base = 'http://localhost:5000'

        # 打印当前数据库连接信息（便于确认）
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"🔗 当前数据库: {db_uri}")
        print(f"🔄 将把 '{old_base}' 替换为 '{new_base}'")
        if dry_run:
            print("🧪 试运行模式：仅输出变更，不会修改数据库")
        else:
            print("⚠️  实际执行模式：将修改数据库！")
            confirm = input("请输入 'yes' 继续执行: ")
            if confirm.lower() != 'yes':
                print("❌ 操作已取消")
                return

        total_updated = 0
        changes = []  # 记录所有变更，用于输出

        # 1. 更新 covers 表
        covers = Cover.query.all()
        for cover in covers:
            updated_fields = []
            if cover.background_image and old_base in cover.background_image:
                new_url = cover.background_image.replace(old_base, new_base)
                changes.append({
                    'table': 'covers',
                    'id': cover.id,
                    'field': 'background_image',
                    'old': cover.background_image,
                    'new': new_url
                })
                if not dry_run:
                    cover.background_image = new_url
                updated_fields.append('background_image')
            if cover.music and old_base in cover.music:
                new_url = cover.music.replace(old_base, new_base)
                changes.append({
                    'table': 'covers',
                    'id': cover.id,
                    'field': 'music',
                    'old': cover.music,
                    'new': new_url
                })
                if not dry_run:
                    cover.music = new_url
                updated_fields.append('music')
            if updated_fields:
                total_updated += 1

        # 2. 更新 posts 表的 image 字段
        posts = Post.query.filter(Post.image.isnot(None)).all()
        for post in posts:
            if post.image and old_base in post.image:
                new_url = post.image.replace(old_base, new_base)
                changes.append({
                    'table': 'posts',
                    'id': post.id,
                    'field': 'image',
                    'old': post.image,
                    'new': new_url
                })
                if not dry_run:
                    post.image = new_url
                total_updated += 1

        # 3. 更新 communities 表的 avatar 字段
        communities = Community.query.filter(Community.avatar.isnot(None)).all()
        for community in communities:
            if community.avatar and old_base in community.avatar:
                new_url = community.avatar.replace(old_base, new_base)
                changes.append({
                    'table': 'communities',
                    'id': community.id,
                    'field': 'avatar',
                    'old': community.avatar,
                    'new': new_url
                })
                if not dry_run:
                    community.avatar = new_url
                total_updated += 1

        # 4. 更新 users 表的 avatar 字段（只替换本地上传的，保留外部URL）
        users = User.query.filter(User.avatar.isnot(None)).all()
        for user in users:
            if user.avatar and old_base in user.avatar:
                new_url = user.avatar.replace(old_base, new_base)
                changes.append({
                    'table': 'users',
                    'id': user.id,
                    'field': 'avatar',
                    'old': user.avatar,
                    'new': new_url
                })
                if not dry_run:
                    user.avatar = new_url
                total_updated += 1

        # 输出所有变更
        if changes:
            print("\n📝 待更改的条目：")
            for change in changes:
                print(f"[{change['table']}] ID {change['id']} - {change['field']}")
                print(f"    旧: {change['old']}")
                print(f"    新: {change['new']}")
            print(f"\n共 {total_updated} 条记录需要更新。")
        else:
            print("✅ 没有发现需要更新的记录。")

        # 实际提交
        if not dry_run and changes:
            try:
                db.session.commit()
                print(f"\n✅ 迁移完成！共更新 {total_updated} 条记录。")
                print(f"📊 新域名: {new_base}")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ 提交失败: {str(e)}")
                sys.exit(1)
        elif dry_run and changes:
            print("\n💡 试运行完成。若要实际执行，请运行: python migrate_all_urls.py --commit")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='替换数据库中的本地URL为生产域名')
    parser.add_argument('--commit', action='store_true', help='实际执行提交（默认为试运行）')
    args = parser.parse_args()

    migrate_urls(dry_run=not args.commit)
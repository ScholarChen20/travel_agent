"""
MySQL种子数据脚本

功能：
1. 创建默认角色（user, admin）
2. 创建默认权限
3. 分配权限给角色
4. 可选：创建管理员账户
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import get_settings
from app.database.mysql import MySQLDatabase
from app.database.models import Role, Permission, RolePermission
from passlib.context import CryptContext


def seed_data():
    """初始化种子数据"""
    settings = get_settings()

    print("="*60)
    print("🌱 开始初始化种子数据...")
    print("="*60)

    # 连接MySQL
    print(f"\n📡 连接MySQL: {settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}")
    mysql_db = MySQLDatabase(settings.mysql_url)

    try:
        # 测试连接
        if not mysql_db.health_check():
            print("❌ MySQL连接失败")
            return False
        print("✅ MySQL连接成功")
    except Exception as e:
        print(f"❌ MySQL连接失败: {str(e)}")
        return False

    # ========== 创建角色 ==========
    print("\n" + "="*60)
    print("👥 创建角色...")
    print("="*60)

    with mysql_db.get_session() as session:
        # 检查角色是否已存在
        existing_roles = session.query(Role).all()
        if existing_roles:
            print("  ⚠️  角色已存在，跳过创建")
            roles_dict = {role.name: role for role in existing_roles}
        else:
            roles_data = [
                {"name": "user", "description": "普通用户角色"},
                {"name": "admin", "description": "管理员角色，拥有所有权限"}
            ]

            roles_dict = {}
            for role_data in roles_data:
                role = Role(**role_data)
                session.add(role)
                roles_dict[role.name] = role
                print(f"  ✅ 创建角色: {role.name}")

            session.flush()  # 确保角色ID已生成

    # ========== 创建权限 ==========
    print("\n" + "="*60)
    print("🔐 创建权限...")
    print("="*60)

    with mysql_db.get_session() as session:
        # 检查权限是否已存在
        existing_perms = session.query(Permission).count()
        if existing_perms > 0:
            print(f"  ⚠️  权限已存在（{existing_perms}个），跳过创建")
        else:
            permissions_data = [
                # 用户相关权限
                {"name": "查看个人资料", "resource": "user", "action": "read", "description": "查看自己的用户资料"},
                {"name": "编辑个人资料", "resource": "user", "action": "update", "description": "编辑自己的用户资料"},
                {"name": "修改密码", "resource": "user", "action": "update_password", "description": "修改自己的密码"},

                # 旅行计划权限
                {"name": "生成旅行计划", "resource": "trip", "action": "create", "description": "生成新的旅行计划"},
                {"name": "查看旅行计划", "resource": "trip", "action": "read", "description": "查看自己的旅行计划"},
                {"name": "编辑旅行计划", "resource": "trip", "action": "update", "description": "编辑自己的旅行计划"},
                {"name": "删除旅行计划", "resource": "trip", "action": "delete", "description": "删除自己的旅行计划"},

                # 对话权限
                {"name": "创建对话", "resource": "dialog", "action": "create", "description": "创建对话会话"},
                {"name": "查看对话历史", "resource": "dialog", "action": "read", "description": "查看自己的对话历史"},
                {"name": "删除对话", "resource": "dialog", "action": "delete", "description": "删除自己的对话"},

                # 社交权限
                {"name": "发布帖子", "resource": "post", "action": "create", "description": "发布新帖子"},
                {"name": "查看帖子", "resource": "post", "action": "read", "description": "查看帖子"},
                {"name": "编辑帖子", "resource": "post", "action": "update", "description": "编辑自己的帖子"},
                {"name": "删除帖子", "resource": "post", "action": "delete", "description": "删除自己的帖子"},

                {"name": "发表评论", "resource": "comment", "action": "create", "description": "发表评论"},
                {"name": "删除评论", "resource": "comment", "action": "delete", "description": "删除自己的评论"},

                {"name": "点赞", "resource": "like", "action": "create", "description": "点赞帖子或评论"},
                {"name": "取消点赞", "resource": "like", "action": "delete", "description": "取消点赞"},

                {"name": "关注用户", "resource": "follow", "action": "create", "description": "关注其他用户"},
                {"name": "取消关注", "resource": "follow", "action": "delete", "description": "取消关注用户"},

                # 管理员权限
                {"name": "管理用户", "resource": "admin_user", "action": "manage", "description": "管理所有用户"},
                {"name": "审核内容", "resource": "admin_content", "action": "moderate", "description": "审核用户发布的内容"},
                {"name": "查看系统日志", "resource": "admin_log", "action": "read", "description": "查看系统日志"},
                {"name": "系统配置", "resource": "admin_config", "action": "manage", "description": "管理系统配置"},
            ]

            for perm_data in permissions_data:
                permission = Permission(**perm_data)
                session.add(permission)

            print(f"  ✅ 创建 {len(permissions_data)} 个权限")

    # ========== 分配权限给角色 ==========
    print("\n" + "="*60)
    print("🔗 分配权限给角色...")
    print("="*60)

    with mysql_db.get_session() as session:
        # 获取所有角色和权限
        user_role = session.query(Role).filter_by(name="user").first()
        admin_role = session.query(Role).filter_by(name="admin").first()
        all_permissions = session.query(Permission).all()

        # 检查是否已分配
        existing_role_perms = session.query(RolePermission).count()
        if existing_role_perms > 0:
            print("  ⚠️  权限已分配，跳过")
        else:
            # 普通用户权限（排除admin_*开头的权限）
            user_permissions = [p for p in all_permissions if not p.resource.startswith("admin_")]
            for perm in user_permissions:
                role_perm = RolePermission(role_id=user_role.id, permission_id=perm.id)
                session.add(role_perm)

            print(f"  ✅ 为 user 角色分配 {len(user_permissions)} 个权限")

            # 管理员权限（所有权限）
            for perm in all_permissions:
                role_perm = RolePermission(role_id=admin_role.id, permission_id=perm.id)
                session.add(role_perm)

            print(f"  ✅ 为 admin 角色分配 {len(all_permissions)} 个权限（全部权限）")

    # ========== 可选：创建管理员账户 ==========
    print("\n" + "="*60)
    print("👤 创建管理员账户（可选）...")
    print("="*60)

    create_admin = input("  是否创建默认管理员账户？(y/n): ").strip().lower()

    if create_admin == 'y':
        admin_username = input("  请输入管理员用户名 [默认: admin]: ").strip() or "admin"
        admin_email = input("  请输入管理员邮箱 [默认: admin@example.com]: ").strip() or "admin@example.com"
        admin_password = input("  请输入管理员密码 [默认: Admin@123456]: ").strip() or "Admin@123456"

        with mysql_db.get_session() as session:
            # 检查是否已存在
            from app.database.models import User, UserRole
            existing_admin = session.query(User).filter_by(username=admin_username).first()

            if existing_admin:
                print(f"  ⚠️  管理员 '{admin_username}' 已存在，跳过创建")
            else:
                # 哈希密码
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                password_hash = pwd_context.hash(admin_password)

                # 创建用户
                admin_user = User(
                    username=admin_username,
                    email=admin_email,
                    password_hash=password_hash,
                    role="admin",
                    is_active=True,
                    is_verified=True
                )
                session.add(admin_user)
                session.flush()

                # 分配admin角色
                admin_role = session.query(Role).filter_by(name="admin").first()
                user_role_assoc = UserRole(user_id=admin_user.id, role_id=admin_role.id)
                session.add(user_role_assoc)

                print(f"  ✅ 创建管理员账户: {admin_username}")
                print(f"     邮箱: {admin_email}")
                print(f"     密码: {admin_password}")
                print(f"     ⚠️  请务必修改默认密码！")
    else:
        print("  ⏭️  跳过管理员账户创建")

    # 关闭连接
    mysql_db.close()

    print("\n" + "="*60)
    print("✅ 种子数据初始化完成！")
    print("="*60)

    return True


if __name__ == "__main__":
    try:
        success = seed_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

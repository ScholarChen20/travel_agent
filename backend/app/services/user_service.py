"""
用户管理服务

功能：
1. 获取用户资料
2. 更新用户资料
3. 获取用户旅行统计
4. 获取访问过的城市列表
5. 修改密码
"""

from typing import Optional, Dict, Any, List
from loguru import logger

from ..database.mysql import get_mysql_db
from ..database.models import User, UserProfile
from ..services.auth_service import get_auth_service
from ..services.travel_plan_service import get_travel_plan_service


class UserService:
    """用户管理服务类"""

    def __init__(self):
        """初始化服务"""
        self.mysql_db = get_mysql_db()
        self.auth_service = get_auth_service()
        logger.info("用户服务已初始化")

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户资料

        Args:
            user_id: 用户ID

        Returns:
            Dict: 用户资料，包含User和UserProfile信息
        """
        try:
            with self.mysql_db.get_session() as session:
                # 查询用户
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    logger.warning(f"用户不存在: {user_id}")
                    return None

                # 查询用户档案
                profile = session.query(UserProfile).filter(
                    UserProfile.user_id == user_id
                ).first()

                # 构建响应
                user_data = {
                    # 基本信息
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "avatar_url": user.avatar_url,
                    "is_verified": user.is_verified,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,

                    # 档案信息
                    "profile": {
                        "travel_preferences": profile.travel_preferences if profile else [],
                        "visited_cities": profile.visited_cities if profile else [],
                        "travel_stats": profile.travel_stats if profile else {}
                    }
                }

                return user_data

        except Exception as e:
            logger.error(f"获取用户资料失败: {str(e)}")
            raise

    def update_user_profile(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        avatar_url: Optional[str] = None,
        travel_preferences: Optional[List[str]] = None
    ) -> bool:
        """
        更新用户资料

        Args:
            user_id: 用户ID
            username: 用户名（可选）
            email: 邮箱（可选）
            avatar_url: 头像URL（可选）
            travel_preferences: 旅行偏好（可选）

        Returns:
            bool: 是否成功
        """
        try:
            with self.mysql_db.get_session() as session:
                # 查询用户
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    logger.warning(f"用户不存在: {user_id}")
                    return False

                # 更新User表字段
                if username is not None:
                    # 检查用户名是否已被使用
                    existing_user = session.query(User).filter(
                        User.username == username,
                        User.id != user_id
                    ).first()

                    if existing_user:
                        logger.warning(f"用户名已被使用: {username}")
                        raise ValueError("用户名已被使用")

                    user.username = username

                if email is not None:
                    # 检查邮箱是否已被使用
                    existing_user = session.query(User).filter(
                        User.email == email,
                        User.id != user_id
                    ).first()

                    if existing_user:
                        logger.warning(f"邮箱已被使用: {email}")
                        raise ValueError("邮箱已被使用")

                    user.email = email
                    # 如果修改邮箱，需要重新验证
                    user.is_verified = False

                if avatar_url is not None:
                    user.avatar_url = avatar_url

                # 更新UserProfile表字段
                if travel_preferences is not None:
                    profile = session.query(UserProfile).filter(
                        UserProfile.user_id == user_id
                    ).first()

                    if profile:
                        profile.travel_preferences = travel_preferences
                    else:
                        # 如果档案不存在，创建
                        profile = UserProfile(
                            user_id=user_id,
                            travel_preferences=travel_preferences,
                            visited_cities=[],
                            travel_stats={}
                        )
                        session.add(profile)

                logger.info(f"用户资料已更新: {user_id}")
                return True

        except ValueError:
            # 重新抛出值错误（用户名或邮箱冲突）
            raise
        except Exception as e:
            logger.error(f"更新用户资料失败: {str(e)}")
            raise

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户旅行统计数据

        从MongoDB聚合获取准确数据

        Args:
            user_id: 用户ID

        Returns:
            Dict: 统计数据
        """
        try:
            plan_service = get_travel_plan_service()

            # 从MongoDB获取统计
            stats = await plan_service.get_user_stats(user_id)

            # 同步更新MySQL中的travel_stats
            try:
                with self.mysql_db.get_session() as session:
                    profile = session.query(UserProfile).filter(
                        UserProfile.user_id == user_id
                    ).first()

                    if profile:
                        profile.travel_stats = stats
            except Exception as e:
                logger.warning(f"同步统计数据到MySQL失败: {str(e)}")

            return stats

        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            raise

    def get_visited_cities(self, user_id: int) -> List[str]:
        """
        获取用户访问过的城市列表

        Args:
            user_id: 用户ID

        Returns:
            List[str]: 城市列表
        """
        try:
            with self.mysql_db.get_session() as session:
                profile = session.query(UserProfile).filter(
                    UserProfile.user_id == user_id
                ).first()

                if profile:
                    return profile.visited_cities or []
                else:
                    return []

        except Exception as e:
            logger.error(f"获取访问城市列表失败: {str(e)}")
            raise

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码

        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            bool: 是否成功
        """
        try:
            # 1. 验证新密码强度
            is_valid, error_msg = self.auth_service.validate_password_strength(new_password)
            if not is_valid:
                logger.warning(f"新密码强度不足: {user_id}")
                raise ValueError(error_msg)

            with self.mysql_db.get_session() as session:
                # 2. 查询用户
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    logger.warning(f"用户不存在: {user_id}")
                    return False

                # 3. 验证旧密码
                if not self.auth_service.verify_password(old_password, user.password_hash):
                    logger.warning(f"旧密码错��: {user_id}")
                    raise ValueError("旧密码错误")

                # 4. 哈希新密码
                new_password_hash = self.auth_service.hash_password(new_password)

                # 5. 更新密码
                user.password_hash = new_password_hash

                logger.info(f"密码已修改: {user_id}")
                return True

        except ValueError:
            # 重新抛出值错误（密码强度或旧密码错误）
            raise
        except Exception as e:
            logger.error(f"修改密码失败: {str(e)}")
            raise

    def update_avatar(self, user_id: int, avatar_url: str) -> bool:
        """
        更新用户头像

        Args:
            user_id: 用户ID
            avatar_url: 头像URL

        Returns:
            bool: 是否成功
        """
        try:
            with self.mysql_db.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    logger.warning(f"用户不存在: {user_id}")
                    return False

                user.avatar_url = avatar_url

                logger.info(f"头像已更新: {user_id} -> {avatar_url}")
                return True

        except Exception as e:
            logger.error(f"更新头像失败: {str(e)}")
            raise


# ========== 全局实例（单例模式） ==========

_user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """
    获取全局用户服务实例（单例）

    Returns:
        UserService: 用户服务实例
    """
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service

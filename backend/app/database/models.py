"""SQLAlchemy ORM模型定义

定义MySQL数据库中所有表的ORM映射
"""

from datetime import datetime
from typing import List
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, DateTime,
    Date, Enum, ForeignKey, Index, UniqueConstraint, JSON
)
from sqlalchemy.orm import relationship
from .mysql import Base


# ========== 用户与认证模型 ==========

class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(Enum('user', 'admin', name='user_role'), default='user', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # 关系
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete-orphan")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
        Index('idx_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserProfile(Base):
    """用户档案表"""
    __tablename__ = "user_profiles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    gender = Column(Enum('male', 'female', 'other', name='gender_type'), nullable=True)
    birth_date = Column(Date, nullable=True)
    location = Column(String(200), nullable=True)
    travel_preferences = Column(JSON, nullable=True, comment='旅行偏好标签数组')
    visited_cities = Column(JSON, nullable=True, comment='访问过的城市数组')
    travel_stats = Column(JSON, nullable=True, comment='旅行统计信息')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, full_name='{self.full_name}')>"


# ========== RBAC权限模型 ==========

class Role(Base):
    """角色表"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", secondary="user_roles", backref="user_roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(50), nullable=False, comment='API资源')
    action = Column(String(50), nullable=False, comment='操作：create, read, update, delete')
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

    # 索引
    __table_args__ = (
        UniqueConstraint('resource', 'action', name='unique_permission'),
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"


class RolePermission(Base):
    """角色-权限关联表"""
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)


class UserRole(Base):
    """用户-角色关联表"""
    __tablename__ = "user_roles"

    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)


# ========== 社交模型 ==========

class Post(Base):
    """帖子表"""
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, nullable=True, comment='图片/视频URL数组')
    tags = Column(JSON, nullable=True, comment='标签数组')
    location = Column(String(200), nullable=True)
    trip_plan_id = Column(String(50), nullable=True, comment='关联的MongoDB旅行计划ID')
    status = Column(Enum('draft', 'published', 'hidden', 'deleted', name='post_status'), default='published', nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
    is_moderated = Column(Boolean, default=False, nullable=False)
    moderation_status = Column(Enum('pending', 'approved', 'rejected', name='moderation_status'), default='pending', nullable=False)
    moderation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)

    # 关系
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    post_tags = relationship("PostTag", back_populates="post", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_published_at', 'published_at'),
        Index('idx_moderation_status', 'moderation_status'),
    )

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title[:30]}...', user_id={self.user_id})>"


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_id = Column(BigInteger, ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, comment='父评论ID，用于嵌套回复')
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    # 索引
    __table_args__ = (
        Index('idx_post_created', 'post_id', 'created_at'),
        Index('idx_parent', 'parent_id'),
    )

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"


class Like(Base):
    """点赞表"""
    __tablename__ = "likes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_type = Column(Enum('post', 'comment', name='like_target_type'), nullable=False)
    target_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="likes")

    # 索引和约束
    __table_args__ = (
        UniqueConstraint('user_id', 'target_type', 'target_id', name='unique_like'),
        Index('idx_target', 'target_type', 'target_id'),
    )

    def __repr__(self):
        return f"<Like(id={self.id}, user_id={self.user_id}, target_type='{self.target_type}', target_id={self.target_id})>"


class Follow(Base):
    """关注表"""
    __tablename__ = "follows"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    follower_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    following_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")

    # 索引和约束
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_follow'),
        Index('idx_follower', 'follower_id'),
        Index('idx_following', 'following_id'),
    )

    def __repr__(self):
        return f"<Follow(id={self.id}, follower_id={self.follower_id}, following_id={self.following_id})>"


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=True)
    use_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    post_tags = relationship("PostTag", back_populates="tag", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_use_count', 'use_count'),
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', use_count={self.use_count})>"


class PostTag(Base):
    """帖子-标签关联表"""
    __tablename__ = "post_tags"

    post_id = Column(BigInteger, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)

    # 关系
    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag", back_populates="post_tags")


# ========== 验证码记录 ==========

class CaptchaRecord(Base):
    """验证码记录表"""
    __tablename__ = "captcha_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    captcha_code = Column(String(10), nullable=False)
    attempt_count = Column(Integer, default=0, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)

    # 索引
    __table_args__ = (
        Index('idx_session', 'session_id'),
        Index('idx_expires', 'expires_at'),
    )

    def __repr__(self):
        return f"<CaptchaRecord(id={self.id}, session_id='{self.session_id}', is_verified={self.is_verified})>"


# ========== 审计日志 ==========

class AuditLog(Base):
    """审计日志表"""
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True, comment='操作用户ID，NULL表示系统操作')
    action = Column(String(100), nullable=False, comment='操作类型')
    resource = Column(String(100), nullable=False, comment='操作资源')
    resource_id = Column(String(100), nullable=True, comment='资源ID')
    details = Column(JSON, nullable=True, comment='操作详情')
    ip_address = Column(String(45), nullable=True, comment='IP地址')
    user_agent = Column(Text, nullable=True, comment='User-Agent')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 索引
    __table_args__ = (
        Index('idx_user_action', 'user_id', 'action'),
        Index('idx_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}', resource='{self.resource}')>"

"""服务模块"""

from .auth_service import get_auth_service
from .user_service import get_user_service
from .travel_plan_service import get_travel_plan_service
from .dialog_service import get_dialog_service
from .amap_service import get_amap_service
from .unsplash_service import get_unsplash_service
from .llm_service import get_llm
from .admin_service import get_admin_service
from .social_service import get_social_service
from .voice_service import get_voice_service
from .storage_service import get_storage_service
from .monitoring_service import get_monitoring_service
from .douyin_service import get_douyin_service

__all__ = [
    "get_auth_service",
    "get_user_service",
    "get_travel_plan_service",
    "get_dialog_service",
    "get_amap_service",
    "get_unsplash_service",
    "get_llm",
    "get_admin_service",
    "get_social_service",
    "get_voice_service",
    "get_storage_service",
    "get_monitoring_service",
    "get_douyin_service"
]


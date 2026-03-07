"""离线功能服务"""

import zipfile
import os
import json
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..config import get_settings

settings = get_settings()


class DownloadMapRequest(BaseModel):
    """下载地图请求"""
    city: str = Field(..., description="城市名称")
    user_id: Optional[str] = Field(None, description="用户ID")


class DownloadMapResponse(BaseModel):
    """下载地图响应"""
    city: str = Field(..., description="城市名称")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小（字节）")
    version: str = Field(..., description="数据版本")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class SyncOfflineDataRequest(BaseModel):
    """同步离线数据请求"""
    user_id: str = Field(..., description="用户ID")
    data: Dict = Field(..., description="同步数据")


class SyncOfflineDataResponse(BaseModel):
    """同步离线数据响应"""
    user_id: str = Field(..., description="用户ID")
    sync_id: str = Field(..., description="同步ID")
    status: str = Field(..., description="同步状态")
    synced_at: datetime = Field(default_factory=datetime.now, description="同步时间")


class OfflineService:
    """离线功能服务"""

    def __init__(self, offline_dir: str = "offline_data"):
        self.offline_dir = Path(offline_dir)
        self.offline_dir.mkdir(parents=True, exist_ok=True)
        self.user_data_dir = self.offline_dir / "user_data"
        self.user_data_dir.mkdir(exist_ok=True)

    def download_map(self, request: DownloadMapRequest) -> DownloadMapResponse:
        """下载离线地图"""
        map_file = self.offline_dir / f"{request.city}_map.zip"
        self._generate_map_package(request.city, map_file)
        file_size = map_file.stat().st_size
        version = "1.0"
        
        return DownloadMapResponse(
            city=request.city,
            file_path=str(map_file),
            file_size=file_size,
            version=version
        )

    def _generate_map_package(self, city: str, output_file: Path) -> None:
        """生成地图数据包"""
        map_data = self._get_map_data(city)
        metadata = {
            "version": "1.0",
            "city": city,
            "created_at": datetime.now().isoformat()
        }
        
        with zipfile.ZipFile(output_file, 'w') as zipf:
            zipf.writestr(f"{city}_map.json", json.dumps(map_data, ensure_ascii=False))
            zipf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False))

    def _get_map_data(self, city: str) -> Dict:
        """获取地图数据"""
        return {
            "city": city,
            "pois": [
                {"id": "1", "name": "故宫博物院", "type": "景点", "address": "北京市东城区景山前街4号"},
                {"id": "2", "name": "天安门广场", "type": "景点", "address": "北京市东城区天安门广场"},
                {"id": "3", "name": "全聚德", "type": "餐厅", "address": "北京市东城区前门大街14号"}
            ],
            "routes": [
                {"id": "r1", "name": "故宫游览路线", "type": "walking", "points": []}
            ]
        }

    def sync_offline_data(self, request: SyncOfflineDataRequest) -> SyncOfflineDataResponse:
        """同步离线数据"""
        user_dir = self.user_data_dir / request.user_id
        user_dir.mkdir(exist_ok=True)
        
        sync_id = f"sync_{int(datetime.now().timestamp())}"
        sync_file = user_dir / f"{sync_id}.json"
        
        with open(sync_file, 'w', encoding='utf-8') as f:
            json.dump(request.data, f, ensure_ascii=False)
        
        return SyncOfflineDataResponse(
            user_id=request.user_id,
            sync_id=sync_id,
            status="success"
        )

    def get_offline_data(self, user_id: str, sync_id: Optional[str] = None) -> Dict:
        """获取离线数据"""
        user_dir = self.user_data_dir / user_id
        if not user_dir.exists():
            return {}
        
        if sync_id:
            sync_file = user_dir / f"{sync_id}.json"
            if sync_file.exists():
                with open(sync_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        
        data_files = sorted(user_dir.glob("sync_*.json"), reverse=True)
        if data_files:
            with open(data_files[0], 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

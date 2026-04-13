"""
RAG数据导入服务
功能：
1. 文本增强（OCR提取）
2. 可信度评分计算
3. 向量化（密集+稀疏）
4. 导入Qdrant混合索引
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
import asyncio
import re
from datetime import datetime
from loguru import logger

from .credibility_calculator import CredibilityCalculator, CredibilityScore
from .hybrid_vector_store import (
    HybridVectorStore,
    PostPayload,
    ImagePayload,
    get_hybrid_vector_store
)


@dataclass
class ImportConfig:
    """导入配置"""
    batch_size: int = 20
    enable_ocr: bool = False  # OCR需要额外依赖，默认关闭
    enable_sparse_vector: bool = True
    credibility_threshold: float = 0.65
    skip_low_credibility: bool = True  # 跳过低置信度帖子


@dataclass
class ImportResult:
    """导入结果"""
    total: int = 0
    success: int = 0
    skipped_low_credibility: int = 0
    failed: int = 0
    errors: List[str] = field(default_factory=list)


class RAGDataImporter:
    """RAG数据导入器"""

    def __init__(
        self,
        import_config: Optional[ImportConfig] = None,
        credibility_calculator: Optional[CredibilityCalculator] = None
    ):
        self.config = import_config or ImportConfig()
        self.credibility_calc = credibility_calculator or CredibilityCalculator()
        self._vector_store: Optional[HybridVectorStore] = None
        self._embedding_service = None

    async def initialize(self):
        """初始化服务"""
        self._vector_store = await get_hybrid_vector_store()

        # 初始化向量化服务
        try:
            from .embedding_service import get_embedding_service
            self._embedding_service = get_embedding_service()
        except Exception as e:
            logger.warning(f"向量化服务初始化失败: {e}")

    async def import_from_json_file(
        self,
        file_path: str,
        city: Optional[str] = None
    ) -> ImportResult:
        """
        从JSON文件导入数据

        Args:
            file_path: JSON文件路径
            city: 城市名称（可选，从文件名提取）

        Returns:
            ImportResult
        """
        result = ImportResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                data = [data]

            result.total = len(data)

            # 从文件名提取城市
            if not city:
                file_name = Path(file_path).stem
                city = file_name.replace("旅游", "").replace("攻略", "")

            # 批量处理
            for i in range(0, len(data), self.config.batch_size):
                batch = data[i:i + self.config.batch_size]
                batch_result = await self._import_batch(batch, city)

                result.success += batch_result['success']
                result.skipped_low_credibility += batch_result['skipped']
                result.failed += batch_result['failed']
                result.errors.extend(batch_result.get('errors', []))

            logger.info(
                f"导入完成: {file_path}, "
                f"总数={result.total}, 成功={result.success}, "
                f"跳过={result.skipped_low_credibility}, 失败={result.failed}"
            )

        except Exception as e:
            logger.error(f"导入文件失败: {file_path}, 错误: {e}")
            result.errors.append(str(e))

        return result

    async def _import_batch(
        self,
        posts: List[Dict],
        city: str
    ) -> Dict[str, int]:
        """批量导入帖子"""
        result = {'success': 0, 'skipped': 0, 'failed': 0, 'errors': []}

        posts_to_insert = []

        for post in posts:
            try:
                # 1. 计算置信度
                credibility_score = self._calculate_credibility(post, city)

                # 2. 跳过低置信度帖子
                if (self.config.skip_low_credibility and
                    credibility_score.final_score < self.config.credibility_threshold):
                    result['skipped'] += 1
                    logger.debug(
                        f"跳过低置信度帖子: {post.get('id')}, "
                        f"分数={credibility_score.final_score:.3f}"
                    )
                    continue

                # 3. 构建增强文本
                enriched_text = self._build_enriched_text(post)

                # 4. 向量化（如果服务可用）
                dense_vector = None
                sparse_vector = None

                if self._embedding_service:
                    try:
                        emb_result = await self._embedding_service.embed_text(enriched_text)
                        if emb_result.success:
                            dense_vector = emb_result.embedding
                    except Exception as e:
                        logger.warning(f"向量化失败: {e}")

                # 跳过无向量的帖子
                if not dense_vector:
                    logger.debug(f"跳过无向量的帖子: {post.get('id')}")
                    result['skipped'] += 1
                    continue

                # 5. 生成稀疏向量
                if self.config.enable_sparse_vector:
                    sparse_vector = self._generate_sparse_vector(enriched_text)

                # 6. 构建Payload
                payload = self._build_post_payload(post, city, credibility_score)

                posts_to_insert.append({
                    'post_id': post.get('id', ''),
                    'dense_vector': dense_vector,
                    'sparse_vector': sparse_vector,
                    'payload': payload
                })

            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f"处理帖子失败: {post.get('id')}, {e}")

        # 批量插入
        if posts_to_insert and self._vector_store:
            inserted = await self._vector_store.upsert_posts_batch(posts_to_insert)
            result['success'] = inserted

        return result

    def _calculate_credibility(
        self,
        post: Dict,
        city: str
    ) -> CredibilityScore:
        """计算帖子置信度"""
        # 构造评分所需字段
        score_input = {
            'is_verified': post.get('is_verified', False),
            'followers': post.get('followers', 0),
            'report_rate': post.get('report_rate', 0),
            'images': post.get('image_urls', []),
            'image_count': post.get('image_count', 0),
            'desc': post.get('desc', ''),
            'likes': post.get('likes', 0),
            'collects': post.get('collects', 0),
            'comments': post.get('comments', 0),
            'publish_time': post.get('publish_time'),
            'has_real_photos': True,  # 默认为实拍
            'useful_comments_ratio': 0.5,  # 默认值
        }

        # 如果image_urls是字符串，解析为列表
        image_urls = post.get('image_urls', [])
        if isinstance(image_urls, str):
            try:
                image_urls = json.loads(image_urls)
                score_input['images'] = image_urls
                score_input['image_count'] = len(image_urls)
            except:
                pass

        return self.credibility_calc.calculate(score_input)

    def _build_enriched_text(self, post: Dict) -> str:
        """构建增强文本"""
        parts = []

        # 标题
        title = post.get('title', '')
        if title:
            parts.append(title)

        # 描述
        desc = post.get('desc', '')
        if desc:
            parts.append(desc)

        # 标签
        tags = post.get('tags', '')
        if isinstance(tags, str):
            # 解析 "标签1[话题],标签2[话题]" 格式
            tag_list = re.findall(r'([^,\[\]]+)\[话题\]', tags)
            if tag_list:
                parts.append(' '.join(tag_list))
        elif isinstance(tags, list):
            parts.append(' '.join(tags))

        # OCR内容（如果有）
        ocr_summary = post.get('ocr_summary', '')
        if ocr_summary:
            parts.append(f"OCR: {ocr_summary}")

        return ' '.join(parts)

    def _generate_sparse_vector(self, text: str) -> Dict[int, float]:
        """
        生成稀疏向量（简单实现）

        注意：使用hashlib确保跨进程一致性

        生产环境建议使用:
        - BGE-M3的稀疏向量输出
        - SPLADE
        - BM25
        """
        import hashlib

        words = re.findall(r'\w+', text.lower())
        word_freq = {}
        for word in words:
            # 使用md5哈希确保跨进程一致性
            word_hash = int(hashlib.md5(word.encode()).hexdigest()[:8], 16) % 100000
            word_freq[word_hash] = word_freq.get(word_hash, 0) + 1

        # 归一化
        max_freq = max(word_freq.values()) if word_freq else 1
        return {k: v / max_freq for k, v in word_freq.items()}

    def _build_post_payload(
        self,
        post: Dict,
        city: str,
        credibility_score: CredibilityScore
    ) -> PostPayload:
        """构建帖子Payload"""
        # 解析图片URL
        image_urls = post.get('image_urls', [])
        if isinstance(image_urls, str):
            try:
                image_urls = json.loads(image_urls)
            except:
                image_urls = []

        # 解析标签
        tags = post.get('tags', '')
        if isinstance(tags, str):
            tags = re.findall(r'([^,\[\]]+)\[话题\]', tags)
            if not tags:
                tags = [t.strip() for t in tags.split(',') if t.strip()]
        elif not isinstance(tags, list):
            tags = []

        return PostPayload(
            post_id=post.get('id', ''),
            title=post.get('title', ''),
            content=post.get('content', post.get('desc', '')),
            tags=tags,
            credibility=credibility_score.final_score,
            publish_time=self._parse_publish_time(post.get('publish_time')),
            image_count=len(image_urls),
            image_urls=image_urls[:10] if image_urls else [],  # 限制存储数量
            ocr_summary=post.get('ocr_summary', ''),
            keyword=post.get('keyword', '')
        )

    def _parse_publish_time(self, time_val) -> Optional[datetime]:
        """解析发布时间"""
        if not time_val:
            return None

        if isinstance(time_val, datetime):
            return time_val

        if isinstance(time_val, (int, float)):
            try:
                return datetime.fromtimestamp(time_val)
            except:
                pass

        if isinstance(time_val, str):
            try:
                return datetime.fromisoformat(time_val)
            except:
                pass

        return None

    async def import_from_directory(
        self,
        directory: str
    ) -> Dict[str, ImportResult]:
        """
        从目录导入所有JSON文件

        Args:
            directory: 目录路径

        Returns:
            每个文件的导入结果
        """
        results = {}
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.error(f"目录不存在: {directory}")
            return results

        json_files = list(dir_path.glob("*.json"))
        logger.info(f"发现 {len(json_files)} 个JSON文件")

        for json_file in json_files:
            result = await self.import_from_json_file(str(json_file))
            results[json_file.name] = result

        return results


async def import_rag_data(
    data_dir: str,
    config: Optional[ImportConfig] = None
) -> Dict[str, ImportResult]:
    """
    导入RAG数据的便捷函数

    Args:
        data_dir: 数据目录
        config: 导入配置

    Returns:
        导入结果
    """
    importer = RAGDataImporter(config)
    await importer.initialize()
    return await importer.import_from_directory(data_dir)
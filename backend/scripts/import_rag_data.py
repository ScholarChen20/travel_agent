#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG数据导入脚本（优化版）
功能：将小红书爬取的旅行数据导入到Qdrant向量数据库

优化点：
1. 图片ID使用 {post_id}_{image_idx} 格式，避免覆盖
2. 添加置信度评分计算
3. 支持稀疏向量
4. 更好的错误处理和进度显示

数据格式：
- id: 帖子ID
- title: 标题
- desc: 正文描述
- image_urls: 图片URL数组
- tags: 标签

使用方法:
    python scripts/import_rag_data.py [--data-dir DATA_DIR] [--skip-images]
"""

import asyncio
import argparse
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)
logger.add(
    logs_dir / "rag_import_{time}.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
    encoding="utf-8"
)


class RAGDataImporter:
    """RAG数据导入器（优化版）"""

    def __init__(
        self,
        data_dir: str,
        batch_size: int = 20,
        skip_images: bool = False,
        skip_low_credibility: bool = True,
        credibility_threshold: float = 0.3,  # 降低阈值，更多数据入库
        max_images_per_post: int = 8
    ):
        self.data_dir = Path(data_dir)
        self.batch_size = batch_size
        self.skip_images = skip_images
        self.skip_low_credibility = skip_low_credibility
        self.credibility_threshold = credibility_threshold
        self.max_images_per_post = max_images_per_post

        # 服务实例
        self.vector_store = None
        self.embedding_service = None
        self.credibility_calculator = None

        # 统计
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_posts': 0,
            'indexed_posts': 0,
            'skipped_posts': 0,
            'indexed_images': 0,
            'failed_images': 0,
            'errors': [],
            'start_time': None,
            'end_time': None
        }

    async def initialize(self):
        """初始化服务"""
        logger.info("正在初始化服务...")

        try:
            # 初始化混合向量存储
            from app.services.rag.hybrid_vector_store import get_hybrid_vector_store
            self.vector_store = await get_hybrid_vector_store()

            # 初始化向量化服务
            from app.services.rag.embedding_service import get_embedding_service
            self.embedding_service = get_embedding_service()

            # 初始化置信度计算器
            from app.services.rag.credibility_calculator import CredibilityCalculator
            self.credibility_calculator = CredibilityCalculator(
                credibility_threshold=self.credibility_threshold
            )

            # 健康检查
            health = await self.vector_store.health_check()
            logger.info(f"向量存储状态: {health['status']}")

            stats = self.vector_store.get_collection_stats()
            logger.info(f"当前数据量: posts={stats.get('posts', {}).get('count', 0)}, images={stats.get('images', {}).get('count', 0)}")

        except Exception as e:
            logger.error(f"服务初始化失败: {e}")
            raise

    def scan_data_files(self) -> List[Path]:
        """扫描数据文件"""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"数据目录不存在: {self.data_dir}")

        json_files = list(self.data_dir.glob("*.json"))
        valid_files = [f for f in json_files if f.stat().st_size > 0]

        self.stats['total_files'] = len(valid_files)
        logger.info(f"发现 {len(valid_files)} 个JSON文件")

        return valid_files

    def parse_json_file(self, file_path: Path) -> List[Dict]:
        """解析JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                logger.warning(f"JSON格式错误: {file_path.name}")
                return []

            posts = []
            for item in data:
                # 解析图片URL
                image_urls = item.get('image_urls', [])
                if isinstance(image_urls, str):
                    try:
                        image_urls = json.loads(image_urls)
                    except:
                        image_urls = []

                # 解析标签
                tags = item.get('tags', '')
                if isinstance(tags, str):
                    tags = re.findall(r'([^,\[\]]+)\[话题\]', tags)
                    if not tags:
                        tags = [t.strip() for t in tags.split(',') if t.strip()]
                elif not isinstance(tags, list):
                    tags = []

                post = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'desc': item.get('desc', ''),
                    'content': item.get('content', item.get('desc', '')),
                    'image_urls': image_urls,
                    'tags': tags,
                    'image_count': len(image_urls)
                }

                if post['id'] and post['title']:
                    posts.append(post)

            return posts

        except Exception as e:
            logger.error(f"解析文件失败: {file_path.name}, 错误: {e}")
            return []

    def calculate_credibility(self, post: Dict) -> float:
        """计算帖子置信度"""
        score_input = {
            'is_verified': post.get('is_verified', False),
            'followers': post.get('followers', 1000),
            'report_rate': post.get('report_rate', 0.02),
            'images': post.get('image_urls', []),
            'image_count': post.get('image_count', 0),
            'desc': post.get('desc', ''),
            'likes': post.get('likes', 100),
            'collects': post.get('collects', 50),
            'comments': post.get('comments', 10),
        }

        score = self.credibility_calculator.calculate(score_input)
        return score.final_score

    def generate_sparse_vector(self, text: str) -> Dict[int, float]:
        """生成稀疏向量（使用hashlib确保跨进程一致性）"""
        import hashlib

        words = re.findall(r'\w+', text.lower())
        word_freq = {}
        for word in words:
            word_hash = int(hashlib.md5(word.encode()).hexdigest()[:8], 16) % 100000
            word_freq[word_hash] = word_freq.get(word_hash, 0) + 1

        if not word_freq:
            return {}

        max_freq = max(word_freq.values())
        return {k: v / max_freq for k, v in word_freq.items()}

    async def import_file(self, file_path: Path) -> Dict:
        """导入单个文件"""
        result = {
            'file': file_path.name,
            'posts_total': 0,
            'posts_indexed': 0,
            'posts_skipped': 0,
            'images_indexed': 0,
            'images_failed': 0,
            'errors': []
        }

        logger.info(f"处理文件: {file_path.name}")
        city = file_path.stem.replace("旅游", "").replace("攻略", "")

        # 解析文件
        posts = self.parse_json_file(file_path)
        result['posts_total'] = len(posts)
        self.stats['total_posts'] += len(posts)

        if not posts:
            return result

        # 批量处理帖子
        posts_to_insert = []
        vectorization_failed = 0

        for post in posts:
            try:
                # 计算置信度
                credibility = self.calculate_credibility(post)

                # 跳过低置信度
                if self.skip_low_credibility and credibility < self.credibility_threshold:
                    result['posts_skipped'] += 1
                    continue

                # 构建增强文本
                enriched_text = f"{post['title']} {post['desc']} {' '.join(post['tags'])}"

                # 向量化
                dense_vector = None
                if self.embedding_service:
                    try:
                        emb_result = await self.embedding_service.embed_text(enriched_text)
                        if emb_result.success:
                            dense_vector = emb_result.embedding
                    except Exception as e:
                        logger.warning(f"文本向量化失败: {post['id']}, {e}")

                # 如果向量化失败，跳过该帖子
                if not dense_vector:
                    logger.debug(f"跳过无向量的帖子: {post['id']}")
                    vectorization_failed += 1
                    continue

                # 稀疏向量
                sparse_vector = self.generate_sparse_vector(enriched_text)

                # 构建payload
                payload = {
                    'post_id': post['id'],
                    'title': post['title'],
                    'content': post['content'] or post['desc'],
                    'desc': post['desc'],
                    'tags': post['tags'],
                    'credibility': credibility,
                    'image_count': post['image_count'],
                    'image_urls': post['image_urls'],  # 限制存储
                    'city': city
                }

                posts_to_insert.append({
                    'post_id': post['id'],
                    'dense_vector': dense_vector,
                    'sparse_vector': sparse_vector,
                    'payload': payload
                })

            except Exception as e:
                result['errors'].append(f"处理帖子失败: {post['id']}, {e}")

        # 记录向量化失败数
        if vectorization_failed > 0:
            logger.info(f"向量化失败跳过: {vectorization_failed} 条")

        # 批量插入帖子
        if posts_to_insert:
            inserted = await self.vector_store.upsert_posts_batch(posts_to_insert)
            result['posts_indexed'] = inserted
            self.stats['indexed_posts'] += inserted

        # 图片向量化
        if not self.skip_images:
            for post in posts:
                image_urls = post.get('image_urls', [])
                if not image_urls:
                    continue

                post_id = post['id']
                indexed, failed = await self._index_images(
                    post_id=post_id,
                    image_urls=image_urls[:self.max_images_per_post],
                    title=post['title'],
                    city=city
                )

                result['images_indexed'] += indexed
                result['images_failed'] += failed

                # 避免API限流
                if indexed > 0:
                    await asyncio.sleep(0.3)

        self.stats['skipped_posts'] += result['posts_skipped']
        self.stats['indexed_images'] += result['images_indexed']
        self.stats['failed_images'] += result['images_failed']

        logger.info(
            f"文件完成: {file_path.name} - "
            f"帖子={result['posts_indexed']}/{result['posts_total']}, "
            f"图片={result['images_indexed']}"
        )

        return result

    async def _index_images(
        self,
        post_id: str,
        image_urls: List[str],
        title: str,
        city: str
    ) -> tuple:
        """索引帖子图片（每张图片独立ID）"""
        indexed = 0
        failed = 0

        for idx, img_url in enumerate(image_urls):
            try:
                # 关键：使用 {post_id}_{idx} 作为唯一ID
                image_id = f"{post_id}_{idx}"

                # 向量化图片
                img_result = await self.embedding_service.embed_image(img_url)

                if img_result and img_result.embedding:
                    await self.vector_store.upsert_image(
                        post_id=post_id,
                        image_idx=idx,
                        dense_vector=img_result.embedding,
                        payload={
                            'post_id': post_id,
                            'image_idx': idx,
                            'image_url': img_url,
                            'title': title,
                            'city': city
                        }
                    )
                    indexed += 1
                else:
                    failed += 1

            except Exception as e:
                logger.debug(f"图片向量化失败: {img_url[:50]}..., {e}")
                failed += 1

        return indexed, failed

    async def import_all(self) -> Dict:
        """导入所有数据"""
        self.stats['start_time'] = datetime.now()

        logger.info("=" * 60)
        logger.info("RAG数据导入（优化版）")
        logger.info(f"数据目录: {self.data_dir}")
        logger.info(f"跳过图片: {self.skip_images}")
        logger.info(f"置信度阈值: {self.credibility_threshold}")
        logger.info("=" * 60)

        await self.initialize()

        files = self.scan_data_files()
        if not files:
            logger.warning("没有找到数据文件")
            return self.stats

        for i, file_path in enumerate(files, 1):
            logger.info(f"\n[{i}/{len(files)}] {file_path.name}")

            try:
                result = await self.import_file(file_path)
                self.stats['processed_files'] += 1
            except Exception as e:
                logger.error(f"处理失败: {file_path.name}, {e}")
                self.stats['errors'].append({
                    'file': file_path.name,
                    'error': str(e)
                })

            if i < len(files):
                await asyncio.sleep(1)

        self.stats['end_time'] = datetime.now()
        self._print_summary()

        return self.stats

    def _print_summary(self):
        """打印摘要"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        logger.info("\n" + "=" * 60)
        logger.info("导入完成")
        logger.info("=" * 60)
        logger.info(f"处理文件: {self.stats['processed_files']}/{self.stats['total_files']}")
        logger.info(f"帖子总数: {self.stats['total_posts']}")
        logger.info(f"索引帖子: {self.stats['indexed_posts']}")
        logger.info(f"跳过帖子: {self.stats['skipped_posts']}")
        logger.info(f"索引图片: {self.stats['indexed_images']}")
        logger.info(f"失败图片: {self.stats['failed_images']}")
        logger.info(f"总耗时: {duration:.2f}秒")

        if self.stats['indexed_posts'] > 0:
            logger.info(f"平均每帖: {duration/self.stats['indexed_posts']:.3f}秒")

        if self.stats['errors']:
            logger.warning(f"\n错误数: {len(self.stats['errors'])}")

        logger.info("=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="RAG数据导入脚本（优化版）")
    parser.add_argument("--data-dir", default="data/rag_data", help="数据目录")
    parser.add_argument("--batch-size", type=int, default=20, help="批处理大小")
    parser.add_argument("--skip-images", action="store_true", help="跳过图片导入")
    parser.add_argument("--credibility-threshold", type=float, default=0.3, help="置信度阈值")

    args = parser.parse_args()
    data_dir = Path(project_root) / args.data_dir

    importer = RAGDataImporter(
        data_dir=str(data_dir),
        batch_size=args.batch_size,
        skip_images=args.skip_images,
        credibility_threshold=args.credibility_threshold
    )

    try:
        await importer.import_all()
    except KeyboardInterrupt:
        logger.warning("\n用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"导入失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
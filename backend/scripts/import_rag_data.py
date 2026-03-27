#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG数据导入脚本
功能：将小红书爬取的旅行数据导入到Qdrant向量数据库

使用方法:
    python scripts/import_rag_data.py [--data-dir DATA_DIR] [--batch-size BATCH_SIZE]

示例:
    python scripts/import_rag_data.py
    python scripts/import_rag_data.py --data-dir backend/data/rag_data --batch-size 20
"""

import asyncio
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    project_root / "logs" / "rag_import_{time}.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
    encoding="utf-8"
)


class RAGDataImporter:
    """RAG数据导入器"""
    
    def __init__(
        self,
        data_dir: str,
        batch_size: int = 20,
        max_concurrent: int = 5
    ):
        """
        初始化导入器
        
        Args:
            data_dir: 数据目录路径
            batch_size: 批处理大小
            max_concurrent: 最大并发数
        """
        self.data_dir = Path(data_dir)
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        
        self.rag_service = None
        self.data_processor = None
        
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_posts': 0,
            'cleaned_posts': 0,
            'indexed_posts': 0,
            'failed_posts': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }
    
    async def initialize(self):
        """初始化服务"""
        logger.info("正在初始化RAG服务...")
        
        try:
            from app.services.rag import (
                RAGService,
                RAGConfig,
                DataProcessor
            )
            
            config = RAGConfig(
                batch_index_size=self.batch_size,
                max_concurrent_indexing=self.max_concurrent
            )
            
            self.rag_service = await RAGService.get_instance(config)
            self.data_processor = DataProcessor()
            
            health = await self.rag_service.health_check()
            logger.info(f"RAG服务健康状态: {health['status']}")
            
            if health['status'] == 'error':
                raise RuntimeError(f"RAG服务初始化失败: {health.get('errors', [])}")
            
            logger.info("RAG服务初始化成功")
            
        except Exception as e:
            logger.error(f"初始化RAG服务失败: {e}")
            raise
    
    def scan_data_files(self) -> List[Path]:
        """扫描数据文件"""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"数据目录不存在: {self.data_dir}")
        
        json_files = list(self.data_dir.glob("*.json"))
        
        valid_files = []
        for f in json_files:
            if f.stat().st_size > 0:
                valid_files.append(f)
            else:
                logger.warning(f"跳过空文件: {f.name}")
        
        self.stats['total_files'] = len(valid_files)
        logger.info(f"发现 {len(valid_files)} 个有效JSON文件")
        
        return valid_files
    
    def load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'posts' in data:
                    return data['posts']
                elif 'data' in data:
                    return data['data']
                else:
                    return [data]
            else:
                logger.warning(f"未知数据格式: {file_path.name}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {file_path.name}, 错误: {e}")
            self.stats['errors'].append({
                'file': str(file_path),
                'error': f"JSON解析失败: {e}"
            })
            return []
        except Exception as e:
            logger.error(f"读取文件失败: {file_path.name}, 错误: {e}")
            self.stats['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return []
    
    async def import_file(self, file_path: Path) -> Dict[str, Any]:
        """
        导入单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            导入结果
        """
        result = {
            'file': file_path.name,
            'raw_count': 0,
            'cleaned_count': 0,
            'indexed_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        logger.info(f"开始处理文件: {file_path.name}")
        
        raw_posts = self.load_json_file(file_path)
        result['raw_count'] = len(raw_posts)
        
        if not raw_posts:
            logger.warning(f"文件无有效数据: {file_path.name}")
            return result
        
        self.stats['total_posts'] += len(raw_posts)
        
        cleaned_posts = self.data_processor.clean_posts_batch(raw_posts)
        result['cleaned_count'] = len(cleaned_posts)
        self.stats['cleaned_posts'] += len(cleaned_posts)
        
        if not cleaned_posts:
            logger.warning(f"清洗后无有效数据: {file_path.name}")
            return result
        
        logger.info(f"清洗完成: {len(cleaned_posts)}/{len(raw_posts)} 条有效")
        
        try:
            index_result = await self.rag_service.index_posts_batch(
                cleaned_posts,
                progress_callback=lambda p: logger.debug(f"索引进度: {p['progress_percent']:.1f}%")
            )
            
            result['indexed_count'] = index_result['success']
            result['failed_count'] = index_result['failed']
            
            self.stats['indexed_posts'] += index_result['success']
            self.stats['failed_posts'] += index_result['failed']
            
            logger.info(
                f"索引完成: 成功 {index_result['success']}, "
                f"失败 {index_result['failed']}"
            )
            
        except Exception as e:
            logger.error(f"索引失败: {file_path.name}, 错误: {e}")
            result['errors'].append(str(e))
            self.stats['errors'].append({
                'file': file_path.name,
                'error': str(e)
            })
        
        return result
    
    async def import_all(self) -> Dict[str, Any]:
        """
        导入所有数据
        
        Returns:
            导入结果汇总
        """
        self.stats['start_time'] = datetime.now()
        logger.info("=" * 60)
        logger.info("开始RAG数据导入")
        logger.info(f"数据目录: {self.data_dir}")
        logger.info(f"批处理大小: {self.batch_size}")
        logger.info(f"最大并发数: {self.max_concurrent}")
        logger.info("=" * 60)
        
        await self.initialize()
        
        files = self.scan_data_files()
        
        if not files:
            logger.warning("没有找到可导入的数据文件")
            return self.stats
        
        file_results = []
        
        for i, file_path in enumerate(files, 1):
            logger.info(f"\n处理进度: [{i}/{len(files)}] {file_path.name}")
            
            try:
                result = await self.import_file(file_path)
                file_results.append(result)
                self.stats['processed_files'] += 1
                
            except Exception as e:
                logger.error(f"处理文件失败: {file_path.name}, 错误: {e}")
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
        """打印导入摘要"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("RAG数据导入完成")
        logger.info("=" * 60)
        logger.info(f"处理文件数: {self.stats['processed_files']}/{self.stats['total_files']}")
        logger.info(f"原始帖子数: {self.stats['total_posts']}")
        logger.info(f"清洗后帖子数: {self.stats['cleaned_posts']}")
        logger.info(f"成功索引帖子数: {self.stats['indexed_posts']}")
        logger.info(f"失败帖子数: {self.stats['failed_posts']}")
        logger.info(f"总耗时: {duration:.2f} 秒")
        
        if self.stats['indexed_posts'] > 0:
            avg_time = duration / self.stats['indexed_posts']
            logger.info(f"平均每条: {avg_time:.3f} 秒")
        
        if self.stats['errors']:
            logger.warning(f"\n错误数: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:
                logger.warning(f"  - {error}")
        
        logger.info("=" * 60)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="RAG数据导入脚本 - 将小红书数据导入向量数据库"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="backend/data/rag_data",
        help="数据目录路径 (默认: backend/data/rag_data)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="批处理大小 (默认: 20)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="最大并发数 (默认: 5)"
    )
    
    args = parser.parse_args()
    
    data_dir = Path(project_root) / args.data_dir
    
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    importer = RAGDataImporter(
        data_dir=str(data_dir),
        batch_size=args.batch_size,
        max_concurrent=args.max_concurrent
    )
    
    try:
        await importer.import_all()
    except KeyboardInterrupt:
        logger.warning("\n用户中断导入")
        sys.exit(1)
    except Exception as e:
        logger.error(f"导入失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

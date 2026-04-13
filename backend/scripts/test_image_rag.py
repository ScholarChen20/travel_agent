#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试图片服务RAG兜底功能
"""

import asyncio
import sys
import re
import unittest
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置控制台编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def remove_emoji(text: str) -> str:
    """移除emoji字符"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


class TestImageRAG(unittest.TestCase):
    """测试图片服务RAG兜底功能"""

    def test_get_fallback_images(self):
        """测试从RAG获取图片"""
        # 使用 asyncio.run 或 get_event_loop 来运行异步代码
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(self._test_get_fallback_images())

    async def _test_get_fallback_images(self):
        """异步测试方法"""
        print("=" * 60)
        print("图片服务RAG兜底测试")
        print("=" * 60)

        from app.services.image_service import get_image_service

        image_service = get_image_service()
        print("[OK] 图片服务初始化成功")

        # 测试从RAG获取图片
        test_cases = [
            {"attraction": "故宫", "city": "北京"},
            {"attraction": "外滩", "city": "上海"},
            {"attraction": "厦门大学", "city": "厦门"},
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"测试 {i}: {test['city']} - {test['attraction']}")
            print("=" * 60)

            try:
                images = await image_service._get_fallback_images_from_rag(
                    attraction_name=test["attraction"],
                    city=test["city"]
                )

                print(f"找到 {len(images)} 张图片:")
                for j, url in enumerate(images, 1):
                    # 截断URL显示
                    short_url = url[:100] + "..." if len(url) > 60 else url
                    print(f"  [{j}] {short_url}")

                # 断言：应该返回图片列表
                self.assertIsInstance(images, list)

            except Exception as e:
                print(f"[ERROR] 测试失败: {str(e)}")
                self.fail(f"测试失败: {str(e)}")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


if __name__ == "__main__":
    # 直接运行时使用 asyncio.run
    asyncio.run(TestImageRAG()._test_get_fallback_images())
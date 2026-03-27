#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书热门帖子爬虫 - 支持关键词搜索
使用网页抓取方式，绕过API认证限制

**使用方法**:
1. 安装依赖: pip install httpx beautifulsoup4
2. 运行: python xiaohongshu_scraper_httpx.py "关键词"
"""

import httpx
import json
import time
import random
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class XiaohongshuScraper:
    def __init__(self):
        self.client = httpx.Client(
            follow_redirects=True,
            timeout=15
        )
        # 模拟完整浏览器请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }
        self.client.headers.update(self.headers)

    def search_hot_posts(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        搜索指定关键词的热门帖子
        通过搜索页面网页抓取
        """
        url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"

        try:
            time.sleep(random.uniform(1, 2))

            response = self.client.get(url)
            response.raise_for_status()

            # 从网页中提取初始数据
            posts = self._extract_from_html(response.text, limit)

            if not posts:
                print("[WARNING] No posts extracted from page")
                return []

            print(f"[INFO] Extracted {len(posts)} posts from search page")
            return posts

        except Exception as e:
            print(f"[ERROR] Search failed: {str(e)}")
            return []

    def _extract_from_html(self, html: str, limit: int) -> List[Dict]:
        """从HTML页面提取帖子信息"""
        # 尝试从window.__INITIAL_STATE__提取数据
        pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});?\s*</script>'
        match = re.search(pattern, html, re.DOTALL)

        posts = []

        if match:
            try:
                import json
                data = json.loads(match.group(1))

                # 搜索结果在不同位置
                # 尝试多种路径
                search_result = None
                paths = [
                    ('searchResult', 'notes'),
                    ('SearchResult', 'notes'),
                    ('noteList', 'list'),
                ]

                for path1, path2 in paths:
                    if path1 in data and path2 in data[path1]:
                        search_result = data[path1][path2]
                        break

                if search_result and isinstance(search_result, list):
                    for item in search_result[:limit]:
                        post = self._format_post(item)
                        if post:
                            posts.append(post)

            except Exception as e:
                print(f"[WARNING] Failed to parse initial state: {e}")

        # 如果JSON提取失败，尝试BeautifulSoup解析DOM
        if not posts:
            posts = self._extract_from_soup(html, limit)

        return posts[:limit]

    def _format_post(self, item: Dict) -> Optional[Dict]:
        """格式化帖子数据"""
        try:
            # 不同页面结构兼容
            post_id = item.get('noteId', item.get('note_id', item.get('id', '')))
            if not post_id:
                return None

            title = item.get('title', item.get('desc', ''))
            desc = item.get('desc', item.get('content', ''))
            likes = item.get('likeCount', item.get('like_count', item.get('likes', 0)))
            comments = item.get('commentCount', item.get('comment_count', item.get('comments', 0)))
            collects = item.get('collectCount', item.get('collect_count', 0))

            # 作者信息
            user = item.get('user', item.get('author', {}))
            if isinstance(user, dict):
                author_name = user.get('nickname', user.get('nickName', ''))
                author_id = user.get('userId', user.get('user_id', ''))
            else:
                author_name = ''
                author_id = ''

            # 图片
            if 'cover' in item:
                cover = item['cover']
                if isinstance(cover, dict):
                    image_url = cover.get('url', cover.get('imageUrl', ''))
                else:
                    image_url = cover
            elif 'imageList' in item and item['imageList']:
                image_url = item['imageList'][0].get('url', '')
            else:
                image_url = ''

            if image_url and not image_url.startswith('http'):
                image_url = 'https:' + image_url

            post_url = f"https://www.xiaohongshu.com/discovery/item/{post_id}"

            # 标签
            tags = []
            if 'tags' in item:
                tags = [t.get('name', t) if isinstance(t, dict) else t for t in item['tags']]

            return {
                'post_id': str(post_id),
                'title': str(title).strip(),
                'description': str(desc).strip(),
                'author_name': str(author_name).strip(),
                'author_id': str(author_id),
                'likes': int(likes),
                'comments': int(comments),
                'collects': int(collects),
                'cover_image_url': image_url,
                'post_url': post_url,
                'tags': tags,
            }

        except Exception as e:
            print(f"[WARNING] Failed to format post: {e}")
            return None

    def _extract_from_soup(self, html: str, limit: int) -> List[Dict]:
        """使用BeautifulSoup从DOM提取"""
        soup = BeautifulSoup(html, 'html.parser')
        posts = []

        # 查找帖子卡片
        cards = soup.select('.note-item')[:limit]

        for card in cards:
            try:
                title_elem = card.select_one('.title')
                title = title_elem.get_text().strip() if title_elem else ''

                link_elem = card.select_one('a')
                post_url = link_elem.get('href') if link_elem else ''
                post_id = post_url.split('/')[-1] if post_url else ''

                author_elem = card.select_one('.author-name')
                author_name = author_elem.get_text().strip() if author_elem else ''

                likes_elem = card.select_one('.like-count')
                likes = int(likes_elem.get_text().strip()) if likes_elem else 0

                img_elem = card.select_one('img')
                image_url = img_elem.get('src') if img_elem else ''
                if image_url and not image_url.startswith('http'):
                    image_url = 'https:' + image_url

                posts.append({
                    'post_id': post_id,
                    'title': title,
                    'description': '',
                    'author_name': author_name,
                    'author_id': '',
                    'likes': likes,
                    'comments': 0,
                    'collects': 0,
                    'cover_image_url': image_url,
                    'post_url': f"https://www.xiaohongshu.com{post_url}" if post_url else '',
                    'tags': [],
                })

            except Exception:
                continue

        return posts

    def get_post_detail(self, post_id: str) -> Optional[Dict]:
        """获取帖子详情"""
        url = f"https://www.xiaohongshu.com/discovery/item/{post_id}"

        try:
            time.sleep(random.uniform(1, 2))
            response = self.client.get(url)
            response.raise_for_status()

            posts = self._extract_from_html(response.text, 1)
            if posts:
                return posts[0]
            return None

        except Exception as e:
            print(f"[ERROR] Get detail failed: {e}")
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='小红书热门帖子爬虫 - 网页抓取版')
    parser.add_argument('keyword', nargs='?', help='搜索关键词', default=None)
    parser.add_argument('--limit', '-l', type=int, default=20, help='返回结果数量')
    parser.add_argument('--output', '-o', help='输出JSON文件路径')

    args = parser.parse_args()

    if not args.keyword:
        print("请提供搜索关键词！例如: python xiaohongshu_scraper_httpx.py \"正能量\"")
        print("\n可选示例:")
        print("  python xiaohongshu_scraper_httpx.py \"健身\" --limit 10")
        print("  python xiaohongshu_scraper_httpx.py \"美食\" --limit 20 --output result.json")
        return

    scraper = XiaohongshuScraper()
    print(f"正在搜索关键词「{args.keyword}」的热门帖子...\n")

    posts = scraper.search_hot_posts(args.keyword, limit=min(args.limit, 50))

    print(f"抓取完成！共获取 {len(posts)} 条帖子\n")

    # 打印结果概要
    for i, post in enumerate(posts, 1):
        title = post['title'][:30] + ('...' if len(post['title']) > 30 else '')
        print(f"{i}. {title}")
        print(f"   作者: {post['author_name'] or '-'} | 点赞: {post['likes']}")
        print(f"   链接: {post['post_url']}\n")

    # 输出JSON文件
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"完整数据已保存到: {args.output}")
    else:
        if posts:
            print("\n=== 完整JSON数据 ===")
            print(json.dumps(posts, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
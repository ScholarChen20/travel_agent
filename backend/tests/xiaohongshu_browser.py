#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爬虫 - 使用 DrissionPage 浏览器自动化
========================================
功能:
- 支持关键词搜索
- 获取详细帖子信息（标题、描述、作者、点赞、评论、收藏）
- 提取帖子内所有图片并下载保存
- 支持翻页爬取
"""

from DrissionPage import ChromiumPage
from urllib.parse import quote
import json
import time
import random
import os
import re
import requests
from tqdm import tqdm


# ========== 配置区域 ==========
# 在这里粘贴你的Cookie
COOKIE = """
# 示例:
# a1=xxx; xsecappid=xxx; ...
"""

# 图片保存目录
IMAGE_DIR = "xiaohongshu_images"

# 调试模式：打印页面结构
DEBUG = True
# ============================


def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def download_image(url, save_path, timeout=10):
    """下载单张图片"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"[WARNING] 下载失败: {url} - {e}")
    return False


def extract_post_id(url):
    """从URL提取帖子ID"""
    if not url:
        return None
    # URL格式: https://www.xiaohongshu.com/explore/xxx 或 /discovery/item/xxx
    match = re.search(r'/explore/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    match = re.search(r'/item/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None


def get_post_detail(page, post_url):
    """
    进入帖子详情页，获取更详细的信息和所有图片

    Returns:
        dict: 包含详细信息的字典
    """
    detail = {
        'images': [],          # 所有图片URL列表
        'description': '',     # 帖子正文/描述
        'tags': [],            # 话题标签
        'location': '',        # 定位地点
        'created_at': '',      # 发布时间
    }

    try:
        # 打开新标签页访问帖子
        page.get(post_url)
        time.sleep(2)  # 等待页面加载

        # 获取帖子正文/描述 - 尝试多种选择器
        desc_selectors = ['.desc', '.note-content', '.content', '.text', '.note-text']
        for sel in desc_selectors:
            desc_elem = page.ele(sel, timeout=2)
            if desc_elem and desc_elem.text:
                detail['description'] = desc_elem.text
                break

        # 获取话题标签
        tag_selectors = ['.tag', '.topic', '.hash-tag', '.tag-item']
        for sel in tag_selectors:
            tag_elems = page.eles(sel, timeout=2)
            if tag_elems:
                detail['tags'] = [tag.text for tag in tag_elems if tag.text and tag.text.startswith('#')]
                if detail['tags']:
                    break

        # 获取定位信息
        loc_selectors = ['.location', '.address', '.geo', '.position']
        for sel in loc_selectors:
            location_elem = page.ele(sel, timeout=2)
            if location_elem and location_elem.text:
                detail['location'] = location_elem.text
                break

        # 获取发布时间
        time_selectors = ['.date', '.time', '.publish-time', '.created-at']
        for sel in time_selectors:
            time_elem = page.ele(sel, timeout=2)
            if time_elem and time_elem.text:
                detail['created_at'] = time_elem.text
                break

        # 获取所有图片 - 从img标签中提取
        img_elems = page.eles('tag:img', timeout=3)
        for img in img_elems:
            try:
                src = img.attr('src') or img.attr('data-src')
                if src:
                    # 过滤掉头像、图标等小图和无效URL
                    lower_src = src.lower()
                    if any(x in lower_src for x in ['xiaohongshu.com', 'cdn', 'hdslb', 'aliimg']) and \
                       'avatar' not in lower_src and 'icon' not in lower_src and 'logo' not in lower_src:
                        if src not in detail['images']:
                            detail['images'].append(src)
            except:
                continue

        # 如果图片列表为空，尝试从 background-image 或其他方式获取
        if not detail['images']:
            # 尝试获取封面元素
            cover_selectors = ['.cover-img', '.cover image', '.main-image', '.note-cover']
            for sel in cover_selectors:
                cover_elem = page.ele(sel, timeout=2)
                if cover_elem:
                    src = cover_elem.attr('src') or cover_elem.attr('data-src')
                    if src:
                        detail['images'].append(src)
                        break

        if DEBUG:
            print(f"[DEBUG] 详情页获取 - 图片: {len(detail['images'])}张, 描述长度: {len(detail['description'])}")

    except Exception as e:
        print(f"[WARNING] 获取详情失败: {e}")

    return detail


def debug_page_structure(page, page_num=1):
    """调试：打印页面结构，帮助找出正确的选择器"""
    if not DEBUG:
        return

    # 只在第一页打印详细调试信息
    if page_num > 1:
        return

    print("\n========== 页面结构调试 ==========")

    # 打印页面标题
    try:
        title = page.title
        print(f"页面标题: {title}")
    except:
        pass

    # 打印页面URL
    print(f"页面URL: {page.url}")

    # 尝试各种选择器
    selectors = [
        '.note-item', '.feed-list .item', '.notes .note',
        '.item', '.note-card', '.feed-item', '.note',
        '[class*="note"]', '[class*="feed"]', '[class*="item"]'
    ]

    for sel in selectors:
        try:
            elems = page.eles(sel)
            if elems:
                print(f"  {sel}: 找到 {len(elems)} 个元素")
        except Exception as e:
            print(f"  {sel}: 错误 - {e}")

    # 尝试获取页面中所有的 class 名
    try:
        # 获取 body 下的直接子元素
        body = page.ele('tag:body')
        if body:
            divs = body.eles('tag:div')
            classes = set()
            for d in divs[:50]:  # 只检查前50个
                cls = d.attr('class')
                if cls:
                    classes.add(cls)
            if classes:
                print(f"\n  页面包含的class (前20个):")
                for c in list(classes)[:20]:
                    print(f"    .{c}")
    except:
        pass

    print("===================================\n")


def parse_page(page, get_detail=False, page_num=1):
    """
    解析当前页面的笔记数据

    Args:
        page: ChromiumPage对象
        get_detail: 是否获取每个帖子的详细信息和图片
        page_num: 页码（用于调试）
    """
    posts = []

    # 调试模式：打印页面结构
    debug_page_structure(page, page_num)

    try:
        # 定位笔记列表容器 - 尝试多种选择器
        container = page.eles('.note-item')
        if not container:
            container = page.eles('.feed-list .item')
        if not container:
            container = page.eles('.notes .note')
        if not container:
            container = page.eles('.item')

        if DEBUG and page_num == 1:
            print(f"找到 {len(container)} 个笔记元素")
            # 打印第一个元素的完整HTML，帮助调试
            if container:
                try:
                    first = container[0]
                    html = first.html
                    print(f"\n========== 第一个元素HTML ==========")
                    print(html)
                    print("==================================================\n")
                except Exception as e:
                    print(f"[DEBUG] 获取HTML失败: {e}")

        for idx, item in enumerate(container):
            try:
                post = {}

                # ============ 基本信息 ============
                # 获取笔记链接 - 从 .cover 元素获取
                cover_elem = item.ele('.cover', timeout=0)
                if cover_elem:
                    post['url'] = 'https://www.xiaohongshu.com' + cover_elem.attr('href')
                else:
                    # 备用：从 a 标签获取
                    link_elem = item.ele('tag:a', timeout=0)
                    if link_elem:
                        post['url'] = link_elem.attr('href') or link_elem.attr('link')

                # 提取post_id（从URL中）
                post['post_id'] = extract_post_id(post.get('url', ''))

                # 获取标题 - 从 .title span 获取
                title_elem = item.ele('.title span', timeout=0)
                if not title_elem:
                    title_elem = item.ele('.title', timeout=0)
                if title_elem:
                    post['title'] = title_elem.text
                else:
                    post['title'] = ''

                # 获取描述/正文 - 搜索结果页不显示正文，需要进详情页
                post['description'] = ''

                # ============ 作者信息 ============
                # 作者信息在 .author 元素中
                author_elem = item.ele('.author', timeout=0)
                if author_elem:
                    # 作者昵称 - .name
                    name_elem = author_elem.ele('.name', timeout=0)
                    post['author_name'] = name_elem.text if name_elem else ''

                    # 作者头像 - .author-avatar
                    avatar_elem = author_elem.ele('.author-avatar', timeout=0)
                    if avatar_elem:
                        post['author_avatar'] = avatar_elem.attr('src') or ''

                    # 发布时间 - .time
                    time_elem = author_elem.ele('.time', timeout=0)
                    if time_elem:
                        post['created_at'] = time_elem.text
                else:
                    post['author_name'] = ''
                    post['author_avatar'] = ''

                # ============ 互动数据 ============
                # 点赞数 - 从 .like-wrapper .count 获取
                like_wrapper = item.ele('.like-wrapper', timeout=0)
                if like_wrapper:
                    count_elem = like_wrapper.ele('.count', timeout=0)
                    post['likes'] = count_elem.text.strip() if count_elem else '0'
                else:
                    post['likes'] = '0'

                # 评论数和收藏数 - 搜索结果页可能不直接显示，需要进详情页
                post['comments'] = '0'
                post['collects'] = '0'

                # ============ 封面图片 ============
                # 从 .cover 元素内获取 img 标签
                cover_elem = item.ele('.cover', timeout=0)
                if cover_elem:
                    cover_img = cover_elem.ele('tag:img', timeout=0)
                    if not cover_img:
                        cover_img = cover_elem.ele('img', timeout=0)
                else:
                    cover_img = None

                if cover_img:
                    src = cover_img.attr('src') or cover_img.attr('data-src') or ''
                    if src:
                        post['cover_image_url'] = src
                        post['images'] = [src]
                    else:
                        post['images'] = []
                else:
                    post['images'] = []

                if DEBUG and idx == 0:
                    print(f"[DEBUG] 封面图片: {post.get('cover_image_url', 'N/A')[:80]}...")

                # ============ 获取详情（可选）============
                if get_detail and post.get('url'):
                    try:
                        detail = get_post_detail(page, post['url'])
                        # 合并详情信息
                        if detail.get('description'):
                            post['description'] = detail['description']
                        if detail.get('tags'):
                            post['tags'] = detail['tags']
                        if detail.get('location'):
                            post['location'] = detail['location']
                        if detail.get('created_at'):
                            post['created_at'] = detail['created_at']
                        if detail.get('images'):
                            # 合并图片，去重
                            for img in detail['images']:
                                if img not in post['images']:
                                    post['images'].append(img)
                        # 更新互动数据
                        if detail.get('likes'):
                            post['likes'] = detail['likes']
                        if detail.get('comments'):
                            post['comments'] = detail['comments']
                        if detail.get('collects'):
                            post['collects'] = detail['collects']
                    except Exception as e:
                        print(f"[WARNING] 获取帖子详情失败: {e}")

                # 只有有标题或链接的才保存
                if post.get('title') or post.get('url'):
                    posts.append(post)

            except Exception as e:
                print(f"[WARNING] 解析单个笔记失败: {e}")
                continue

    except Exception as e:
        print(f"[ERROR] 解析页面失败: {e}")

    return posts


def download_post_images(posts, keyword, start_index=0):
    """
    下载帖子的所有图片

    Args:
        posts: 帖子列表
        keyword: 搜索关键词（用于目录名）
        start_index: 起始索引（用于断点续传）
    """
    ensure_dir(IMAGE_DIR)

    keyword_dir = os.path.join(IMAGE_DIR, keyword.replace(' ', '_'))
    ensure_dir(keyword_dir)

    total_downloaded = 0

    for i, post in enumerate(posts[start_index:], start=start_index):
        post_id = post.get('post_id', f'post_{i+1}')
        title = post.get('title', '无标题')[:30]  # 限制标题长度

        # 创建帖子专属文件夹
        post_dir = os.path.join(keyword_dir, f"{post_id}_{title}")
        ensure_dir(post_dir)

        images = post.get('images', [])
        if images:
            print(f"\n[{i+1}/{len(posts)}] 下载 {title} 的 {len(images)} 张图片...")

            for j, img_url in enumerate(images):
                if not img_url:
                    continue

                # 确定文件扩展名
                ext = '.jpg'
                if '?' in img_url:
                    img_url_clean = img_url.split('?')[0]
                    if '.' in img_url_clean:
                        ext = '.' + img_url_clean.split('.')[-1]
                        if len(ext) > 5:
                            ext = '.jpg'

                filename = f"image_{j+1}{ext}"
                filepath = os.path.join(post_dir, filename)

                # 跳过已存在的文件
                if os.path.exists(filepath):
                    print(f"  图片 {j+1} 已存在，跳过")
                    continue

                # 下载图片
                if download_image(img_url, filepath):
                    print(f"  ✅ 下载成功: {filename}")
                    total_downloaded += 1
                else:
                    print(f"  ❌ 下载失败: {filename}")

                # 随机延迟，避免过快
                time.sleep(random.uniform(0.3, 0.8))

            # 保存帖子信息到JSON
            info_file = os.path.join(post_dir, 'info.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(post, f, ensure_ascii=False, indent=2)

    print(f"\n========== 图片下载完成 ==========")
    print(f"共下载 {total_downloaded} 张图片")
    print(f"保存位置: {keyword_dir}")

    return total_downloaded


def search_with_browser(keyword, times=5, cookie=None, get_detail=False):
    """
    使用浏览器搜索并爬取

    Args:
        keyword: 搜索关键词
        times: 翻页次数
        cookie: 可选的Cookie
        get_detail: 是否获取每个帖子的详细信息
    """
    page = ChromiumPage()

    # 设置Cookie（如果提供）
    if cookie and cookie.strip():
        domain = '.xiaohongshu.com'
        page.set.cookies(cookie, domain=domain)

    # 构建搜索URL
    keyword_encode = quote(keyword)
    search_url = f'https://www.xiaohongshu.com/search_result?keyword={keyword_encode}&source=web_search_result'

    print(f"正在打开: {search_url}")
    page.get(search_url)

    # 等待页面加载
    print("等待页面加载...")
    time.sleep(3)

    all_posts = []

    for i in tqdm(range(times), desc="爬取进度"):
        # 解析当前页
        posts = parse_page(page, get_detail=get_detail, page_num=i+1)
        all_posts.extend(posts)
        print(f"第 {i+1} 页: 获取 {len(posts)} 条笔记")

        # 下滑加载更多
        if i < times - 1:
            random_time = random.uniform(1, 2)
            time.sleep(random_time)
            page.scroll.to_bottom()
            time.sleep(2)  # 等待新内容加载

    return all_posts


def get_cookie_from_browser():
    """从浏览器获取Cookie（需要手动操作）"""
    page = ChromiumPage()
    page.get('https://www.xiaohongshu.com')

    print("请在浏览器中扫码登录...")
    print("登录完成后，在控制台按回车继续...")

    input("登录完成后按回车继续...")

    # 获取Cookie
    cookies = page.cookies()

    # 转换为字符串格式
    cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])

    print("\n========== 你的Cookie ==========")
    print(cookie_str)
    print("================================\n")

    return cookie_str


def main():
    import argparse

    parser = argparse.ArgumentParser(description='小红书爬虫 - 浏览器自动化版本')
    parser.add_argument('keyword', nargs='?', help='搜索关键词')
    parser.add_argument('--times', '-t', type=int, default=3, help='翻页次数（默认3）')
    parser.add_argument('--cookie', '-c', help='Cookie（可选）')
    parser.add_argument('--get-cookie', '-g', action='store_true', help='仅获取Cookie')
    parser.add_argument('--detail', '-d', action='store_true', help='获取每个帖子的详细信息和所有图片（较慢）')
    parser.add_argument('--download', '-D', action='store_true', help='下载所有图片（需要配合 --detail 使用）')

    args = parser.parse_args()

    if args.get_cookie:
        get_cookie_from_browser()
        return

    if not args.keyword:
        print(__doc__)
        return

    keyword = args.keyword
    times = args.times

    if args.cookie:
        cookie = args.cookie
    elif COOKIE and not COOKIE.startswith('\n#'):
        cookie = COOKIE.strip()
    else:
        cookie = None
        print("[WARNING] 未配置Cookie，可能只能查看公开内容")

    print(f"正在搜索: 「{keyword}」")
    print(f"翻页次数: {times}")
    print(f"详细信息: {'是' if args.detail else '否'}\n")

    # 搜索并爬取
    posts = search_with_browser(keyword, times=times, cookie=cookie, get_detail=args.detail)
    print(json.dumps(posts, ensure_ascii=False, indent=2))

    print(f"\n========== 抓取完成 ==========")
    print(f"共获取 {len(posts)} 条笔记\n")

    # 打印结果
    for i, post in enumerate(posts[:10], 1):
        title = post.get('title', '无标题')[:50]
        author = post.get('author_name', '未知')
        likes = post.get('likes', '0')
        comments = post.get('comments', '0')
        image_count = len(post.get('images', []))

        print(f"{i}. {title}")
        print(f"   👤 {author} | 👍 {likes} | 💬 {comments} | 🖼️ {image_count}张图")

    # 保存JSON
    filename = f"xiaohongshu_{keyword.replace(' ', '_')}_{len(posts)}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 帖子数据已保存到: {filename}")

    # 下载图片
    if args.download and posts:
        print("\n开始下载图片...")
        download_post_images(posts, keyword)


if __name__ == '__main__':
    main()
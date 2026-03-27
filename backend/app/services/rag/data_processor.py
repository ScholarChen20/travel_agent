"""
数据预处理模块
功能：
1. 清洗小红书原始数据
2. 提取关键信息（城市、景点、美食、酒店）
3. 分类标注
4. 数据验证和安全性检查
"""

from typing import Dict, List, Optional, Tuple
import re
import html
from loguru import logger
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """内容类型枚举"""
    ATTRACTION = "attraction"
    FOOD = "food"
    HOTEL = "hotel"
    TIPS = "tips"
    GENERAL = "general"


@dataclass
class CleanedPost:
    """清洗后的帖子数据结构"""
    post_id: str
    title: str
    content: str
    content_type: str
    city: str
    tags: List[str]
    author: str
    likes: int
    comments: int
    collects: int
    source_url: str
    images: List[str]
    entities: Dict[str, List[str]]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'post_id': self.post_id,
            'title': self.title,
            'content': self.content,
            'content_type': self.content_type,
            'city': self.city,
            'tags': self.tags,
            'author': self.author,
            'likes': self.likes,
            'comments': self.comments,
            'collects': self.collects,
            'source_url': self.source_url,
            'images': self.images,
            'entities': self.entities
        }


class DataProcessor:
    """数据处理器"""
    
    CITY_KEYWORDS = {
        '澳门': ['澳门', 'macau', '妈阁'],
        '珠海': ['珠海', 'zhuhai'],
        '南澳岛': ['南澳岛', '南澳'],
        '香港': ['香港', 'hongkong', 'hk'],
        '北京': ['北京', 'beijing', '北平'],
        '上海': ['上海', 'shanghai'],
        '广州': ['广州', 'guangzhou', '羊城'],
        '深圳': ['深圳', 'shenzhen', '鹏城'],
        '杭州': ['杭州', 'hangzhou'],
        '成都': ['成都', 'chengdu', '蓉城'],
        '重庆': ['重庆', 'chongqing'],
        '西安': ['西安', 'xian', '长安'],
        '南京': ['南京', 'nanjing', '金陵'],
        '苏州': ['苏州', 'suzhou'],
        '厦门': ['厦门', 'xiamen', '鹭岛'],
        '三亚': ['三亚', 'sanya'],
        '丽江': ['丽江', 'lijiang'],
        '大理': ['大理', 'dali'],
        '桂林': ['桂林', 'guilin'],
        '张家界': ['张家界', 'zhangjiajie'],
    }
    
    CONTENT_KEYWORDS = {
        ContentType.ATTRACTION: [
            '景点', '打卡', '旅游', '攻略', '游玩', '景区', '门票',
            '必去', '推荐', '网红', '拍照', '风景', '名胜'
        ],
        ContentType.FOOD: [
            '美食', '餐厅', '小吃', '好吃', '推荐', '必吃', '特色',
            '美味', '佳肴', '料理', '探店', '吃货'
        ],
        ContentType.HOTEL: [
            '酒店', '住宿', '民宿', '宾馆', '入住', '房间', '预订',
            '度假村', '客栈', '青旅', '旅馆'
        ],
        ContentType.TIPS: [
            '避坑', '注意', '建议', '攻略', '贴士', '经验', '教训',
            '提醒', '必看', '收藏', '干货'
        ]
    }
    
    MAX_TITLE_LENGTH = 200
    MAX_CONTENT_LENGTH = 5000
    MAX_TAGS_COUNT = 20
    MAX_IMAGES_COUNT = 20
    
    def __init__(self):
        """初始化数据处理器"""
        self._compile_patterns()
        logger.info("数据处理器已初始化")
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"
            "\u3030"
            "]+",
            flags=re.UNICODE
        )
        
        self.html_pattern = re.compile(r'<[^>]+>')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.whitespace_pattern = re.compile(r'\s+')
    
    def clean_post(self, post: Dict) -> Optional[CleanedPost]:
        """
        清洗单条帖子数据
        
        Args:
            post: 原始帖子数据
            
        Returns:
            CleanedPost对象，失败返回None
        """
        try:
            if not self._validate_post(post):
                logger.warning(f"帖子数据验证失败: {post.get('post_id', 'unknown')}")
                return None
            
            post_id = self._sanitize_string(post.get('post_id', ''))
            if not post_id:
                logger.warning("帖子ID为空")
                return None
            
            title = self._clean_text(post.get('title', ''))
            content = self._clean_text(post.get('description', ''))
            
            if not title and not content:
                logger.warning(f"帖子标题和内容都为空: {post_id}")
                return None
            
            city = self._extract_city(
                post.get('tags', []),
                post.get('location', ''),
                title,
                content
            )
            
            content_type = self._classify_content(title, content, post.get('tags', []))
            
            tags = self._clean_tags(post.get('tags', []))
            
            author = self._sanitize_string(post.get('author_name', '匿名用户'))
            
            likes = self._parse_number(post.get('likes', '0'))
            comments = self._parse_number(post.get('comments', '0'))
            collects = self._parse_number(post.get('collects', '0'))
            
            source_url = self._validate_url(post.get('url', ''))
            
            images = self._clean_images(post.get('images', []))
            
            entities = self._extract_entities(title, content, tags)
            
            cleaned_post = CleanedPost(
                post_id=post_id,
                title=title[:self.MAX_TITLE_LENGTH],
                content=content[:self.MAX_CONTENT_LENGTH],
                content_type=content_type.value,
                city=city,
                tags=tags[:self.MAX_TAGS_COUNT],
                author=author,
                likes=likes,
                comments=comments,
                collects=collects,
                source_url=source_url,
                images=images[:self.MAX_IMAGES_COUNT],
                entities=entities
            )
            
            logger.debug(f"帖子清洗成功: {post_id}, 类型: {content_type.value}, 城市: {city}")
            return cleaned_post
            
        except Exception as e:
            logger.error(f"清洗帖子失败: {e}", exc_info=True)
            return None
    
    def _validate_post(self, post: Dict) -> bool:
        """验证帖子数据"""
        if not isinstance(post, dict):
            return False
        
        required_fields = ['post_id']
        for field in required_fields:
            if field not in post:
                return False
        
        return True
    
    def _sanitize_string(self, text: str) -> str:
        """清理字符串，防止XSS攻击"""
        if not isinstance(text, str):
            return ''
        
        text = html.escape(text.strip())
        
        text = self.html_pattern.sub('', text)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        if not isinstance(text, str):
            return ''
        
        text = self._sanitize_string(text)
        
        text = self.emoji_pattern.sub('', text)
        
        text = self.url_pattern.sub('', text)
        
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
    
    def _clean_tags(self, tags: List[str]) -> List[str]:
        """清洗标签"""
        if not isinstance(tags, list):
            return []
        
        cleaned_tags = []
        for tag in tags:
            if isinstance(tag, str):
                tag = tag.strip()
                if tag.startswith('#'):
                    tag = tag[1:]
                
                tag = self._sanitize_string(tag)
                
                if tag and len(tag) <= 50:
                    cleaned_tags.append(tag)
        
        return list(set(cleaned_tags))
    
    def _clean_images(self, images: List[str]) -> List[str]:
        """清洗图片URL列表"""
        if not isinstance(images, list):
            return []
        
        cleaned_images = []
        for img in images:
            url = self._validate_url(img)
            if url:
                cleaned_images.append(url)
        
        return cleaned_images
    
    def _validate_url(self, url: str) -> str:
        """验证URL"""
        if not isinstance(url, str):
            return ''
        
        url = url.strip()
        
        if not url:
            return ''
        
        if not url.startswith(('http://', 'https://')):
            return ''
        
        if len(url) > 2048:
            return ''
        
        return url
    
    def _extract_city(
        self,
        tags: List[str],
        location: str,
        title: str,
        content: str
    ) -> str:
        """从多个来源提取城市"""
        all_text = ' '.join([
            ' '.join(tags) if isinstance(tags, list) else '',
            location if isinstance(location, str) else '',
            title if isinstance(title, str) else '',
            content if isinstance(content, str) else ''
        ]).lower()
        
        for city, keywords in self.CITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in all_text:
                    return city
        
        if isinstance(location, str) and location:
            return location.split()[0] if ' ' in location else location
        
        return '未知'
    
    def _classify_content(
        self,
        title: str,
        desc: str,
        tags: List[str]
    ) -> ContentType:
        """分类内容类型"""
        text = f"{title} {desc} {' '.join(tags) if isinstance(tags, list) else ''}".lower()
        
        scores = {}
        for content_type, keywords in self.CONTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[content_type] = score
        
        if not scores or max(scores.values()) == 0:
            return ContentType.GENERAL
        
        return max(scores, key=scores.get)
    
    def _parse_number(self, num_str: str) -> int:
        """解析数字字符串"""
        if isinstance(num_str, (int, float)):
            return int(num_str)
        
        if not isinstance(num_str, str):
            return 0
        
        num_str = num_str.strip()
        
        if not num_str:
            return 0
        
        try:
            if '万' in num_str:
                num_str = num_str.replace('万', '')
                return int(float(num_str) * 10000)
            elif 'k' in num_str.lower():
                num_str = num_str.lower().replace('k', '')
                return int(float(num_str) * 1000)
            else:
                return int(float(num_str))
        except (ValueError, TypeError):
            return 0
    
    def _extract_entities(
        self,
        title: str,
        content: str,
        tags: List[str]
    ) -> Dict[str, List[str]]:
        """提取关键实体"""
        entities = {
            'attractions': [],
            'foods': [],
            'hotels': []
        }
        
        attraction_keywords = ['景点', '公园', '博物馆', '寺', '塔', '楼', '桥', '广场', '山', '湖', '海']
        food_keywords = ['餐厅', '小吃', '美食', '菜', '面', '饭', '火锅', '烧烤', '甜品']
        hotel_keywords = ['酒店', '民宿', '宾馆', '客栈', '度假村']
        
        text = f"{title} {content}"
        
        for keyword in attraction_keywords:
            if keyword in text:
                pattern = rf'([^\s，。！？、]+{keyword}[^\s，。！？、]*)'
                matches = re.findall(pattern, text)
                entities['attractions'].extend(matches[:3])
        
        for keyword in food_keywords:
            if keyword in text:
                pattern = rf'([^\s，。！？、]+{keyword}[^\s，。！？、]*)'
                matches = re.findall(pattern, text)
                entities['foods'].extend(matches[:3])
        
        for keyword in hotel_keywords:
            if keyword in text:
                pattern = rf'([^\s，。！？、]+{keyword}[^\s，。！？、]*)'
                matches = re.findall(pattern, text)
                entities['hotels'].extend(matches[:3])
        
        for key in entities:
            entities[key] = list(set(entities[key]))[:5]
        
        return entities
    
    def clean_posts_batch(self, posts: List[Dict]) -> List[CleanedPost]:
        """
        批量清洗帖子
        
        Args:
            posts: 帖子列表
            
        Returns:
            清洗后的帖子列表
        """
        if not isinstance(posts, list):
            logger.error("posts参数必须是列表")
            return []
        
        cleaned_posts = []
        failed_count = 0
        
        for post in posts:
            cleaned = self.clean_post(post)
            if cleaned:
                cleaned_posts.append(cleaned)
            else:
                failed_count += 1
        
        logger.info(f"批量清洗完成: 成功 {len(cleaned_posts)} 条, 失败 {failed_count} 条")
        return cleaned_posts

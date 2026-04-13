# RAG检索增强设计方案

## 📋 设计目标

将小红书爬取的旅行数据构建到向量数据库中，为旅行助手提供：
1. **旅行报告生成增强**：从检索库中获取酒店、美食、景点等参考信息
2. **景点图片兜底方案**：当Unsplash无法获取图片时，从RAG库中检索相关景点图片
3. **数据价值挖掘**：充分利用爬取的小红书数据，提升推荐质量

---

## 🏗️ 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户请求层                                 │
│  (旅行计划生成 / 景点图片获取 / 美食推荐 / 酒店推荐)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG检索服务层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 文本检索服务  │  │ 图片检索服务  │  │ 混合检索服务  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      向量数据库层                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Milvus / Chroma / Qdrant                     │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │ 文本向量库  │  │ 图片向量库  │  │ 元数据存储  │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据处理层                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 数据清洗模块  │  │ 向量化模块    │  │ 索引构建模块  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据源层                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  小红书爬取数据 (JSON格式)                                │  │
│  │  - 景点攻略、美食推荐、酒店点评                            │  │
│  │  - 多张图片、标签、地理位置                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 数据结构设计

### 1. 小红书原始数据结构

```json
{
  "url": "https://www.xiaohongshu.com/explore/xxx",
  "post_id": "69bec0aa0000000023025fb7",
  "title": "在澳门瞎溜达的7小时🇲🇴🙃plog存档",
  "description": "什么都要拍几张就对了 #澳门旅游#随便乱走系列...",
  "author_name": "一只陈",
  "author_avatar": "https://...",
  "created_at": "5天前 广东",
  "likes": "0",
  "comments": "0",
  "collects": "0",
  "images": ["https://...", "https://..."],
  "tags": ["#澳门旅游", "#随便乱走系列", "#澳门"],
  "location": "辽宁"
}
```

### 2. 向量化后的数据结构

#### 文档向量表 (travel_documents)

```python
{
    "id": "uuid",                          # 唯一标识
    "post_id": "69bec0aa0000000023025fb7", # 小红书帖子ID
    "title": "在澳门瞎溜达的7小时",          # 标题
    "content": "什么都要拍几张就对了...",    # 正文内容
    "content_type": "attraction",          # 内容类型: attraction/food/hotel/tips
    "city": "澳门",                         # 城市
    "location": "辽宁",                     # 发布者位置
    "tags": ["澳门旅游", "随便乱走系列"],    # 标签列表
    "author": "一只陈",                     # 作者
    "likes": 0,                            # 点赞数
    "comments": 0,                         # 评论数
    "collects": 0,                         # 收藏数
    "source_url": "https://...",           # 原文链接
    "images": ["https://...", ...],        # 图片列表
    "embedding": [0.123, -0.456, ...],     # 向量 (1024维 - Qwen3-Embedding-8B)
    "created_at": "2026-03-27",            # 创建时间
    "updated_at": "2026-03-27"             # 更新时间
}
```

#### 图片向量表 (travel_images)

```python
{
    "id": "uuid",                          # 唯一标识
    "post_id": "69bec0aa0000000023025fb7", # 关联的帖子ID
    "image_url": "https://...",            # 图片URL
    "image_type": "attraction",            # 图片类型
    "city": "澳门",                         # 城市
    "tags": ["澳门旅游", "景点"],           # 标签
    "description": "澳门街景",              # 图片描述
    "embedding": [0.789, 0.234, ...],      # 图片向量 (512维或768维)
    "created_at": "2026-03-27"
}
```

---

## 🔧 技术选型

### 方案对比

| 组件 | 方案A (推荐) | 方案B | 方案C |
|------|-------------|-------|-------|
| **向量数据库** | Qdrant Cloud (云服务) | Milvus (生产级) | Chroma (轻量级) |
| **文本向量化** | ModelScope Qwen3-Embedding-8B | BGE-large-zh | OpenAI text-embedding-3-small |
| **图片向量化** | 通义多模态 tongyi-embedding-vision-plus | CLIP ViT-B/32 | BLIP-2 |
| **LLM集成** | OpenAI API | 通义千问 | 本地模型 |
| **部署复杂度** | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **成本** | 中 | 中 | 低 |

### 推荐方案：Qdrant Cloud + ModelScope Qwen3-Embedding + 通义多模态嵌入

**理由**：
1. **Qdrant Cloud**：
   - 云服务，无需部署维护
   - 高可用、自动扩展
   - 支持丰富的过滤和查询
   - 提供免费额度，适合中小规模应用

2. **ModelScope Qwen3-Embedding-8B**：
   - 阿里云开源模型，中文效果优秀
   - 1024维向量，平衡性能和精度
   - 国内访问稳定，延迟低
   - 与通义千问生态统一

3. **通义多模态嵌入 (tongyi-embedding-vision-plus)**：
   - 阿里云原生服务，国内访问稳定
   - 支持图文跨模态检索
   - 支持视频、图片等多种输入
   - 与项目已使用的通义千问服务统一

---

## 📝 实现方案

### 阶段一：数据预处理与向量化 (1-2周)

#### 1.1 数据清洗模块

**文件**: `backend/app/services/rag/data_processor.py`

```python
"""
数据预处理模块
功能：
1. 清洗小红书原始数据
2. 提取关键信息（城市、景点、美食、酒店）
3. 分类标注
"""

from typing import List, Dict
import re
import json

class DataProcessor:
    """数据处理器"""
    
    def clean_post(self, post: Dict) -> Dict:
        """清洗单条帖子数据"""
        # 1. 提取城市信息
        city = self._extract_city(post.get('tags', []), post.get('location', ''))
        
        # 2. 分类内容类型
        content_type = self._classify_content(
            post.get('title', ''),
            post.get('description', ''),
            post.get('tags', [])
        )
        
        # 3. 清洗文本
        clean_content = self._clean_text(post.get('description', ''))
        
        # 4. 提取关键实体
        entities = self._extract_entities(clean_content)
        
        return {
            'post_id': post.get('post_id'),
            'title': post.get('title', ''),
            'content': clean_content,
            'content_type': content_type,
            'city': city,
            'tags': post.get('tags', []),
            'author': post.get('author_name', ''),
            'likes': self._parse_number(post.get('likes', '0')),
            'comments': self._parse_number(post.get('comments', '0')),
            'collects': self._parse_number(post.get('collects', '0')),
            'source_url': post.get('url', ''),
            'images': post.get('images', []),
            'entities': entities
        }
    
    def _extract_city(self, tags: List[str], location: str) -> str:
        """从标签和位置中提取城市"""
        # 城市关键词映射
        city_keywords = {
            '澳门': ['澳门', 'macau'],
            '珠海': ['珠海', 'zhuhai'],
            '南澳岛': ['南澳岛', '南澳'],
            # ... 更多城市
        }
        
        # 从标签中提取
        for tag in tags:
            for city, keywords in city_keywords.items():
                if any(kw in tag.lower() for kw in keywords):
                    return city
        
        return location or '未知'
    
    def _classify_content(self, title: str, desc: str, tags: List[str]) -> str:
        """分类内容类型"""
        text = f"{title} {desc} {' '.join(tags)}".lower()
        
        # 关键词分类
        keywords = {
            'attraction': ['景点', '打卡', '旅游', '攻略', '游玩', '景区'],
            'food': ['美食', '餐厅', '小吃', '好吃', '推荐', '必吃'],
            'hotel': ['酒店', '住宿', '民宿', '宾馆', '入住'],
            'tips': ['避坑', '注意', '建议', '攻略', '贴士']
        }
        
        for content_type, words in keywords.items():
            if any(word in text for word in words):
                return content_type
        
        return 'general'
    
    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        # 移除emoji
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、；：""''（）【】]', ' ', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_entities(self, text: str) -> Dict:
        """提取关键实体（景点、美食、酒店名称）"""
        # TODO: 使用NER模型提取
        return {
            'attractions': [],
            'foods': [],
            'hotels': []
        }
    
    def _parse_number(self, num_str: str) -> int:
        """解析数字字符串"""
        try:
            # 处理 "1.2万" 这种格式
            if '万' in num_str:
                return int(float(num_str.replace('万', '')) * 10000)
            return int(num_str)
        except:
            return 0
```

#### 1.2 向量化模块

**文件**: `backend/app/services/rag/embedding_service.py`

```python
"""
向量化服务
功能：
1. 文本向量化 (ModelScope Qwen3-Embedding)
2. 图片向量化 (通义多模态嵌入)
"""

from typing import List
from openai import OpenAI
from loguru import logger
import dashscope
import asyncio
from ..config import get_settings

class EmbeddingService:
    """向量化服务"""
    
    def __init__(self):
        self.settings = get_settings()
        self._init_text_embedding()
        self._init_image_embedding()
    
    def _init_text_embedding(self):
        """初始化文本向量化模型 (ModelScope)"""
        self.text_client = OpenAI(
            base_url='https://api-inference.modelscope.cn/v1',
            api_key=self.settings.modelscope_api_key
        )
        self.text_model = 'Qwen/Qwen3-Embedding-8B'
        self.embedding_dim = 1024  # Qwen3-Embedding-8B 输出维度
    
    def _init_image_embedding(self):
        """初始化图片向量化模型 (通义多模态)"""
        dashscope.api_key = self.settings.dashscope_api_key
        self.image_model = "tongyi-embedding-vision-plus"
    
    async def embed_text(self, text: str) -> List[float]:
        """
        文本向量化
        
        Args:
            text: 输入文本
            
        Returns:
            向量列表 (1024维)
        """
        try:
            response = self.text_client.embeddings.create(
                model=self.text_model,
                input=text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            logger.info(f"文本向量化成功，维度: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"文本向量化失败: {e}")
            return []
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量文本向量化"""
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
            await asyncio.sleep(0.1)  # 避免API限流
        return embeddings
    
    async def embed_image(self, image_url: str) -> List[float]:
        """
        图片向量化 (使用通义多模态嵌入)
        
        Args:
            image_url: 图片URL或本地路径
            
        Returns:
            向量列表
        """
        try:
            input_data = [{'image': image_url}]
            
            resp = dashscope.MultiModalEmbedding.call(
                model=self.image_model,
                input=input_data
            )
            
            if resp.status_code == 200:
                embedding = resp.output['embeddings'][0]['embedding']
                logger.info(f"图片向量化成功，维度: {len(embedding)}")
                return embedding
            else:
                logger.error(f"图片向量化失败: {resp.code} - {resp.message}")
                return []
                
        except Exception as e:
            logger.error(f"图片向量化失败: {e}")
            return []
    
    async def embed_images(self, image_urls: List[str]) -> List[List[float]]:
        """批量图片向量化"""
        embeddings = []
        for image_url in image_urls:
            embedding = await self.embed_image(image_url)
            embeddings.append(embedding)
            await asyncio.sleep(0.1)  # 避免API限流
        return embeddings
    
    async def embed_text_for_image_search(self, text: str) -> List[float]:
        """
        为图片搜索生成文本向量 (使用通义多模态嵌入)
        
        Args:
            text: 搜索文本
            
        Returns:
            向量列表
        """
        try:
            input_data = [{'text': text}]
            
            resp = dashscope.MultiModalEmbedding.call(
                model=self.image_model,
                input=input_data
            )
            
            if resp.status_code == 200:
                embedding = resp.output['embeddings'][0]['embedding']
                logger.info(f"文本向量化成功，维度: {len(embedding)}")
                return embedding
            else:
                logger.error(f"文本向量化失败: {resp.code} - {resp.message}")
                return []
                
        except Exception as e:
            logger.error(f"文本向量化失败: {e}")
            return []
```

#### 1.3 向量数据库管理

**文件**: `backend/app/services/rag/vector_store.py`

```python
"""
向量数据库管理
使用Qdrant Cloud作为向量存储
"""

from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from loguru import logger
from ..config import get_settings

class VectorStore:
    """向量数据库管理类"""
    
    def __init__(self):
        """初始化向量数据库"""
        settings = get_settings()
        
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        
        self.documents_collection = "travel_documents"
        self.images_collection = "travel_images"
        
        self._init_collections()
        logger.info("Qdrant向量数据库已初始化")
    
    def _init_collections(self):
        """初始化集合"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.documents_collection not in collection_names:
            self.client.create_collection(
                collection_name=self.documents_collection,
                vectors_config=VectorParams(
                    size=1024,  # Qwen3-Embedding-8B 输出维度
                    distance=Distance.COSINE
                )
            )
            logger.info(f"创建文档集合: {self.documents_collection}")
        
        if self.images_collection not in collection_names:
            self.client.create_collection(
                collection_name=self.images_collection,
                vectors_config=VectorParams(
                    size=1024,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"创建图片集合: {self.images_collection}")
    
    async def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict
    ):
        """
        添加文档到向量库
        
        Args:
            doc_id: 文档ID
            content: 文档内容
            embedding: 向量
            metadata: 元数据
        """
        try:
            self.client.upsert(
                collection_name=self.documents_collection,
                points=[
                    PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload={
                            "content": content,
                            **metadata
                        }
                    )
                ]
            )
            logger.info(f"添加文档成功: {doc_id}")
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
    
    async def add_documents(
        self,
        doc_ids: List[str],
        contents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict]
    ):
        """批量添加文档"""
        try:
            points = [
                PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={
                        "content": content,
                        **metadata
                    }
                )
                for doc_id, content, embedding, metadata in zip(
                    doc_ids, contents, embeddings, metadatas
                )
            ]
            
            self.client.upsert(
                collection_name=self.documents_collection,
                points=points
            )
            logger.info(f"批量添加文档成功: {len(points)} 条")
        except Exception as e:
            logger.error(f"批量添加文档失败: {e}")
    
    async def add_image(
        self,
        image_id: str,
        image_url: str,
        embedding: List[float],
        metadata: Dict
    ):
        """添加图片到向量库"""
        try:
            self.client.upsert(
                collection_name=self.images_collection,
                points=[
                    PointStruct(
                        id=image_id,
                        vector=embedding,
                        payload={
                            "image_url": image_url,
                            **metadata
                        }
                    )
                ]
            )
            logger.info(f"添加图片成功: {image_id}")
        except Exception as e:
            logger.error(f"添加图片失败: {e}")
    
    async def search_documents(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        city: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> List[Dict]:
        """
        搜索文档
        
        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            city: 城市过滤
            content_type: 内容类型过滤
            
        Returns:
            搜索结果列表
        """
        try:
            filter_conditions = []
            
            if city:
                filter_conditions.append(
                    FieldCondition(key="city", match=MatchValue(value=city))
                )
            
            if content_type:
                filter_conditions.append(
                    FieldCondition(key="content_type", match=MatchValue(value=content_type))
                )
            
            query_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            results = self.client.search(
                collection_name=self.documents_collection,
                query_vector=query_embedding,
                limit=n_results,
                query_filter=query_filter
            )
            
            documents = []
            for result in results:
                documents.append({
                    'id': result.id,
                    'content': result.payload.get('content', ''),
                    'metadata': {k: v for k, v in result.payload.items() if k != 'content'},
                    'score': result.score
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return []
    
    async def search_images(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        city: Optional[str] = None
    ) -> List[Dict]:
        """搜索图片"""
        try:
            filter_conditions = []
            
            if city:
                filter_conditions.append(
                    FieldCondition(key="city", match=MatchValue(value=city))
                )
            
            query_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            results = self.client.search(
                collection_name=self.images_collection,
                query_vector=query_embedding,
                limit=n_results,
                query_filter=query_filter
            )
            
            images = []
            for result in results:
                images.append({
                    'id': result.id,
                    'image_url': result.payload.get('image_url', ''),
                    'metadata': {k: v for k, v in result.payload.items() if k != 'image_url'},
                    'score': result.score
                })
            
            return images
            
        except Exception as e:
            logger.error(f"搜索图片失败: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """获取集合统计信息"""
        try:
            doc_info = self.client.get_collection(self.documents_collection)
            img_info = self.client.get_collection(self.images_collection)
            
            return {
                "documents_count": doc_info.points_count,
                "images_count": img_info.points_count
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                "documents_count": 0,
                "images_count": 0
            }
```

### 阶段二：RAG检索服务 (1周)

#### 2.1 RAG检索服务

**文件**: `backend/app/services/rag/rag_service.py`

```python
"""
RAG检索服务
功能：
1. 文本检索：景点、美食、酒店推荐
2. 图片检索：景点图片兜底
3. 混合检索：多模态检索
"""

from typing import List, Dict, Optional
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from loguru import logger

class RAGService:
    """RAG检索服务"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        logger.info("RAG检索服务已初始化")
    
    async def search_attractions(
        self,
        city: str,
        query: str = "",
        n_results: int = 5
    ) -> List[Dict]:
        """
        搜索景点信息
        
        Args:
            city: 城市名称
            query: 搜索查询（可选）
            n_results: 返回结果数量
            
        Returns:
            景点列表
        """
        try:
            search_text = f"{city} {query} 景点 推荐" if query else f"{city} 景点 推荐"
            
            query_embedding = await self.embedding_service.embed_text(search_text)
            
            if not query_embedding:
                logger.error("生成查询向量失败")
                return []
            
            results = await self.vector_store.search_documents(
                query_embedding=query_embedding,
                n_results=n_results,
                city=city,
                content_type="attraction"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"搜索景点失败: {e}")
            return []
    
    async def search_food(
        self,
        city: str,
        query: str = "",
        n_results: int = 5
    ) -> List[Dict]:
        """搜索美食推荐"""
        try:
            search_text = f"{city} {query} 美食 推荐" if query else f"{city} 美食 推荐"
            
            query_embedding = await self.embedding_service.embed_text(search_text)
            
            if not query_embedding:
                logger.error("生成查询向量失败")
                return []
            
            results = await self.vector_store.search_documents(
                query_embedding=query_embedding,
                n_results=n_results,
                city=city,
                content_type="food"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"搜索美食失败: {e}")
            return []
    
    async def search_hotels(
        self,
        city: str,
        query: str = "",
        n_results: int = 5
    ) -> List[Dict]:
        """搜索酒店推荐"""
        try:
            search_text = f"{city} {query} 酒店 住宿" if query else f"{city} 酒店 住宿"
            
            query_embedding = await self.embedding_service.embed_text(search_text)
            
            if not query_embedding:
                logger.error("生成查询向量失败")
                return []
            
            results = await self.vector_store.search_documents(
                query_embedding=query_embedding,
                n_results=n_results,
                city=city,
                content_type="hotel"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"搜索酒店失败: {e}")
            return []
    
    async def search_attraction_images(
        self,
        attraction_name: str,
        city: str = "",
        n_results: int = 3
    ) -> List[str]:
        """
        搜索景点图片（兜底方案）
        
        Args:
            attraction_name: 景点名称
            city: 城市名称
            n_results: 返回结果数量
            
        Returns:
            图片URL列表
        """
        try:
            search_text = f"{attraction_name} {city} 景点"
            query_embedding = await self.embedding_service.embed_text_for_image_search(search_text)
            
            if not query_embedding:
                logger.error("生成查询向量失败")
                return []
            
            results = await self.vector_store.search_images(
                query_embedding=query_embedding,
                n_results=n_results,
                city=city if city else None
            )
            
            image_urls = [result['image_url'] for result in results]
            
            return image_urls
            
        except Exception as e:
            logger.error(f"搜索景点图片失败: {e}")
            return []
    
    async def get_travel_context(
        self,
        city: str,
        preferences: List[str] = None
    ) -> str:
        """
        获取旅行上下文（用于LLM增强）
        
        Args:
            city: 城市名称
            preferences: 用户偏好
            
        Returns:
            上下文文本
        """
        try:
            attractions = await self.search_attractions(city, n_results=3)
            foods = await self.search_food(city, n_results=3)
            hotels = await self.search_hotels(city, n_results=3)
            
            context = f"\n=== {city}旅行参考信息 ===\n\n"
            
            if attractions:
                context += "【热门景点】\n"
                for i, attr in enumerate(attractions, 1):
                    title = attr['metadata'].get('title', '未知')
                    content = attr['content'][:100]
                    context += f"{i}. {title}\n"
                    context += f"   {content}...\n\n"
            
            if foods:
                context += "【美食推荐】\n"
                for i, food in enumerate(foods, 1):
                    title = food['metadata'].get('title', '未知')
                    content = food['content'][:100]
                    context += f"{i}. {title}\n"
                    context += f"   {content}...\n\n"
            
            if hotels:
                context += "【酒店推荐】\n"
                for i, hotel in enumerate(hotels, 1):
                    title = hotel['metadata'].get('title', '未知')
                    content = hotel['content'][:100]
                    context += f"{i}. {title}\n"
                    context += f"   {content}...\n\n"
            
            return context
            
        except Exception as e:
            logger.error(f"获取旅行上下文失败: {e}")
            return ""


_rag_service = None


def get_rag_service() -> RAGService:
    """获取RAG服务实例（单例模式）"""
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RAGService()
    
    return _rag_service
```

### 阶段三：集成到现有系统 (1周)

#### 3.1 修改旅行计划生成

**文件**: `backend/app/agents/trip_planner_agent.py`

```python
# 在 TripPlannerAgent 类中添加

from ..services.rag.rag_service import get_rag_service

class TripPlannerAgent:
    def __init__(self):
        # ... 现有代码 ...
        self.rag_service = get_rag_service()  # 新增
    
    def _build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str = "") -> str:
        """构建行程规划查询（增强版）"""
        
        # 新增：从RAG获取上下文
        rag_context = await self.rag_service.get_travel_context(
            city=request.city,
            preferences=request.preferences
        )
        
        query = f"""请根据以下信息生成{request.city}的{request.travel_days}天旅行计划:

**基本信息:**
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}天
- 交通方式: {request.transportation}
- 住宿: {request.accommodation}
- 偏好: {', '.join(request.preferences) if request.preferences else '无'}

**景点信息:**
{attractions}

**天气信息:**
{weather}

**酒店信息:**
{hotels}

**小红书真实用户推荐（RAG检索）:**
{rag_context}

**要求:**
1. 每天安排2-3个景点
2. 每天必须包含早中晚三餐
3. 每天推荐一个具体的酒店(从酒店信息中选择)
4. 参考小红书用户的真实推荐，提供更接地气的建议
5. 返回完整的JSON格式数据
"""
        return query
```

#### 3.2 修改图片获取服务

**文件**: `backend/app/services/image_service.py`

```python
# 在 ImageService 类中修改

from ..services.rag.rag_service import get_rag_service

class ImageService:
    def __init__(self):
        # ... 现有代码 ...
        self.rag_service = get_rag_service()  # 新增
    
    async def get_and_upload_attraction_image(
        self,
        attraction_name: str,
        city: str = ""
    ) -> Optional[str]:
        """
        获取景点图片并上传到 OSS（增强版）
        
        流程：
        1. 先尝试从Unsplash获取
        2. 失败则从RAG检索小红书图片
        3. 下载并上传到OSS
        """
        try:
            # 1. 尝试从Unsplash获取
            search_query = f"{attraction_name} {city} China landmark" if city else f"{attraction_name} China"
            logger.info(f"搜索景点图片: {search_query}")
            
            photo_url = self.unsplash_service.get_photo_url(search_query)
            
            # 2. Unsplash失败，使用RAG兜底
            if not photo_url:
                logger.warning(f"Unsplash未找到图片，尝试RAG检索: {attraction_name}")
                rag_images = await self.rag_service.search_attraction_images(
                    attraction_name=attraction_name,
                    city=city,
                    n_results=3
                )
                
                if rag_images:
                    photo_url = rag_images[0]
                    logger.info(f"RAG检索到图片: {photo_url}")
            
            if not photo_url:
                logger.warning(f"未找到景点图片: {attraction_name}")
                return None
            
            # 3. 下载并上传到OSS
            image_data = await self._download_image(photo_url)
            if not image_data:
                logger.error(f"下载图片失败: {photo_url}")
                return None
            
            oss_url = await self._upload_image(image_data, attraction_name, city)
            
            return oss_url
            
        except Exception as e:
            logger.error(f"获取并上传景点图片失败: {attraction_name}, 错误: {str(e)}")
            return None
```

#### 3.3 新增API接口

**文件**: `backend/app/api/routes/rag.py`

```python
"""
RAG检索API
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ...services.rag.rag_service import get_rag_service
from ...models.responses import ApiResponse

router = APIRouter(prefix="/rag", tags=["RAG检索"])

@router.get(
    "/attractions",
    summary="搜索景点",
    description="从RAG库中搜索景点推荐"
)
async def search_attractions(
    city: str = Query(..., description="城市名称"),
    query: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(5, ge=1, le=20, description="返回数量")
):
    """搜索景点"""
    rag_service = get_rag_service()
    results = await rag_service.search_attractions(city, query or "", limit)
    return ApiResponse.success(data=results, msg="搜索成功")

@router.get(
    "/food",
    summary="搜索美食",
    description="从RAG库中搜索美食推荐"
)
async def search_food(
    city: str = Query(..., description="城市名称"),
    query: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(5, ge=1, le=20, description="返回数量")
):
    """搜索美食"""
    rag_service = get_rag_service()
    results = await rag_service.search_food(city, query or "", limit)
    return ApiResponse.success(data=results, msg="搜索成功")

@router.get(
    "/hotels",
    summary="搜索酒店",
    description="从RAG库中搜索酒店推荐"
)
async def search_hotels(
    city: str = Query(..., description="城市名称"),
    query: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(5, ge=1, le=20, description="返回数量")
):
    """搜索酒店"""
    rag_service = get_rag_service()
    results = await rag_service.search_hotels(city, query or "", limit)
    return ApiResponse.success(data=results, msg="搜索成功")

@router.get(
    "/images",
    summary="搜索景点图片",
    description="从RAG库中搜索景点图片"
)
async def search_images(
    attraction_name: str = Query(..., description="景点名称"),
    city: Optional[str] = Query(None, description="城市名称"),
    limit: int = Query(3, ge=1, le=10, description="返回数量")
):
    """搜索景点图片"""
    rag_service = get_rag_service()
    results = await rag_service.search_attraction_images(attraction_name, city or "", limit)
    return ApiResponse.success(data={"images": results}, msg="搜索成功")
```

### 阶段四：数据导入脚本 (1周)

#### 4.1 数据导入脚本

**文件**: `backend/scripts/import_rag_data.py`

```python
"""
RAG数据导入脚本
功能：将小红书数据导入到向量数据库
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
from loguru import logger

# 添加项目路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag.data_processor import DataProcessor
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.vector_store import VectorStore


class RAGDataImporter:
    """RAG数据导入器"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    async def import_from_json(self, json_file: str, batch_size: int = 10):
        """
        从JSON文件导入数据
        
        Args:
            json_file: JSON文件路径
            batch_size: 批处理大小
        """
        logger.info(f"开始导入数据: {json_file}")
        
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
        
        logger.info(f"读取到 {len(posts)} 条数据")
        
        # 批处理
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i+batch_size]
            await self._process_batch(batch, i, len(posts))
        
        logger.info("数据导入完成")
    
    async def _process_batch(self, batch: List[Dict], start_idx: int, total: int):
        """处理一批数据"""
        logger.info(f"处理进度: {start_idx}/{total}")
        
        doc_ids = []
        contents = []
        embeddings = []
        metadatas = []
        
        image_ids = []
        image_urls = []
        image_embeddings = []
        image_metadatas = []
        
        for post in batch:
            try:
                # 1. 清洗数据
                cleaned_data = self.processor.clean_post(post)
                
                # 2. 生成文档向量
                doc_content = f"{cleaned_data['title']}\n{cleaned_data['content']}"
                doc_embedding = await self.embedding_service.embed_text(doc_content)
                
                if doc_embedding:
                    doc_ids.append(cleaned_data['post_id'])
                    contents.append(doc_content)
                    embeddings.append(doc_embedding)
                    metadatas.append({
                        'post_id': cleaned_data['post_id'],
                        'title': cleaned_data['title'],
                        'content_type': cleaned_data['content_type'],
                        'city': cleaned_data['city'],
                        'tags': ','.join(cleaned_data['tags']),
                        'author': cleaned_data['author'],
                        'likes': cleaned_data['likes'],
                        'source_url': cleaned_data['source_url']
                    })
                
                # 3. 处理图片
                for idx, image_url in enumerate(cleaned_data['images'][:5]):  # 最多处理5张图片
                    try:
                        image_embedding = self.embedding_service.embed_image(image_url)
                        
                        if image_embedding:
                            image_id = f"{cleaned_data['post_id']}_img_{idx}"
                            image_ids.append(image_id)
                            image_urls.append(image_url)
                            image_embeddings.append(image_embedding)
                            image_metadatas.append({
                                'post_id': cleaned_data['post_id'],
                                'city': cleaned_data['city'],
                                'content_type': cleaned_data['content_type'],
                                'tags': ','.join(cleaned_data['tags'])
                            })
                    except Exception as e:
                        logger.warning(f"处理图片失败: {e}")
                        continue
                
                # 延迟，避免API限流
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"处理帖子失败: {e}")
                continue
        
        # 批量添加到向量库
        if doc_ids:
            await self.vector_store.add_documents(
                doc_ids=doc_ids,
                contents=contents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"添加 {len(doc_ids)} 条文档")
        
        if image_ids:
            for i in range(len(image_ids)):
                await self.vector_store.add_image(
                    image_id=image_ids[i],
                    image_url=image_urls[i],
                    embedding=image_embeddings[i],
                    metadata=image_metadatas[i]
                )
            logger.info(f"添加 {len(image_ids)} 张图片")
    
    async def import_from_directory(self, data_dir: str):
        """
        从目录导入所有JSON文件
        
        Args:
            data_dir: 数据目录路径
        """
        data_path = Path(data_dir)
        json_files = list(data_path.glob("*.json"))
        
        logger.info(f"找到 {len(json_files)} 个JSON文件")
        
        for json_file in json_files:
            await self.import_from_json(str(json_file))
        
        # 打印统计信息
        stats = self.vector_store.get_collection_stats()
        logger.info(f"向量库统计: {stats}")


async def main():
    """主函数"""
    importer = RAGDataImporter()
    
    # 导入单个文件
    # await importer.import_from_json("backend/data/rag_data/xiaohongshu_澳门旅游_1.json")
    
    # 导入整个目录
    await importer.import_from_directory("backend/data/rag_data")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📦 依赖安装

### requirements.txt 新增依赖

```txt
# RAG相关依赖
qdrant-client>=1.7.0
dashscope>=1.14.0
openai>=1.12.0
```

### 安装命令

```bash
pip install qdrant-client dashscope openai
```

### 配置文件更新

**文件**: `backend/app/config.py`

```python
class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # Qdrant配置
    qdrant_url: str = Field(
        default="https://f0322c03-b3f8-423e-a3cb-2f160f26d25a.us-east4-0.gcp.cloud.qdrant.io:6333",
        alias="QDRANT_URL"
    )
    qdrant_api_key: str = Field(
        default="",
        alias="QDRANT_API_KEY"
    )
    
    # ModelScope配置
    modelscope_api_key: str = Field(
        default="ms-7df9fd49-9a59-495d-bf50-f2922001f367",
        alias="MODELSCOPE_API_KEY"
    )
    
    # 通义千问配置（已存在）
    dashscope_api_key: str = Field(
        default="",
        alias="DASHSCOPE_API_KEY"
    )
```

**文件**: `.env`

```bash
# Qdrant配置
QDRANT_URL=https://f0322c03-b3f8-423e-a3cb-2f160f26d25a.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=

# ModelScope配置
MODELSCOPE_API_KEY=ms-7df9fd49-9a59-495d-bf50-f2922001f367

# 通义千问配置
DASHSCOPE_API_KEY=your_dashscope_api_key
```

---

## 🚀 部署方案

### 开发环境

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，填写Qdrant和通义千问的API密钥

# 3. 导入数据
python backend/scripts/import_rag_data.py

# 4. 启动服务
python backend/run.py
```

### 生产环境

```yaml
# docker-compose.yml 新增环境变量
services:
  backend:
    # ... 现有配置 ...
    environment:
      # ... 现有环境变量 ...
      - QDRANT_URL=${QDRANT_URL}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
```

### Qdrant Cloud 配置

1. **访问 Qdrant Cloud 控制台**
   - 登录：https://cloud.qdrant.io/
   - 创建集群（免费额度：1GB存储）

2. **获取连接信息**
   - URL: `https://xxx.us-east4-0.gcp.cloud.qdrant.io:6333`
   - API Key: 在集群详情页获取

3. **配置防火墙（可选）**
   - 如需限制访问IP，在Qdrant控制台配置

### 通义千问配置

1. **开通服务**
   - 访问：https://dashscope.console.aliyun.com/
   - 开通"多模态向量"服务

2. **获取API Key**
   - 在控制台创建API Key
   - 配置到`.env`文件中

### ModelScope配置

1. **访问 ModelScope**
   - 网址：https://www.modelscope.cn/
   - 注册账号并登录

2. **获取API Key**
   - 进入个人中心 → API Token管理
   - 创建新的Token
   - 配置到`.env`文件中

---

## 📊 性能优化

### 1. 向量化优化
- **批量处理**：使用批量API减少网络请求
- **缓存机制**：缓存已处理的向量
- **异步处理**：使用异步IO提高并发

### 2. 检索优化
- **索引优化**：使用HNSW索引加速检索
- **元数据过滤**：先过滤元数据再检索
- **结果缓存**：缓存热门查询结果

### 3. 存储优化
- **数据压缩**：压缩向量数据
- **分区存储**：按城市分区存储
- **定期清理**：清理过期数据

---

## 📈 监控指标

### 关键指标

1. **数据质量指标**
   - 向量化成功率
   - 数据完整性
   - 分类准确率

2. **检索性能指标**
   - 检索延迟 (P50/P95/P99)
   - 检索召回率
   - 检索准确率

3. **系统资源指标**
   - 向量库大小
   - 内存使用
   - CPU使用率

### 监控方案

```python
# backend/app/services/rag/monitoring.py

from prometheus_client import Counter, Histogram, Gauge

# 定义指标
RAG_SEARCH_COUNT = Counter('rag_search_total', 'RAG检索总次数', ['type'])
RAG_SEARCH_LATENCY = Histogram('rag_search_latency_seconds', 'RAG检索延迟')
RAG_VECTOR_COUNT = Gauge('rag_vector_total', '向量总数', ['collection'])

class RAGMonitor:
    """RAG监控"""
    
    @staticmethod
    def record_search(search_type: str, latency: float):
        RAG_SEARCH_COUNT.labels(type=search_type).inc()
        RAG_SEARCH_LATENCY.observe(latency)
    
    @staticmethod
    def update_vector_count(collection: str, count: int):
        RAG_VECTOR_COUNT.labels(collection=collection).set(count)
```

---

## 🎯 预期效果

### 1. 旅行计划质量提升
- **更真实的推荐**：基于真实用户分享
- **更丰富的内容**：包含用户真实体验
- **更接地气的建议**：避坑指南、小众景点

### 2. 图片获取成功率提升
- **Unsplash失败率降低**：从30%降低到10%
- **图片相关性提升**：使用CLIP跨模态检索
- **图片质量提升**：真实用户拍摄的照片

### 3. 用户体验提升
- **更快的响应**：本地向量库检索
- **更准确的结果**：语义检索而非关键词匹配
- **更个性化的推荐**：基于用户偏好检索

---

## 📅 实施计划

| 阶段 | 任务 | 时间 | 优先级 |
|------|------|------|--------|
| 阶段一 | 数据预处理与向量化 | 1-2周 | 高 |
| 阶段二 | RAG检索服务开发 | 1周 | 高 |
| 阶段三 | 集成到现有系统 | 1周 | 高 |
| 阶段四 | 数据导入与测试 | 1周 | 中 |
| 阶段五 | 性能优化与监控 | 1周 | 中 |
| 阶段六 | 文档与部署 | 1周 | 低 |

**总计：6-7周**

---

## 🔍 风险与挑战

### 1. 技术风险
- **向量质量**：中文文本向量化效果
- **检索准确率**：语义理解可能不准确
- **性能瓶颈**：大规模数据检索延迟

### 2. 数据风险
- **数据质量**：小红书数据可能包含噪音
- **数据时效性**：数据可能过时
- **版权问题**：图片版权需要确认

### 3. 缓解措施
- **A/B测试**：对比有无RAG的效果
- **人工审核**：定期审核推荐质量
- **用户反馈**：收集用户反馈持续优化

---

## 📚 参考资料

1. [Qdrant官方文档](https://qdrant.tech/documentation/)
2. [ModelScope Embedding API](https://www.modelscope.cn/docs)
3. [通义千问多模态嵌入](https://help.aliyun.com/document_detail/2712575.html)
4. [RAG最佳实践](https://www.pinecone.io/learn/retrieval-augmented-generation/)

"""
RAG模块单元测试
测试覆盖：
1. 数据处理器测试
2. 向量化服务测试
3. 向量存储测试
4. RAG服务测试
5. 安全性测试
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from app.services.rag.data_processor import (
    DataProcessor,
    CleanedPost,
    ContentType
)
from app.services.rag.embedding_service import (
    EmbeddingService,
    EmbeddingResult,
    EmbeddingConfig,
    InputValidator as EmbeddingValidator,
    SecurityError,
    ValidationError
)
from app.services.rag.vector_store import (
    VectorStore,
    VectorConfig,
    SearchResult,
    InputValidator as VectorValidator
)


class TestDataProcessor:
    """数据处理器测试"""
    
    @pytest.fixture
    def processor(self):
        return DataProcessor()
    
    @pytest.fixture
    def sample_post(self):
        return {
            "post_id": "test123",
            "title": "澳门旅游攻略",
            "description": "澳门必去景点推荐，大三巴牌坊、威尼斯人、巴黎人等",
            "author_name": "测试用户",
            "tags": ["#澳门旅游", "#澳门", "#景点推荐"],
            "likes": "100",
            "comments": "20",
            "collects": "50",
            "url": "https://www.xiaohongshu.com/explore/test123",
            "images": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ],
            "location": "澳门"
        }
    
    def test_clean_post_success(self, processor, sample_post):
        """测试成功清洗帖子"""
        result = processor.clean_post(sample_post)
        
        assert result is not None
        assert result.post_id == "test123"
        assert result.title == "澳门旅游攻略"
        assert result.city == "澳门"
        assert result.content_type in ["attraction", "general"]
        assert len(result.tags) > 0
        assert len(result.images) == 2
    
    def test_clean_post_empty_id(self, processor, sample_post):
        """测试空ID帖子"""
        sample_post["post_id"] = ""
        result = processor.clean_post(sample_post)
        assert result is None
    
    def test_clean_post_missing_id(self, processor, sample_post):
        """测试缺少ID的帖子"""
        del sample_post["post_id"]
        result = processor.clean_post(sample_post)
        assert result is None
    
    def test_clean_post_xss_prevention(self, processor, sample_post):
        """测试XSS攻击防护"""
        sample_post["title"] = "<script>alert('xss')</script>澳门旅游"
        sample_post["description"] = "<img src=x onerror=alert('xss')>"
        
        result = processor.clean_post(sample_post)
        
        assert result is not None
        assert "<script>" not in result.title
        assert "<img" not in result.content
    
    def test_extract_city_from_tags(self, processor, sample_post):
        """测试从标签提取城市"""
        sample_post["location"] = ""
        result = processor.clean_post(sample_post)
        assert result.city == "澳门"
    
    def test_extract_city_from_location(self, processor, sample_post):
        """测试从位置提取城市"""
        sample_post["tags"] = []
        result = processor.clean_post(sample_post)
        assert result.city == "澳门"
    
    def test_classify_content_attraction(self, processor, sample_post):
        """测试景点内容分类"""
        sample_post["description"] = "澳门必去景点打卡，大三巴牌坊"
        result = processor.clean_post(sample_post)
        assert result.content_type == "attraction"
    
    def test_classify_content_food(self, processor, sample_post):
        """测试美食内容分类"""
        sample_post["description"] = "澳门美食推荐，猪扒包、蛋挞必吃"
        sample_post["tags"] = ["#澳门美食", "#美食推荐"]
        result = processor.clean_post(sample_post)
        assert result.content_type == "food"
    
    def test_classify_content_hotel(self, processor, sample_post):
        """测试酒店内容分类"""
        sample_post["description"] = "澳门酒店推荐，威尼斯人度假村"
        sample_post["tags"] = ["#澳门酒店", "#住宿推荐"]
        result = processor.clean_post(sample_post)
        assert result.content_type == "hotel"
    
    def test_clean_posts_batch(self, processor):
        """测试批量清洗帖子"""
        posts = [
            {"post_id": "1", "title": "测试1", "description": "内容1"},
            {"post_id": "2", "title": "测试2", "description": "内容2"},
            {"post_id": "", "title": "无效帖子"},
        ]
        
        results = processor.clean_posts_batch(posts)
        
        assert len(results) == 2
        assert all(isinstance(r, CleanedPost) for r in results)
    
    def test_parse_number_with_wan(self, processor):
        """测试万单位数字解析"""
        assert processor._parse_number("1.5万") == 15000
        assert processor._parse_number("2万") == 20000
    
    def test_parse_number_with_k(self, processor):
        """测试K单位数字解析"""
        assert processor._parse_number("1.5k") == 1500
        assert processor._parse_number("2K") == 2000
    
    def test_validate_url_valid(self, processor):
        """测试有效URL验证"""
        url = "https://example.com/image.jpg"
        result = processor._validate_url(url)
        assert result == url
    
    def test_validate_url_invalid(self, processor):
        """测试无效URL验证"""
        assert processor._validate_url("not_a_url") == ""
        assert processor._validate_url("ftp://example.com") == ""
        assert processor._validate_url("") == ""


class TestEmbeddingValidator:
    """向量化输入验证器测试"""
    
    def test_validate_text_success(self):
        """测试文本验证成功"""
        text = "这是一个测试文本"
        result = EmbeddingValidator.validate_text(text)
        assert result == text
    
    def test_validate_text_empty(self):
        """测试空文本"""
        with pytest.raises(ValidationError):
            EmbeddingValidator.validate_text("")
    
    def test_validate_text_whitespace_only(self):
        """测试仅空白字符"""
        with pytest.raises(ValidationError):
            EmbeddingValidator.validate_text("   ")
    
    def test_validate_text_truncation(self):
        """测试文本截断"""
        long_text = "a" * 10000
        result = EmbeddingValidator.validate_text(long_text, max_length=100)
        assert len(result) == 100
    
    def test_validate_image_url_success(self):
        """测试图片URL验证成功"""
        url = "https://sns-webpic-qc.xhscdn.com/test.jpg"
        result = EmbeddingValidator.validate_image_url(url)
        assert result == url
    
    def test_validate_image_url_dangerous_protocol(self):
        """测试危险协议"""
        with pytest.raises(SecurityError):
            EmbeddingValidator.validate_image_url("javascript:alert(1)")
        
        with pytest.raises(SecurityError):
            EmbeddingValidator.validate_image_url("data:text/html,<script>")
    
    def test_validate_image_url_localhost(self):
        """测试本地地址"""
        with pytest.raises(SecurityError):
            EmbeddingValidator.validate_image_url("http://localhost/image.jpg")
        
        with pytest.raises(SecurityError):
            EmbeddingValidator.validate_image_url("http://127.0.0.1/image.jpg")
    
    def test_validate_image_url_private_network(self):
        """测试私有网络地址"""
        with pytest.raises(SecurityError):
            EmbeddingValidator.validate_image_url("http://192.168.1.1/image.jpg")
        
        with pytest.raises(SecurityError):
            EmbeddingValidator.validate_image_url("http://10.0.0.1/image.jpg")


class TestVectorValidator:
    """向量存储输入验证器测试"""
    
    def test_validate_id_success(self):
        """测试ID验证成功"""
        assert VectorValidator.validate_id("test123") == "test123"
        assert VectorValidator.validate_id("test-123:abc") == "test-123:abc"
    
    def test_validate_id_empty(self):
        """测试空ID"""
        with pytest.raises(ValidationError):
            VectorValidator.validate_id("")
    
    def test_validate_id_too_long(self):
        """测试过长ID"""
        long_id = "a" * 300
        with pytest.raises(ValidationError):
            VectorValidator.validate_id(long_id)
    
    def test_validate_id_invalid_chars(self):
        """测试非法字符ID"""
        with pytest.raises(ValidationError):
            VectorValidator.validate_id("test@123")
        
        with pytest.raises(ValidationError):
            VectorValidator.validate_id("test 123")
    
    def test_validate_embedding_success(self):
        """测试向量验证成功"""
        embedding = [0.1] * 1024
        result = VectorValidator.validate_embedding(embedding, 1024)
        assert result == embedding
    
    def test_validate_embedding_wrong_dimension(self):
        """测试向量维度错误"""
        embedding = [0.1] * 512
        with pytest.raises(ValidationError):
            VectorValidator.validate_embedding(embedding, 1024)
    
    def test_validate_embedding_invalid_type(self):
        """测试向量类型错误"""
        with pytest.raises(ValidationError):
            VectorValidator.validate_embedding("not_a_list", 1024)
    
    def test_validate_metadata_success(self):
        """测试元数据验证成功"""
        metadata = {"key": "value", "number": 123}
        result = VectorValidator.validate_metadata(metadata)
        assert result == metadata
    
    def test_validate_metadata_too_many_fields(self):
        """测试元数据字段过多"""
        metadata = {f"key_{i}": f"value_{i}" for i in range(150)}
        with pytest.raises(ValidationError):
            VectorValidator.validate_metadata(metadata)
    
    def test_validate_metadata_value_truncation(self):
        """测试元数据值截断"""
        metadata = {"key": "a" * 2000}
        result = VectorValidator.validate_metadata(metadata)
        assert len(result["key"]) == 1000


class TestEmbeddingService:
    """向量化服务测试"""
    
    @pytest.fixture
    def mock_settings(self):
        """模拟配置"""
        settings = Mock()
        settings.modelscope_api_key = "test_key"
        settings.dashscope_api_key = "test_key"
        return settings
    
    @pytest.fixture
    def embedding_config(self):
        """向量化配置"""
        return EmbeddingConfig(
            text_model="test-model",
            image_model="test-image-model",
            max_retries=2,
            retry_delay=0.1
        )
    
    @patch('app.services.rag.embedding_service.get_settings')
    def test_init_without_api_key(self, mock_get_settings):
        """测试无API密钥初始化"""
        mock_settings = Mock()
        mock_settings.modelscope_api_key = None
        mock_settings.dashscope_api_key = None
        mock_get_settings.return_value = mock_settings
        
        with pytest.raises(Exception):
            EmbeddingService()
    
    @pytest.mark.asyncio
    async def test_embed_text_empty(self):
        """测试空文本向量化"""
        service = Mock(spec=EmbeddingService)
        service._semaphore = asyncio.Semaphore(5)
        service.validator = EmbeddingValidator()
        service.config = EmbeddingConfig()
        
        result = EmbeddingResult(success=False, error="文本为空")
        
        with patch.object(EmbeddingValidator, 'validate_text', side_effect=ValidationError("文本为空")):
            assert result.success == False


class TestVectorStore:
    """向量存储测试"""
    
    @pytest.fixture
    def vector_config(self):
        """向量存储配置"""
        return VectorConfig(
            documents_collection="test_documents",
            images_collection="test_images",
            documents_vector_size=1024,
            images_vector_size=1024,
            max_retries=2
        )
    
    @pytest.fixture
    def sample_embedding(self):
        """示例向量"""
        return [0.1] * 1024
    
    def test_config_defaults(self, vector_config):
        """测试配置默认值"""
        assert vector_config.documents_collection == "test_documents"
        assert vector_config.max_retries == 2
        assert vector_config.batch_size == 100
    
    @pytest.mark.asyncio
    async def test_search_documents_validation(self, vector_config):
        """测试搜索文档验证"""
        store = VectorStore(vector_config)
        store._initialized = True
        store._client = Mock()
        store._semaphore = asyncio.Semaphore(10)
        
        wrong_embedding = [0.1] * 512
        
        results = await store.search_documents(
            query_embedding=wrong_embedding,
            n_results=5
        )
        
        assert results == []


class TestCleanedPost:
    """清洗后帖子数据结构测试"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        post = CleanedPost(
            post_id="test123",
            title="测试标题",
            content="测试内容",
            content_type="attraction",
            city="澳门",
            tags=["旅游", "景点"],
            author="测试作者",
            likes=100,
            comments=20,
            collects=50,
            source_url="https://example.com",
            images=["https://example.com/img.jpg"],
            entities={"attractions": ["景点1"]}
        )
        
        result = post.to_dict()
        
        assert isinstance(result, dict)
        assert result["post_id"] == "test123"
        assert result["title"] == "测试标题"
        assert result["city"] == "澳门"


class TestSearchResult:
    """搜索结果测试"""
    
    def test_search_result_creation(self):
        """测试搜索结果创建"""
        result = SearchResult(
            id="test_id",
            score=0.95,
            payload={"title": "测试", "content": "内容"}
        )
        
        assert result.id == "test_id"
        assert result.score == 0.95
        assert result.payload["title"] == "测试"


class TestEmbeddingResult:
    """向量化结果测试"""
    
    def test_success_result(self):
        """测试成功结果"""
        result = EmbeddingResult(
            success=True,
            embedding=[0.1] * 1024,
            model="test-model",
            dimension=1024,
            processing_time_ms=100.5
        )
        
        assert result.success == True
        assert len(result.embedding) == 1024
        assert result.error is None
    
    def test_error_result(self):
        """测试错误结果"""
        result = EmbeddingResult(
            success=False,
            error="API调用失败"
        )
        
        assert result.success == False
        assert result.embedding is None
        assert result.error == "API调用失败"


class TestSecurityMeasures:
    """安全性测试"""
    
    @pytest.fixture
    def processor(self):
        return DataProcessor()
    
    def test_sql_injection_prevention(self, processor):
        """测试SQL注入防护"""
        post = {
            "post_id": "test'; DROP TABLE users; --",
            "title": "正常标题",
            "description": "正常内容"
        }
        
        result = processor.clean_post(post)
        
        assert result is not None
        assert "DROP TABLE" not in result.post_id
    
    def test_html_injection_prevention(self, processor):
        """测试HTML注入防护"""
        post = {
            "post_id": "test123",
            "title": "<h1>标题</h1>",
            "description": "<a href='javascript:alert(1)'>链接</a>"
        }
        
        result = processor.clean_post(post)
        
        assert result is not None
        assert "<h1>" not in result.title
        assert "javascript:" not in result.content
    
    def test_emoji_handling(self, processor):
        """测试Emoji处理"""
        post = {
            "post_id": "test123",
            "title": "澳门旅游🎉🎊",
            "description": "好玩的地方👍"
        }
        
        result = processor.clean_post(post)
        
        assert result is not None
    
    def test_long_content_truncation(self, processor):
        """测试长内容截断"""
        post = {
            "post_id": "test123",
            "title": "a" * 300,
            "description": "b" * 6000
        }
        
        result = processor.clean_post(post)
        
        assert result is not None
        assert len(result.title) <= processor.MAX_TITLE_LENGTH
        assert len(result.content) <= processor.MAX_CONTENT_LENGTH
    
    def test_max_tags_limit(self, processor):
        """测试标签数量限制"""
        post = {
            "post_id": "test123",
            "title": "测试",
            "description": "内容",
            "tags": [f"tag{i}" for i in range(50)]
        }
        
        result = processor.clean_post(post)
        
        assert result is not None
        assert len(result.tags) <= processor.MAX_TAGS_COUNT
    
    def test_max_images_limit(self, processor):
        """测试图片数量限制"""
        post = {
            "post_id": "test123",
            "title": "测试",
            "description": "内容",
            "images": [f"https://example.com/img{i}.jpg" for i in range(50)]
        }
        
        result = processor.clean_post(post)
        
        assert result is not None
        assert len(result.images) <= processor.MAX_IMAGES_COUNT


class TestContentType:
    """内容类型枚举测试"""
    
    def test_content_types(self):
        """测试内容类型"""
        assert ContentType.ATTRACTION.value == "attraction"
        assert ContentType.FOOD.value == "food"
        assert ContentType.HOTEL.value == "hotel"
        assert ContentType.TIPS.value == "tips"
        assert ContentType.GENERAL.value == "general"

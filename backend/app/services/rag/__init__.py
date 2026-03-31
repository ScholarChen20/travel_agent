"""
RAG检索服务模块

模块说明：
- credibility_calculator: 置信度评分
- hybrid_vector_store: 混合向量存储（密集向量）
- hybrid_rag_service: 混合检索服务（推荐使用）
- simple_rag_service: 简单文本检索（无向量化依赖）
- data_importer: 数据导入服务

已废弃（保留兼容）：
- rag_service.py
- vector_store.py
- embedding_service.py
- data_processor.py
"""

# 推荐使用的模块
from .credibility_calculator import (
    CredibilityCalculator,
    CredibilityScore,
    calculate_credibility,
    is_credible_post
)
from .hybrid_vector_store import (
    HybridVectorStore,
    SearchResult,
    PostPayload,
    ImagePayload,
    VectorConfig,
    get_hybrid_vector_store
)
from .hybrid_rag_service import (
    HybridRAGService,
    HybridRAGConfig,
    RAGSearchResult,
    get_hybrid_rag_service
)
from .simple_rag_service import (
    SimpleRAGService,
    SimpleRAGConfig,
    SearchResult as SimpleSearchResult,
    get_simple_rag_service
)
from .data_importer import (
    RAGDataImporter,
    ImportConfig,
    ImportResult,
    import_rag_data
)

__all__ = [
    # 置信度评分
    "CredibilityCalculator",
    "CredibilityScore",
    "calculate_credibility",
    "is_credible_post",

    # 混合向量存储（推荐）
    "HybridVectorStore",
    "SearchResult",
    "PostPayload",
    "ImagePayload",
    "VectorConfig",
    "get_hybrid_vector_store",

    # 混合检索服务（推荐）
    "HybridRAGService",
    "HybridRAGConfig",
    "RAGSearchResult",
    "get_hybrid_rag_service",

    # 简单检索服务（无向量化）
    "SimpleRAGService",
    "SimpleRAGConfig",
    "SimpleSearchResult",
    "get_simple_rag_service",

    # 数据导入
    "RAGDataImporter",
    "ImportConfig",
    "ImportResult",
    "import_rag_data",
]
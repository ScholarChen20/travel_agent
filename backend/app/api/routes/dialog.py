"""
对话管理路由

提供以下API：
- POST /api/dialog/chat - 多轮对话接口
- GET /api/dialog/sessions - 列出对话会话
- GET /api/dialog/sessions/{session_id} - 获取会话历史
- DELETE /api/dialog/sessions/{session_id} - 删除会话
- WebSocket /api/dialog/ws/{session_id} - WebSocket实时对话
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from loguru import logger
import json
import asyncio
from asyncio import Queue

from ...services.dialog_service import get_dialog_service
from ...agents.trip_planner_agent import get_conversational_planner
from ...middleware.auth_middleware import get_current_user, CurrentUser, verify_token


router = APIRouter(prefix="/dialog", tags=["对话管理"])

# ========== SSE 会话队列（内存级别，每个 session 一个队列）==========
_session_queues: dict[str, Queue] = {}


def get_session_queue(session_id: str) -> Queue:
    if session_id not in _session_queues:
        _session_queues[session_id] = Queue()
    return _session_queues[session_id]


async def get_current_user_sse(
    token: Optional[str] = Query(None),
) -> CurrentUser:
    """SSE 专用认证：支持 query param 传 token（EventSource 不支持自定义请求头）"""
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证凭证")
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="认证凭证无效或已过期")
    return user


# ========== 请求/响应模型 ==========

class ChatRequest(BaseModel):
    """对话请求"""
    session_id: Optional[str] = Field(None, description="会话ID（可选，不提供则创建新会话）")
    message: str = Field(..., description="用户消息")
    voice_data: Optional[str] = Field(None, description="语音数据（Base64编码，可选）")


class ChatResponse(BaseModel):
    """对话响应"""
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="助手回复")
    intent: str = Field(..., description="识别的意图")
    suggestions: List[str] = Field(default=[], description="建议回复")


class SessionListResponse(BaseModel):
    """会话列表响应"""
    total: int = Field(..., description="总数")
    sessions: List[dict] = Field(..., description="会话列表")


class SessionDetailResponse(BaseModel):
    """会话详情响应"""
    session_id: str = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")
    context: dict = Field(..., description="会话上下文")
    message_count: int = Field(..., description="消息数量")
    messages: List[dict] = Field(..., description="消息列表")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str = Field(..., description="消息内容")


class UpdateSessionRequest(BaseModel):
    """更新会话请求"""
    title: str = Field(..., description="会话标题", max_length=50)


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    initial_context: dict = Field(default={}, description="初始上下文")


class CreateSessionResponse(BaseModel):
    """创建会话响应"""
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="消息")


# ========== API端点 ==========

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    多轮对话接口

    支持：
    - 自动创建新会话或使用现有会话
    - 意图识别和智能路由
    - 上下文理解
    - 工具调用日志记录
    """
    try:
        dialog_service = get_dialog_service()

        # 如果没有提供session_id，创建新会话
        session_id = request.session_id
        if not session_id:
            session_id = await dialog_service.create_session(
                user_id=current_user.id,
                initial_context={}
            )
            logger.info(f"创建新会话: {session_id} (用户: {current_user.username})")

        # 获取对话式Agent
        conversational_planner = get_conversational_planner(dialog_service)

        # 处理对话
        response = await conversational_planner.chat(
            session_id=session_id,
            user_id=current_user.id,
            user_message=request.message
        )

        logger.info(f"对话处理完成: {session_id} (意图: {response['intent']})")

        # 将响应推入 SSE 队列，供 SSE 连接实时推送
        queue = get_session_queue(session_id)
        await queue.put({
            "type": "message",
            "session_id": session_id,
            "message": response["message"],
            "intent": response["intent"],
            "suggestions": response.get("suggestions", [])
        })

        return ChatResponse(**response)

    except Exception as e:
        logger.error(f"对话处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话处理失败: {str(e)}"
        )


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest = CreateSessionRequest(),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建新的对话会话

    用于手动创建会话，通常在开始新对话时调用
    """
    try:
        dialog_service = get_dialog_service()

        session_id = await dialog_service.create_session(
            user_id=current_user.id,
            initial_context=request.initial_context
        )

        logger.info(f"创建新会话: {session_id} (用户: {current_user.username})")

        # 删除redis中的会话缓存
        dialog_service.delete_session_cache(user_id=current_user.id)

        return CreateSessionResponse(
            session_id=session_id,
            message="会话创建成功"
        )

    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    is_active: Optional[bool] = None,
    limit: int = 20,
    skip: int = 0,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    列出用户的对话会话

    支持按活跃状态筛选和分页
    """
    try:
        dialog_service = get_dialog_service()

        sessions = await dialog_service.list_user_sessions(
            user_id=current_user.id,
            is_active=is_active,
            limit=limit,
            skip=skip
        )

        return SessionListResponse(
            total=len(sessions),
            sessions=sessions
        )

    except Exception as e:
        logger.error(f"列出会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="列出会话失败"
        )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取会话详情

    包含会话信息和消息历史
    """
    try:
        dialog_service = get_dialog_service()

        # 获取会话上下文
        context = await dialog_service.get_session_context(session_id)

        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        # 验证权限
        if context["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此会话"
            )

        return SessionDetailResponse(**context)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会话详情失败"
        )


@router.patch("/sessions/{session_id}", response_model=MessageResponse)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新会话标题"""
    try:
        dialog_service = get_dialog_service()
        success = await dialog_service.update_session_title(
            session_id=session_id,
            user_id=current_user.id,
            title=request.title
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        return MessageResponse(message="标题已更新")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新会话标题失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新失败")


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def delete_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除会话

    只能删除自己的会话
    """
    try:
        dialog_service = get_dialog_service()

        success = await dialog_service.delete_session(
            session_id=session_id,
            user_id=current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        logger.info(f"会话已删除: {session_id} (用户: {current_user.username})")

        return MessageResponse(message="会话已删除")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除会话失败"
        )


@router.get("/sessions/{session_id}/logs")
async def get_session_logs(
    session_id: str,
    limit: int = 50,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取会话的工具调用日志

    用于调试和可视化
    """
    try:
        dialog_service = get_dialog_service()

        # 验证会话权限
        context = await dialog_service.get_session_context(session_id)
        if not context or context["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此会话"
            )

        # 获取工具调用日志
        logs = await dialog_service.get_session_tool_logs(session_id, limit)

        return {
            "session_id": session_id,
            "total": len(logs),
            "logs": logs
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取工具调用日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取工具调用日志失败"
        )


# ========== SSE 端点 ==========

@router.get("/sse/{session_id}")
async def sse_endpoint(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user_sse)
):
    """
    SSE 实时对话端点

    前端建立 SSE 连接后，每当 POST /chat 处理完毕，
    响应会通过此连接实时推送到前端。
    每 25 秒发一次心跳防止连接超时。
    """
    # 验证会话归属
    dialog_service = get_dialog_service()
    context = await dialog_service.get_session_context(session_id)
    if not context or context["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此会话")

    queue = get_session_queue(session_id)

    async def event_generator():
        # 发送连接成功事件
        yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id}, ensure_ascii=False)}\n\n"
        while True:
            try:
                data = await asyncio.wait_for(queue.get(), timeout=25)
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            except asyncio.TimeoutError:
                # 心跳，保持连接
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


# ========== WebSocket端点 ==========

class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """连接WebSocket"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket连接建立: {session_id}")

    def disconnect(self, session_id: str):
        """断开WebSocket"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket连接断开: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        """发送消息"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket实时对话端点

    支持：
    - 双向通信
    - 流式响应
    - 心跳检测
    """
    await manager.connect(session_id, websocket)

    try:
        # 发送欢迎消息
        await manager.send_message(session_id, {
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket连接成功"
        })

        while True:
            # 接收客户端消息
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)

                # 处理不同类型的消息
                if message_data.get("type") == "ping":
                    # 心跳响应
                    await manager.send_message(session_id, {
                        "type": "pong",
                        "timestamp": message_data.get("timestamp")
                    })

                elif message_data.get("type") == "chat":
                    # 对话消息
                    user_message = message_data.get("message")
                    user_id = message_data.get("user_id")

                    if not user_message or not user_id:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "message": "缺少必要参数"
                        })
                        continue

                    # 发送处理中状态
                    await manager.send_message(session_id, {
                        "type": "processing",
                        "message": "正在处理您的消息..."
                    })

                    # 处理对话
                    dialog_service = get_dialog_service()
                    conversational_planner = get_conversational_planner(dialog_service)

                    response = await conversational_planner.chat(
                        session_id=session_id,
                        user_id=user_id,
                        user_message=user_message
                    )

                    # 发送响应
                    await manager.send_message(session_id, {
                        "type": "response",
                        **response
                    })

                else:
                    await manager.send_message(session_id, {
                        "type": "error",
                        "message": "未知的消息类型"
                    })

            except json.JSONDecodeError:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": "无效的JSON格式"
                })
            except Exception as e:
                logger.error(f"WebSocket消息处理失败: {str(e)}")
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": f"处理失败: {str(e)}"
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket客户端断开连接: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        manager.disconnect(session_id)

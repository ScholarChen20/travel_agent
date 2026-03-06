# API 使用指南 - v2.0

**文档版本**: v2.0
**更新日期**: 2026-03-06
**最后更新**: 根据实际API实现同步更新，新增黑名单管理、管理员功能、实时信息、语音交互、多语言支持、离线功能等API

本文档说明当前系统的所有可用API端点及其使用方法。

---

## 基础信息

**Base URL**: `http://localhost:8000`
**API文档**: `http://localhost:8000/docs` (Swagger UI)
**ReDoc文档**: `http://localhost:8000/redoc`

---

## 统一响应格式

所有API响应遵循统一格式：

```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {...}
}
```

**字段说明**:
- `code`: 响应状态码（200表示成功，4xx表示客户端错误，5xx表示服务器错误）
- `msg`: 响应消息（成功或错误描述）
- `data`: 响应数据（可选，成功响应时返回具体数据）

---

## 1. 认证相关 API (`/api/auth`)

### 1.1 获取验证码
```http
GET /api/auth/captcha
```

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "session_id": "string",
    "image_base64": "data:image/png;base64,...",
    "expires_in": 300
  }
}
```

---

### 1.2 用户注册
```http
POST /api/auth/register
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Test@123456",
  "nickname": "旅行者",
  "captcha_code": "1234",
  "captcha_session_id": "xxx"
}
```

**响应**:
```json
{
  "code": 201,
  "msg": "注册成功",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 604800,
    "expires_at": "2026-01-22T12:00:00",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "role": "user",
      "is_verified": false
    }
  }
}
```

**防刷机制**:
- IP国家限制：仅允许本国IP注册
- IP频率限制：每小时最多10次注册尝试
- 设备ID检查：使用布隆过滤器快速检测已注册设备
- Redis黑名单精确检查：设备ID在5分钟内注册过则拒绝

---

### 1.3 用户登录
```http
POST /api/auth/login
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "testuser",
  "password": "Test@123456",
  "captcha_code": "1234",
  "captcha_session_id": "xxx"
}
```

**响应**: 同注册响应

**限流**: 5次失败后锁定5分钟

**设备黑名单检查**: 登录前检查设备ID是否在黑名单中

---

### 1.4 用户登出
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "登出成功",
  "data": null
}
```

---

### 1.5 刷新Token
```http
POST /api/auth/refresh
Authorization: Bearer <token>
```

**响应**: 返回新的Token

---

### 1.6 忘记密码
```http
POST /api/auth/forgot-password
Content-Type: application/json
```

**请求体**:
```json
{
  "email": "test@example.com"
}
```

---

### 1.7 重置密码
```http
POST /api/auth/reset-password
Content-Type: application/json
```

**请求体**:
```json
{
  "token": "reset_token_xxx",
  "new_password": "NewPassword@123"
}
```

---

## 2. 用户管理 API (`/api/user`)

> 所有端点都需要认证

### 2.1 获取当前用户资料
```http
GET /api/user/profile
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "avatar_url": "/storage/avatars/xxx.jpg",
    "is_verified": false,
    "is_active": true,
    "created_at": "2026-01-15T12:00:00",
    "last_login_at": "2026-01-15T13:00:00",
    "profile": {
      "full_name": "旅行者",
      "travel_preferences": ["自然风光", "美食"],
      "visited_cities": ["北京", "上海"],
      "travel_stats": {
        "total_trips": 5,
        "total_cities": 3
      }
    }
  }
}
```

---

### 2.2 更新用户资料
```http
PUT /api/user/profile
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体** (所有字段可选):
```json
{
  "username": "newusername",
  "email": "newemail@example.com",
  "travel_preferences": ["海滨", "历史文化"],
  "full_name": "新昵称",
  "gender": "male",
  "birth_date": "1990-01-01",
  "location": "北京"
}
```

---

### 2.3 上传头像
```http
POST /api/user/avatar
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**表单数据**:
- `file`: 图片文件 (JPEG/PNG/GIF, 最大5MB)

**响应**:
```json
{
  "code": 200,
  "msg": "上传头像成功",
  "data": {
    "avatar_url": "/storage/avatars/avatar_1_xxx.jpg"
  }
}
```

---

### 2.4 获取旅行统计
```http
GET /api/user/stats
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "total_trips": 5,
    "completed_trips": 3,
    "favorite_trips": 2,
    "total_cities": 4
  }
}
```

---

### 2.5 获取访问过的城市
```http
GET /api/user/visited-cities
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "cities": ["北京", "上海", "杭州", "成都"]
  }
}
```

---

### 2.6 更新访问过的城市
```http
PUT /api/user/visited-cities
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "cities": ["北京", "上海", "杭州", "成都"]
}
```

---

### 2.7 修改密码
```http
POST /api/user/change-password
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "old_password": "OldPassword@123",
  "new_password": "NewPassword@456"
}
```

---

## 3. 旅行计划 API (`/api/trip`)

### 3.1 生成旅行计划（支持可选认证）
```http
POST /api/trip/plan
Authorization: Bearer <token>  # 可选，匿名用户不需要
Content-Type: application/json
```

**请求体**:
```json
{
  "city": "北京",
  "start_date": "2026-02-01",
  "end_date": "2026-02-03",
  "travel_days": 3
}
```

**响应（匿名用户）**:
```json
{
  "code": 200,
  "msg": "旅行计划生成成功",
  "data": {
    "city": "北京",
    "days": [
      {
        "day": 1,
        "date": "2026-02-01",
        "weather": {...},
        "attractions": [...],
        "meals": {...},
        "hotel": {...}
      }
    ]
  }
}
```

**响应（登录用户）**:
```json
{
  "code": 200,
  "msg": "旅行计划生成成功 (已保存)",
  "data": {
    "city": "北京",
    "days": [...],
    "plan_id": "plan_xxx",
    "session_id": "session_xxx"
  }
}
```

---

### 3.2 健康检查
```http
GET /api/trip/health
```

---

## 4. 计划管理 API (`/api/plans`)

> 所有端点都需要认证

### 4.1 列出用户计划
```http
GET /api/plans?city=北京&is_favorite=true&limit=20&skip=0
Authorization: Bearer <token>
```

**查询参数**:
- `city` (可选): 城市筛选
- `is_favorite` (可选): 收藏筛选
- `is_completed` (可选): 完成状态筛选
- `limit` (可选): 返回数量，默认20
- `skip` (可选): 跳过数量，默认0

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "total": 10,
    "plans": [
      {
        "plan_id": "plan_xxx",
        "city": "北京",
        "start_date": "2026-02-01",
        "days": [...],
        "is_favorite": true,
        "is_completed": false,
        "created_at": "2026-01-15T12:00:00"
      }
    ]
  }
}
```

---

### 4.2 获取计划详情
```http
GET /api/plans/{plan_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "plan_id": "plan_xxx",
    "user_id": 1,
    "session_id": "session_xxx",
    "city": "北京",
    "start_date": "2026-02-01",
    "days": [...],
    "weather_info": {...},
    "budget": 5000.0,
    "preferences": {...},
    "is_favorite": false,
    "is_completed": false,
    "created_at": "2026-01-15T12:00:00",
    "updated_at": "2026-01-15T12:00:00"
  }
}
```

---

### 4.3 更新计划
```http
PUT /api/plans/{plan_id}
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体** (所有字段可选):
```json
{
  "days": [...],
  "budget": 6000.0,
  "preferences": {...}
}
```

---

### 4.4 切换收藏状态
```http
POST /api/plans/{plan_id}/favorite
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "计划已收藏",
  "data": {
    "is_favorite": true
  }
}
```

---

### 4.5 标记完成状态
```http
POST /api/plans/{plan_id}/complete
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "is_completed": true
}
```

---

### 4.6 删除计划
```http
DELETE /api/plans/{plan_id}
Authorization: Bearer <token>
```

---

### 4.7 导出计划
```http
GET /api/plans/{plan_id}/export?format=json
Authorization: Bearer <token>
```

**查询参数**:
- `format`: 导出格式，支持 `json` (当前仅JSON，PDF待实现)

---

## 5. 景点查询 API (`/api/poi`)

### 5.1 搜索POI
```http
GET /api/poi/search?keywords=故宫&city=北京
```

**查询参数**:
- `keywords`: 搜索关键词
- `city`: 城市名称（默认"北京"）

---

### 5.2 获取POI详情
```http
GET /api/poi/detail/{poi_id}
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取POI详情成功",
  "data": {
    "poi_id": "poi_123",
    "name": "故宫",
    "address": "北京市东城区景山前街4号",
    "phone": "010-85007421",
    "opening_hours": "08:30-17:00",
    "rating": 4.8,
    "image_url": "https://..."
  }
}
```

---

### 5.3 获取景点图片
```http
GET /api/poi/photo?name=故宫
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取图片成功",
  "data": {
    "name": "故宫",
    "photo_url": "https://images.unsplash.com/..."
  }
}
```

---

## 6. 地图服务 API (`/api/map`)

### 6.1 天气查询
```http
GET /api/map/weather?city=北京
```

**响应**:
```json
{
  "code": 200,
  "msg": "天气查询成功",
  "data": {
    "city": "北京",
    "temperature": 15,
    "weather": "晴",
    "humidity": 45,
    "wind": "东北风3级"
  }
}
```

---

### 6.2 搜索POI
```http
GET /api/map/poi?keywords=故宫&city=北京&citylimit=true
```

**查询参数**:
- `keywords`: 搜索关键词
- `city`: 城市名称
- `citylimit`: 是否限制在城市范围内（默认true）

---

### 6.3 规划路线
```http
POST /api/map/route
Content-Type: application/json
```

**请求体**:
```json
{
  "origin_address": "北京市朝阳区",
  "destination_address": "北京市海淀区",
  "origin_city": "北京",
  "destination_city": "北京",
  "route_type": "driving"
}
```

---

### 6.4 健康检查
```http
GET /api/map/health
```

---

## 7. 首页仪表盘 API (`/api/dashboard`)

> 所有端点都需要认证

### 7.1 获取首页综合指标
```http
GET /api/dashboard/overview
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "user_stats": {
      "total_users": 1000,
      "active_users": 800,
      "new_users_today": 10
    },
    "content_stats": {
      "total_plans": 500,
      "total_posts": 200,
      "total_comments": 150
    },
    "business_stats": {
      "plan_creation_rate": 50,
      "user_retention_rate": 75
    }
  }
}
```

---

### 7.2 获取用户统计数据
```http
GET /api/dashboard/user-stats
Authorization: Bearer <token>
```

---

### 7.3 获取内容统计数据
```http
GET /api/dashboard/content-stats
Authorization: Bearer <token>
```

---

### 7.4 获取业务指标数据
```http
GET /api/dashboard/business-stats
Authorization: Bearer <token>
```

---

### 7.5 获取业务趋势数据
```http
GET /api/dashboard/business-trend?start_date=2026-01-01&end_date=2026-01-31
Authorization: Bearer <token>
```

**查询参数**:
- `start_date`: 开始日期（YYYY-MM-DD）
- `end_date`: 结束日期（YYYY-MM-DD）

---

## 8. 对话管理 API (`/api/dialog`)

> 所有端点都需要认证

### 8.1 多轮对话接口
```http
POST /api/dialog/chat
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "session_id": "optional_session_id",
  "message": "用户消息",
  "voice_data": "optional_base64_voice_data"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "对话处理完成",
  "data": {
    "session_id": "session_xxx",
    "message": "助手响应消息",
    "intent": "plan_trip",
    "suggestions": ["查看天气", "添加景点"]
  }
}
```

---

### 8.2 创建对话会话
```http
POST /api/dialog/sessions
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "initial_context": {}
}
```

**响应**:
```json
{
  "code": 201,
  "msg": "会话创建成功",
  "data": {
    "session_id": "session_xxx"
  }
}
```

---

### 8.3 列出对话会话
```http
GET /api/dialog/sessions?is_active=true&limit=20&skip=0
Authorization: Bearer <token>
```

**查询参数**:
- `is_active`: 是否活跃（可选）
- `limit`: 返回数量（默认20）
- `skip`: 跳过数量（默认0）

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total": 5,
    "sessions": [
      {
        "session_id": "session_xxx",
        "title": "北京旅行计划",
        "is_active": true,
        "created_at": "2026-01-15T12:00:00"
      }
    ]
  }
}
```

---

### 8.4 获取会话详情
```http
GET /api/dialog/sessions/{session_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "session_id": "session_xxx",
    "user_id": 1,
    "title": "北京旅行计划",
    "messages": [...],
    "context": {...}
  }
}
```

---

### 8.5 更新会话
```http
PATCH /api/dialog/sessions/{session_id}
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "title": "新的会话标题"
}
```

---

### 8.6 删除会话
```http
DELETE /api/dialog/sessions/{session_id}
Authorization: Bearer <token>
```

---

### 8.7 获取会话工具调用日志
```http
GET /api/dialog/sessions/{session_id}/logs?limit=50
Authorization: Bearer <token>
```

**查询参数**:
- `limit`: 返回数量（默认50）

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "session_id": "session_xxx",
    "total": 10,
    "logs": [
      {
        "tool_name": "get_weather",
        "parameters": {"city": "北京"},
        "result": {...},
        "timestamp": "2026-01-15T12:00:00"
      }
    ]
  }
}
```

---

### 8.8 SSE实时对话
```http
GET /api/dialog/sse/{session_id}?token=xxx
```

**查询参数**:
- `token`: JWT Token（通过query参数传递，因为EventSource不支持自定义请求头）

**响应**: Server-Sent Events流

---

### 8.9 WebSocket实时对话
```http
WS /api/dialog/ws/{session_id}
```

**WebSocket消息格式**:
```json
{
  "type": "chat",
  "message": "用户消息",
  "user_id": 1
}
```

**响应类型**:
- `connected`: 连接成功
- `pong`: 心跳响应
- `processing`: 处理中
- `response`: 助手响应
- `error`: 错误消息

---

## 9. 社交功能 API (`/api/social`)

> 所有端点都需要认证

### 9.1 创建帖子
```http
POST /api/social/posts
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "title": "帖子标题",
  "content": "帖子内容",
  "media_urls": ["image_url_1", "image_url_2"],
  "tags": ["旅行", "美食"],
  "location": "北京",
  "trip_plan_id": "plan_xxx"
}
```

**响应**:
```json
{
  "code": 201,
  "msg": "帖子创建成功",
  "data": {
    "post_id": "post_xxx"
  }
}
```

---

### 9.2 上传媒体文件
```http
POST /api/social/posts/media
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**表单数据**:
- `file`: 图片/视频文件

**文件限制**:
- 图片：JPEG, PNG, GIF（最大5MB）
- 视频：MP4（最大50MB）

**响应**:
```json
{
  "code": 200,
  "msg": "媒体文件上传成功",
  "data": {
    "url": "https://storage.example.com/media_xxx.jpg",
    "thumbnail_url": "https://storage.example.com/thumb_xxx.jpg"
  }
}
```

---

### 9.3 获取Feed流
```http
GET /api/social/posts?limit=20&offset=0
Authorization: Bearer <token>
```

**查询参数**:
- `limit`: 返回数量（默认20）
- `offset`: 偏移量（默认0）

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total": 50,
    "posts": [...]
  }
}
```

---

### 9.4 获取帖子详情
```http
GET /api/social/posts/{post_id}
Authorization: Bearer <token>
```

---

### 9.5 点赞/取消点赞
```http
POST /api/social/posts/{post_id}/like
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "已点赞",
  "data": {
    "liked": true
  }
}
```

---

### 9.6 发表评论
```http
POST /api/social/posts/{post_id}/comments
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "content": "评论内容",
  "parent_id": "optional_parent_comment_id"
}
```

**响应**:
```json
{
  "code": 201,
  "msg": "评论发表成功",
  "data": {
    "comment_id": "comment_xxx",
    "id": "comment_xxx",
    "content": "评论内容",
    "user_id": 1,
    "username": "testuser",
    "user_avatar": "/storage/avatars/xxx.jpg",
    "post_id": "post_xxx",
    "parent_id": "optional_parent_comment_id",
    "created_at": "2026-01-15T12:00:00"
  }
}
```

---

### 9.7 获取评论列表
```http
GET /api/social/posts/{post_id}/comments?limit=50&offset=0
Authorization: Bearer <token>
```

**查询参数**:
- `limit`: 返回数量（默认50）
- `offset`: 偏移量（默认0）

---

### 9.8 关注/取消关注
```http
POST /api/social/users/{user_id}/follow
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "已关注",
  "data": {
    "following": true
  }
}
```

---

### 9.9 获取用户主页帖子
```http
GET /api/social/users/{user_id}/posts?limit=20&offset=0
Authorization: Bearer <token>
```

**查询参数**:
- `limit`: 返回数量（默认20）
- `offset`: 偏移量（默认0）

---

### 9.10 获取热门标签
```http
GET /api/social/tags?limit=20
Authorization: Bearer <token>
```

**查询参数**:
- `limit`: 返回数量（默认20）

---

### 9.11 按标签查询帖子
```http
GET /api/social/tags/{tag_name}/posts?limit=20&offset=0
Authorization: Bearer <token>
```

**查询参数**:
- `limit`: 返回数量（默认20）
- `offset`: 偏移量（默认0）

---

### 9.12 获取抖音热点话题
```http
GET /api/social/hot-topics?limit=20
```

**查询参数**:
- `limit`: 返回数量（默认20）

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total": 20,
    "topics": [
      {
        "rank": 1,
        "title": "话题标题",
        "hot_value": 1000000
      }
    ]
  }
}
```

---

## 10. 智能推荐系统 API (`/api/recommendations`)

> 需要认证

### 10.1 获取个性化推荐
```http
GET /api/recommendations/?user_id=1&preferences=自然风光,美食&location=北京&limit=10
Authorization: Bearer <token>
```

**查询参数**:
- `user_id`: 用户ID（可选）
- `preferences`: 兴趣标签，逗号分隔（可选）
- `location`: 当前位置（可选）
- `limit`: 返回数量（默认10）

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "attractions": [
      {
        "id": "attraction_1",
        "name": "故宫",
        "rating": 4.8,
        "distance": 2.5,
        "tags": ["历史文化", "古建筑"],
        "image_url": "https://example.com/gugong.jpg"
      }
    ],
    "restaurants": [
      {
        "id": "restaurant_1",
        "name": "全聚德",
        "rating": 4.5,
        "cuisine": "北京烤鸭",
        "price_range": "¥200-300"
      }
    ],
    "hotels": [
      {
        "id": "hotel_1",
        "name": "北京饭店",
        "rating": 4.7,
        "price": 800,
        "distance": 3.0
      }
    ]
  }
}
```

---

### 10.2 生成个性化推荐
```http
POST /api/recommendations/generate
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "user_id": 1,
  "preferences": ["自然风光", "美食"],
  "location": "北京",
  "limit": 10
}
```

---

## 11. 预算管理 API (`/api/budget`)

> 需要认证

### 11.1 创建预算
```http
POST /api/budget/create
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "trip_id": "trip_xxx",
  "total_budget": 5000,
  "categories": [
    {"name": "住宿", "budget": 2000},
    {"name": "餐饮", "budget": 1500},
    {"name": "交通", "budget": 1000},
    {"name": "门票", "budget": 500}
  ]
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "预算创建成功",
  "data": {
    "budget_id": "budget_xxx",
    "trip_id": "trip_xxx",
    "total_budget": 5000,
    "remaining_budget": 5000,
    "categories": [...]
  }
}
```

---

### 11.2 添加消费记录
```http
POST /api/budget/expense/add
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "budget_id": "budget_xxx",
  "category": "餐饮",
  "amount": 200,
  "description": "午餐",
  "date": "2026-03-15"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "支出添加成功",
  "data": {
    "expense_id": "expense_xxx",
    "budget_id": "budget_xxx",
    "amount": 200,
    "remaining_budget": 4800
  }
}
```

---

### 11.3 获取预算统计
```http
GET /api/budget/stats?user_id=1
Authorization: Bearer <token>
```

**查询参数**:
- `user_id`: 用户ID

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total_budget": 5000,
    "used_budget": 200,
    "remaining_budget": 4800,
    "categories": [
      {
        "name": "住宿",
        "budget": 2000,
        "used": 0,
        "remaining": 2000
      }
    ]
  }
}
```

---

### 11.4 获取预算概览
```http
GET /api/budget/overview?user_id=1
Authorization: Bearer <token>
```

**查询参数**:
- `user_id`: 用户ID

---

## 12. 实时信息服务 API (`/api/real-time`)

> 需要认证

### 12.1 获取实时信息
```http
POST /api/real-time/info
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "user_id": 1,
  "location": "北京",
  "type": "all"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "traffic": [...],
    "weather": {...},
    "activities": [...]
  }
}
```

---

### 12.2 获取实时信息概览
```http
GET /api/real-time/overview?user_id=1&location=北京
Authorization: Bearer <token>
```

**查询参数**:
- `user_id`: 用户ID
- `location`: 当前位置（可选）

---

## 13. 离线功能 API (`/api/offline`)

> 需要认证

### 13.1 下载离线地图
```http
POST /api/offline/map/download
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "city": "北京",
  "map_type": "standard"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "download_url": "https://example.com/beijing_map.zip",
    "file_size": 1024,
    "version": "1.0"
  }
}
```

---

### 13.2 同步离线数据
```http
POST /api/offline/data/sync
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "trip_id": "trip_xxx",
  "data": {...}
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "同步成功",
  "data": {
    "sync_id": "sync_xxx",
    "timestamp": "2026-03-06T12:00:00"
  }
}
```

---

### 13.3 获取离线数据
```http
GET /api/offline/data/{user_id}?sync_id=sync_xxx
Authorization: Bearer <token>
```

**查询参数**:
- `sync_id`: 同步ID（可选，不指定则返回最新数据）

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "user_id": 1,
    "trips": [...],
    "maps": [...],
    "last_sync": "2026-03-06T12:00:00"
  }
}
```

---

## 14. 多语言支持 API (`/api/translate`)

> 需要认证

### 14.1 文本翻译
```http
POST /api/translate/text
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "text": "Hello",
  "from": "en",
  "to": "zh"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "翻译成功",
  "data": {
    "original": "Hello",
    "translated": "你好",
    "from": "en",
    "to": "zh"
  }
}
```

---

### 14.2 语音翻译
```http
POST /api/translate/voice
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "voice_data": "base64_encoded_audio",
  "from": "en",
  "to": "zh"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "翻译成功",
  "data": {
    "original": "Hello",
    "translated": "你好",
    "from": "en",
    "to": "zh",
    "audio_url": "https://example.com/translated_audio.mp3"
  }
}
```

---

### 14.3 获取支持的语言列表
```http
GET /api/translate/languages
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "code": "zh",
      "name": "中文"
    },
    {
      "code": "en",
      "name": "English"
    }
  ]
}
```

---

## 15. 语音交互 API (`/api/voice`)

> 需要认证

### 15.1 语音识别
```http
POST /api/voice/recognize
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "audio_data": "base64_encoded_audio",
  "language": "zh-CN"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "识别成功",
  "data": {
    "text": "你好",
    "confidence": 0.95
  }
}
```

---

### 15.2 语音合成
```http
POST /api/voice/synthesize
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "text": "你好，欢迎使用智能旅行助手",
  "voice": "female",
  "language": "zh-CN"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "合成成功",
  "data": {
    "audio_url": "https://example.com/synthesized_audio.mp3",
    "duration": 3.5
  }
}
```

---

### 15.3 处理语音命令
```http
POST /api/voice/command
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "voice_data": "base64_encoded_audio",
  "language": "zh-CN"
}
```

**响应**:
```json
{
  "code": 200,
  "msg": "语音指令处理完成",
  "data": {
    "intent": "query_weather",
    "parameters": {
      "city": "北京"
    },
    "response": "北京今天天气晴朗，温度15-25摄氏度"
  }
}
```

---

## 16. 黑名单管理 API (`/api/blacklist`)

> 需要管理员权限

### 16.1 添加设备到黑名单
```http
POST /api/blacklist/device
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "device_id": "device_uuid",
  "reason": "恶意注册",
  "ttl_seconds": 3600
}
```

**查询参数**:
- `device_id`: 设备ID
- `reason`: 拉黑原因（可选）
- `ttl_seconds`: 过期时间（秒），None表示永久（可选）

**响应**:
```json
{
  "code": 200,
  "msg": "设备已添加到黑名单"
}
```

---

### 16.2 添加IP到黑名单
```http
POST /api/blacklist/ip
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "ip_address": "192.168.1.1",
  "reason": "恶意攻击",
  "ttl_seconds": 7200
}
```

**查询参数**:
- `ip_address`: IP地址
- `reason`: 拉黑原因（可选）
- `ttl_seconds`: 过期时间（秒），None表示永久（可选）

---

### 16.3 从黑名单移除设备
```http
DELETE /api/blacklist/device/remove?device_id=device_uuid
Authorization: Bearer <token>
```

**查询参数**:
- `device_id`: 设备ID

---

### 16.4 从黑名单移除IP
```http
DELETE /api/blacklist/ip/remove?ip_address=192.168.1.1
Authorization: Bearer <token>
```

**查询参数**:
- `ip_address`: IP地址

---

### 16.5 重建布隆过滤器
```http
POST /api/blacklist/rebuild
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "布隆过滤器重建完成"
}
```

---

### 16.6 获取所有黑名单信息
```http
GET /api/blacklist/list
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取黑名单成功",
  "data": {
    "devices": [
      {
        "device_id": "device_uuid",
        "reason": "恶意注册",
        "added_at": "2026-03-06T12:00:00",
        "expires_at": "2026-03-06T13:00:00"
      }
    ],
    "ips": [
      {
        "ip_address": "192.168.1.1",
        "reason": "恶意攻击",
        "added_at": "2026-03-06T12:00:00",
        "expires_at": "2026-03-06T14:00:00"
      }
    ]
  }
}
```

---

## 17. 管理后台 API (`/api/admin`)

> 所有端点都需要admin角色

### 17.1 获取用户列表
```http
GET /api/admin/users?username=test&email=test@example.com&role=user&is_active=true&is_verified=false&limit=50&offset=0
Authorization: Bearer <token>
```

**查询参数**:
- `username`: 用户名搜索（可选）
- `email`: 邮箱搜索（可选）
- `role`: 角色筛选（admin/user）（可选）
- `is_active`: 激活状态筛选（可选）
- `is_verified`: 验证状态筛选（可选）
- `limit`: 返回数量（默认50）
- `offset`: 偏移量（默认0）

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total": 100,
    "users": [...]
  }
}
```

---

### 17.2 激活/禁用用户
```http
PUT /api/admin/users/{user_id}/status
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "is_active": true
}
```

---

### 17.3 获取评论列表
```http
GET /api/admin/comments?content=test&post_id=post_xxx&user_id=1&limit=50&offset=0
Authorization: Bearer <token>
```

**查询参数**:
- `content`: 评论内容搜索（可选）
- `post_id`: 帖子ID筛选（可选）
- `user_id`: 用户ID筛选（可选）
- `limit`: 返回数量（默认50）
- `offset`: 偏移量（默认0）

---

### 17.4 删除评论
```http
DELETE /api/admin/comments/{comment_id}
Authorization: Bearer <token>
```

---

### 17.5 获取待审核内容
```http
GET /api/admin/posts/moderation?keyword=test&status=pending&limit=50&offset=0
Authorization: Bearer <token>
```

**查询参数**:
- `keyword`: 关键词搜索（标题/内容）（可选）
- `status`: 审核状态（默认pending）
- `limit`: 返回数量（默认50）
- `offset`: 偏移量（默认0）

---

### 17.6 审核帖子
```http
PUT /api/admin/posts/{post_id}/moderate
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "status": "approved",
  "reason": "内容符合规范"
}
```

**状态值**:
- `approved`: 通过
- `rejected`: 拒绝

---

### 17.7 获取系统统计
```http
GET /api/admin/stats
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total_users": 1000,
    "total_posts": 500,
    "total_comments": 200,
    "active_users_today": 800
  }
}
```

---

### 17.8 获取可视化图表数据
```http
GET /api/admin/stats/visualization
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "user_trend": [...],
    "post_trend": [...],
    "moderation_distribution": [...],
    "user_activity": [...],
    "content_type_distribution": [...],
    "top_content": [...],
    "interaction_stats": [...]
  }
}
```

---

### 17.9 获取用户注册趋势
```http
GET /api/admin/stats/user-trend?period=week&start_date=2026-01-01&end_date=2026-01-31
Authorization: Bearer <token>
```

**查询参数**:
- `period`: 预设周期（week/month/year）
- `start_date`: 自定义开始日期（YYYY-MM-DD）（可选）
- `end_date`: 自定义结束日期（YYYY-MM-DD）（可选）

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31",
    "period_type": "day",
    "period": "week",
    "total": 100,
    "trend": [
      {
        "date": "2026-01-01",
        "count": 10
      }
    ]
  }
}
```

---

### 17.10 获取审计日志
```http
GET /api/admin/logs/audit?resource_id=xxx&user_id=1&action=update&resource=user&method=POST&path_keyword=/api/user&status_code=2&response_status=success&limit=100&offset=0
Authorization: Bearer <token>
```

**查询参数**:
- `resource_id`: 资源ID搜索（可选）
- `user_id`: 用户ID筛选（可选）
- `action`: 操作类型筛选（可选）
- `resource`: 资源类型筛选（可选）
- `method`: HTTP方法筛选（GET/POST/PUT/DELETE）（可选）
- `path_keyword`: 请求路径模糊匹配（可选）
- `status_code`: 响应状态码筛选（传入2/4/5匹配2xx/4xx/5xx）（可选）
- `response_status`: 响应结果筛选（success/error）（可选）
- `limit`: 返回数量（默认100）
- `offset`: 偏移量（默认0）

---

### 17.11 获取工具调用统计
```http
GET /api/admin/logs/tools
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total_calls": 1000,
    "tool_usage": [
      {
        "tool_name": "get_weather",
        "call_count": 500,
        "success_rate": 0.98
      }
    ]
  }
}
```

---

### 17.12 触发MySQL备份
```http
POST /api/admin/backup/mysql
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "MySQL备份已触发"
}
```

---

### 17.13 触发MongoDB备份
```http
POST /api/admin/backup/mongodb
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "MongoDB备份已触发"
}
```

---

### 17.14 获取系统健康状态
```http
GET /api/admin/health
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "status": "healthy",
    "services": {
      "mysql": "healthy",
      "mongodb": "healthy",
      "redis": "healthy"
    },
    "uptime": 3600
  }
}
```

---

### 17.15 获取性能指标
```http
GET /api/admin/metrics
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "cpu_usage": 45.5,
    "memory_usage": 68.2,
    "disk_usage": 55.0,
    "response_time": 120
  }
}
```

---

## 18. 系统健康检查

### 18.1 应用健康检查
```http
GET /health
```

**响应**:
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": {
    "status": "healthy",
    "service": "智能旅行助手",
    "version": "1.0.0",
    "databases": {
      "mysql": "healthy",
      "mongodb": "healthy",
      "redis": "healthy"
    }
  }
}
```

---

## 19. 静态文件访问

### 19.1 访问上传的文件
```http
GET /storage/avatars/{filename}
GET /storage/media/{filename}
```

**示例**:
```
http://localhost:8000/storage/avatars/avatar_1_xxx.jpg
```

---

## 认证方式

### Bearer Token认证
大部分API需要在请求头中携带JWT Token：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token获取流程
1. 调用 `/api/auth/register` 或 `/api/auth/login`
2. 从响应中获取 `access_token`
3. 在后续请求中使用 `Authorization: Bearer <token>`

### Token过期
- 默认有效期：7天
- 过期后调用 `/api/auth/refresh` 刷新Token
- 或重新登录获取新Token

---

## 错误响应格式

所有API错误响应遵循统一格式：

```json
{
  "code": 400,
  "msg": "请求参数错误",
  "data": null
}
```

**常见状态码**:
- `200` - 请求成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未认证或Token无效
- `403` - 权限不足
- `404` - 资源不存在
- `429` - 请求过于频繁（限流）
- `500` - 服务器内部错误

**响应码枚举**:
```python
class ResponseCode:
    SUCCESS = 200        # 成功
    CREATED = 201        # 创建成功
    BAD_REQUEST = 400    # 请求参数错误
    UNAUTHORIZED = 401   # 未授权
    FORBIDDEN = 403      # 禁止访问
    NOT_FOUND = 404      # 资源不存在
    INTERNAL_ERROR = 500 # 服务器内部错误
```

---

## 完整使用示例

### 示例1：注册并生成旅行计划

```bash
# 1. 获取验证码
curl http://localhost:8000/api/auth/captcha
# 响应示例:
# {"code":200,"msg":"请求成功","data":{"session_id":"xxx","image_base64":"...","expires_in":300}}

# 2. 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "traveler",
    "email": "traveler@example.com",
    "password": "Travel@123",
    "nickname": "旅行者",
    "captcha_code": "1234",
    "captcha_session_id": "xxx"
  }'
# 响应示例:
# {"code":201,"msg":"注册成功","data":{"access_token":"eyJ...","user":{...}}}

# 3. 生成旅行计划（自动保存）
curl -X POST http://localhost:8000/api/trip/plan \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "上海",
    "start_date": "2026-03-01",
    "end_date": "2026-03-03",
    "travel_days": 3
  }'
# 响应示例:
# {"code":200,"msg":"旅行计划生成成功 (已保存)","data":{"city":"上海","days":[...]}}

# 4. 查询我的计划列表
curl http://localhost:8000/api/plans \
  -H "Authorization: Bearer <token>"
# 响应示例:
# {"code":200,"msg":"请求成功","data":{"total":1,"plans":[{...}]}}

# 5. 获取旅行统计
curl http://localhost:8000/api/user/stats \
  -H "Authorization: Bearer <token>"
# 响应示例:
# {"code":200,"msg":"请求成功","data":{"total_trips":1,"completed_trips":0,...}}
```

---

### 示例2：匿名用户生成计划

```bash
# 直接生成计划（不保存）
curl -X POST http://localhost:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "city": "杭州",
    "start_date": "2026-04-01",
    "end_date": "2026-04-02",
    "travel_days": 2
  }'
# 响应示例:
# {"code":200,"msg":"旅行计划生成成功","data":{"city":"杭州","days":[...]}}
```

---

### 示例3：使用对话功能

```bash
# 1. 创建对话会话
curl -X POST http://localhost:8000/api/dialog/sessions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"initial_context": {}}'
# 响应示例:
# {"code":201,"msg":"会话创建成功","data":{"session_id":"session_xxx"}}

# 2. 发送消息
curl -X POST http://localhost:8000/api/dialog/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_xxx",
    "message": "帮我规划一个北京3日游"
  }'
# 响应示例:
# {"code":200,"msg":"对话处理完成","data":{"session_id":"session_xxx","message":"好的，我来帮您规划北京3日游...","intent":"plan_trip"}}

# 3. 获取会话历史
curl http://localhost:8000/api/dialog/sessions/session_xxx \
  -H "Authorization: Bearer <token>"
# 响应示例:
# {"code":200,"msg":"获取成功","data":{"session_id":"session_xxx","messages":[...]}}
```

---

## 数据库初始化

在使用API之前，需要先初始化数据库：

```bash
# 1. 配置.env文件
cp .env.example .env
# 编辑.env，填写数据库密码和JWT密钥

# 2. 初始化MySQL
mysql -u root -p < backend/scripts/init_mysql.sql

# 3. 初始化MongoDB
python backend/scripts/init_mongodb.py

# 4. 初始化角色权限数据
python backend/scripts/seed_data.py
```

---

## Postman Collection

建议使用Postman导入OpenAPI规范：

1. 访问 `http://localhost:8000/openapi.json`
2. 在Postman中导入该JSON文件
3. 配置环境变量：
   - `base_url`: `http://localhost:8000`
   - `token`: 登录后获取的JWT Token

---

## 常见问题

### Q1: Token过期怎么办？
A: 调用 `/api/auth/refresh` 刷新Token，或重新登录。

### Q2: 匿名用户能使用哪些API？
A: 匿名用户可以使用：
- `/api/trip/plan` (生成计划，不保存)
- `/api/poi/search` (搜索景点)
- `/api/map/weather` (查询天气)
- `/api/poi/photo` (获取景点图片)

### Q3: 如何查看生成的旅行计划历史？
A: 登录后调用 `/api/plans` 查看所有保存的计划。

### Q4: 上传的文件存储在哪里？
A: 本地存储在 `storage/` 目录下，通过 `/storage/*` 路径访问。

### Q5: 如何限制用户只能查看自己的计划？
A: 所有计划API都会验证 `user_id`，确保用户只能操作自己的数据。

### Q6: 如何使用WebSocket实时对话？
A: 连接到 `ws://localhost:8000/api/dialog/ws/{session_id}`，发送JSON格式的消息。

### Q7: 如何使用SSE实时对话？
A: 连接到 `http://localhost:8000/api/dialog/sse/{session_id}?token=xxx`，接收Server-Sent Events。

### Q8: 黑名单管理如何工作？
A: 黑名单管理API包括：
- 设备黑名单：防止恶意设备注册/登录
- IP黑名单：防止恶意IP访问
- 布隆过滤器：快速检测已注册设备
- Redis精确检查：精确验证设备/IP状态

### Q9: 管理员有哪些权限？
A: 管理员可以：
- 查看和管理所有用户
- 审核和删除评论
- 审核帖子内容
- 查看系统统计和可视化数据
- 查看审计日志
- 触发数据库备份
- 查看系统健康状态和性能指标

---

## 技术支持

- **API文档**: http://localhost:8000/docs
- **系统健康**: http://localhost:8000/health
- **GitHub**: [项目仓库地址]

---

## 更新日志

### v2.0 (2026-03-06)
- 根据实际API实现同步更新所有接口文档
- 新增黑名单管理API（设备/IP黑名单、布隆过滤器）
- 新增首页仪表盘API（综合指标、用户统计、内容统计、业务指标、业务趋势）
- 新增对话管理API（创建会话、列出会话、获取会话详情、更新会话、删除会话、获取工具调用日志）
- 新增SSE和WebSocket实时对话端点
- 新增社交功能API（获取评论列表、用户主页帖子、热门标签、按标签查询、抖音热点话题）
- 新增智能推荐系统API（获取个性化推荐、生成个性化推荐）
- 新增预算管理API（创建预算、添加支出、获取预算统计、获取预算概览）
- 新增实时信息服务API（获取实时信息、获取实时信息概览）
- 新增多语言支持API（文本翻译、语音翻译、获取支持的语言列表）
- 新增语音交互API（语音识别、语音合成、处理语音命令）
- 新增离线功能API（下载离线地图、同步离线数据、获取离线数据）
- 新增POI相关API（获取POI详情、获取景点图片）
- 新增地图服务API（搜索POI、规划路线、健康检查）
- 新增管理后台API（用户列表、用户状态管理、评论管理、内容审核、系统统计、可视化数据、用户趋势、审计日志、工具调用日志、数据库备份、系统健康、性能指标）
- 更新用户管理API（更新访问过的城市）
- 更新旅行计划API（导出计划）
- 更新认证API（注册请求增加nickname字段、登录请求移除device_id字段）
- 更新社交功能API（创建帖子请求增加title字段、增加location和trip_plan_id字段）

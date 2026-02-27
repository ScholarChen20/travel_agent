# API 使用指南 - Phase 1 & 2

本文档说明当前系统的所有可用API端点及其使用方法。

---

## 基础信息

**Base URL**: `http://localhost:8000`
**API文档**: `http://localhost:8000/docs` (Swagger UI)
**ReDoc文档**: `http://localhost:8000/redoc`

---

## 1. 认证相关 API (`/api/auth`)

### 1.1 获取验证码
```http
GET /api/auth/captcha
```

**响应**:
```json
{
  "session_id": "string",
  "image_base64": "data:image/png;base64,...",
  "expires_in": 300
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
  "captcha_code": "1234",
  "captcha_session_id": "xxx"
}
```

**响应**:
```json
{
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
```

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
  "captcha_session_id": "xxx",
  "device_id": "web-chrome"
}
```

**响应**: 同注册响应

**限流**: 5次失败后锁定5分钟

---

### 1.4 用户登出
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

**响应**:
```json
{
  "message": "登出成功"
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
    "travel_preferences": ["自然风光", "美食"],
    "visited_cities": ["北京", "上海"],
    "travel_stats": {
      "total_trips": 5,
      "total_cities": 3
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
  "travel_preferences": ["海滨", "历史文化"]
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
  "avatar_url": "/storage/avatars/avatar_1_xxx.jpg"
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
  "total_trips": 5,
  "completed_trips": 3,
  "favorite_trips": 2,
  "total_cities": 4
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
  "cities": ["北京", "上海", "杭州", "成都"]
}
```

---

### 2.6 修改密码
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
  "success": true,
  "message": "旅行计划生成成功",
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
  "success": true,
  "message": "旅行计划生成成功 (已保存)",
  "data": {
    "city": "北京",
    "days": [...],
    "plan_id": "plan_xxx",       // 新增
    "session_id": "session_xxx"  // 新增
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
Content-Type: application/json
```

**请求体**:
```json
{
  "is_favorite": true
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

### 5.1 搜索景点
```http
GET /api/poi/search?city=北京&keywords=故宫
```

---

## 6. 地图服务 API (`/api/map`)

### 6.1 天气查询
```http
GET /api/map/weather?city=北京
```

---

## 7. 系统健康检查

### 7.1 应用健康检查
```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "service": "智能旅行助手",
  "version": "1.0.0",
  "databases": {
    "mysql": "healthy",
    "mongodb": "healthy",
    "redis": "healthy"
  }
}
```

---

## 8. 静态文件访问

### 8.1 访问上传的文件
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
  "detail": "错误描述信息"
}
```

**常见HTTP状态码**:
- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未认证或Token无效
- `403` - 权限不足
- `404` - 资源不存在
- `429` - 请求过于频繁（限流）
- `500` - 服务器内部错误

---

## 完整使用示例

### 示例1：注册并生成旅行计划

```bash
# 1. 获取验证码
curl http://localhost:8000/api/auth/captcha

# 2. 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "traveler",
    "email": "traveler@example.com",
    "password": "Travel@123",
    "captcha_code": "1234",
    "captcha_session_id": "xxx"
  }'

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

# 4. 查询我的计划列表
curl http://localhost:8000/api/plans \
  -H "Authorization: Bearer <token>"

# 5. 获取旅行统计
curl http://localhost:8000/api/user/stats \
  -H "Authorization: Bearer <token>"
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

### Q3: 如何查看生成的旅行计划历史？
A: 登录后调用 `/api/plans` 查看所有保存的计划。

### Q4: 上传的文件存储在哪里？
A: 本地存储在 `storage/` 目录下，通过 `/storage/*` 路径访问。

### Q5: 如何限制用户只能查看自己的计划？
A: 所有计划API都会验证 `user_id`，确保用户只能操作自己的数据。

---

## 技术支持

- **API文档**: http://localhost:8000/docs
- **系统健康**: http://localhost:8000/health
- **GitHub**: [项目仓库地址]

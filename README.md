# 智能旅行助手 🌍✈️

> 基于AI大模型的智能旅行规划助手，一键生成个性化旅行计划

[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Vue Version](https://img.shields.io/badge/vue-3.5+-green.svg)](https://vuejs.org/)
[![node Version]( https://img.shields.io/npm/v/npm.svg?logo=nodedotjs)](https://nodejs.org/en/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)


---

## 📖 项目简介

**智能旅行助手**是一个基于AI大模型的旅行规划应用，通过自然语言交互，为用户自动生成详细的旅行计划。系统集成了高德地图、天气服务、景点推荐等多种功能，让旅行规划变得简单而智能。

### ✨ 核心亮点

- 🤖 **AI智能规划**：基于大语言模型，理解用户需求，自动生成个性化旅行计划
- 🗺️ **地图深度集成**：集成高德地图服务，提供景点搜索、路线规划、天气查询
- 💬 **多轮对话交互**：支持自然语言对话，随时调整旅行计划
- 📱 **全平台支持**：Web端响应式设计，支持PC和移动端访问
- 🔒 **安全可靠**：完整的用户认证、数据加密、防刷机制
- 🌐 **一键部署**：Docker容器化部署，支持云服务器快速上线
- 📊 **数据可视化**：丰富的图表展示，直观了解旅行统计
- 🎯 **智能推荐**：基于用户偏好，推荐景点、餐厅、酒店

### 🎯 适用人群

- **旅行爱好者**：想要快速规划旅行行程，不想花时间做攻略
- **新手旅行者**：对目的地不熟悉，需要专业建议和路线规划
- **自由行用户**：喜欢自由安排行程，但需要参考和建议
- **商务出差**：需要快速了解目的地，安排住宿和交通
- **技术开发者**：学习AI应用开发、前后端分离架构、Docker部署

---

## 🛠️ 技术选型

### 后端技术栈

| 技术 | 版本 | 用途                     |
|------|------|------------------------|
| **Python** | 3.14+ | 主要开发语言                 |
| **FastAPI** | Latest | 高性能Web框架，提供RESTful API |
| **HelloAgents** | Latest | AI智能体框架，实现智能对话和规划      |
| **MySQL** | 8.0+ | 关系型数据库，存储用户数据、日志       |
| **MongoDB** | 7.0+ | 文档数据库，存储旅行计划和对话        |
| **Redis** | 7.0+ | 缓存和会话管理                |
| **Docker** | Latest | 容器化部署                  |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue.js** | 3.5+ | 渐进式JavaScript框架 |
| **TypeScript** | 5.0+ | 类型安全的JavaScript超集 |
| **Vite** | 5.0+ | 现代化构建工具 |
| **Ant Design Vue** | 4.0+ | 企业级UI组件库 |
| **ECharts** | 5.0+ | 数据可视化图表库 |
| **Nginx** | 1.25+ | 负载均衡和静态文件服务 |

### 第三方服务

- **高德地图**：地图服务、POI搜索、路线规划
- **DashScope/DeepSeek**：大语言模型API
- **阿里云OSS**：对象存储服务
- **飞书开放平台**：第三方登录

---

## 🚀 快速上手

### 方式一：Docker一键部署（推荐）

**适合人群**：想要快速体验项目，不想配置复杂环境的用户

#### 前提条件

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ 可用内存

#### 部署步骤

# 安装Docker
```bash
sudo apt-get update
sudo apt-get install docker.io -y

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```
1. **克隆项目**
```bash
git clone https://github.com/yourusername/travel-agent.git
cd travel-agent
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入必要的API密钥
# 环境变量设置
```bash
echo "export FEISHU_APP_SECRET=YOUR_SECRET" >> ~/.bashrc  # 飞书开发者平台密钥
echo "export DASHSCOPE_API_KEY=您的API密钥" >> ~/.bashrc  # DashScope API密钥
echo "export AMAP_API_KEY=您的API密钥" >> ~/.bashrc # 高德地图API密钥
echo "export UNSPLASH_SECRET_KEY=您的API密钥" >> ~/.bashrc # Unsplash API密钥
echo "export OSS_ACCESS_KEY_SECRET=您的API密钥" >> ~/.bashrc  # 阿里云OSS密钥
echo "export NGROK_AUTHTOKEN=你的ngrok的授权令牌" >> ~/.bashrc

source ~/.bashrc
```

3. **启动服务**
```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

4. **访问应用**
- 前端：http://服务器地址
- 后端API：http://服务器地址:8000
- API文档：http://服务器地址:8000/docs

5. **初始化数据库**
```bash
# 进入后端容器
docker exec -it travel-agent-backend-1 bash

# 运行初始化脚本
python scripts/init_mongodb.py

# 退出容器
exit
```
6. **验证服务**
```bash
# 检查前端服务
curl http://服务器地址
# 检查后端API
curl http://服务器地址/api/health
```

7. **内网穿透**
是指通过网络将内网服务暴露给外网，使得外网用户可以访问内网服务。若构建过程中ngrok启动成功，但是地址没映射，可手动执行。
# 7.1 手动脚本运行
```bash
cd /opt/travel-agent
./scripts/ngrok.sh
```
# 7.2 手动命令行运行
```bash
docker run -it --rm \
    --network travel-agent_travel-network \
    -e NGROK_AUTHTOKEN=YOUR_TOKEN \   # 替换为ngrok的授权令牌（需要先注册）
    -p 4040:4040 \
    ngrok/ngrok:latest http frontend:80
```
8. **数据备份**
# 系统已配置定时任务每周天2点执行备份
```bash
# 手动执行
python scripts/backup/backup_databases.py
```

---

### 方式二：本地开发环境

**适合人群**：想要二次开发、学习源码的开发者

#### 前提条件

- Python 3.14+
- Node.js 18+
- MySQL 8.0+
- MongoDB 7.0+
- Redis 7.0+

#### 后端开发

1. **进入后端目录**
```bash
cd backend
```

2. **创建虚拟环境**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置
backend\app\config.py  # 配置文件，包含数据库连接信息、API密钥等
```

5. **启动数据库服务**
```bash
# 方式一：使用Docker Compose（推荐）
docker-compose up -d mysql mongodb redis

# 方式二：使用Docker单独启动各个服务
# Redis（使用Redis Stack Server，支持RedisBloom/RedisSearch/RedisJSON模块）
docker run -d --name redis \
  -p 6379:6379 \
  -v redis-data:/data \
  -v ./redis.conf:/opt/redis/redis.conf:ro \  # /opt/redis/redis.conf需要替换自己的本地文件配置地址
  redis/redis-stack-server:latest \
  redis-stack-server /opt/redis/redis.conf --requirepass "123456"

# MongoDB
docker run -d --name mongodb \
  -p 27017:27017 \
  -v mongodb-data:/data/db \
  -e MONGO_INITDB_ROOT_USERNAME=travel_agent_user \
  -e MONGO_INITDB_ROOT_PASSWORD=123456 \
  -e MONGO_INITDB_DATABASE=travel_agent \
  mongo:7.0

# MySQL
docker run -d --name mysql \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  -v ./backend/scripts/init_mysql.sql:/docker-entrypoint-initdb.d/init.sql:ro \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=travel_agent \
  -e MYSQL_USER=travel_agent_user \
  -e MYSQL_PASSWORD=123456 \
  mysql:8.0 \
  --default-authentication-plugin=mysql_native_password \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 方式三：本地自行安装MySQL、MongoDB、Redis
下载地址：
- MySQL：https://dev.mysql.com/downloads/installer/
- MongoDB：https://www.mongodb.com/try/download/community
- Redis：https://github.com/redis-windows/redis-windows/releases
```

6. **初始化数据库**
```bash
# 初始化MongoDB数据库
python scripts/init_mongodb.py

# 初始化MySQL数据库
mysql -u root -p < backend/scripts/init_data/travel_agent.sql
```

7. **启动后端服务**
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

1. **进入前端目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
npm install
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置API地址
```

4. **启动开发服务器**
```bash
npm run dev
```

5. **访问应用**
打开浏览器访问 http://localhost:5173

---

#### 本地内网穿透
应用下载地址： https://ngrok.com/download  （根据操作系统下载对应版本）
注册地址：https://ngrok.com/
# 1. 配置ngrok
```bash
cd D:\JavaEnv\ngrok-v3-stable # 进入本地ngrok目录
ngrok config add-authtoken $NGROK_AUTHTOKEN # 替换为ngrok的授权令牌（需要先注册）
```
# 2. 本地启动ngrok
```bash
ngrok http 5173   # 等待几秒即可查看到分配的随机域名
```


## 📖 使用指南

### 第一次使用

1. **注册账号**
   - 访问应用首页
   - 点击"注册"按钮
   - 填写用户名、邮箱、密码
   - 完成邮箱验证

2. **生成旅行计划**
   - 在首页输入目的地城市
   - 选择旅行日期和天数
   - 选择交通方式和住宿偏好
   - 点击"生成旅行计划"

3. **查看和调整**
   - 查看生成的详细行程
   - 点击景点查看详情
   - 使用对话功能调整计划
   - 保存喜欢的计划

### 高级功能

- **多轮对话**：在对话页面与AI助手交互，调整旅行计划
- **社交分享**：发布旅行计划到社区，与其他用户交流
- **数据统计**：查看个人旅行统计和趋势分析
- **离线使用**：下载旅行计划到本地，离线查看

---

## 🏗️ 项目结构

```
travel-agent/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agents/            # AI智能体实现
│   │   ├── api/               # FastAPI路由
│   │   │   └── routes/       # 各功能模块路由
│   │   ├── services/          # 业务逻辑层
│   │   ├── models/            # 数据模型
│   │   ├── middleware/        # 中间件
│   │   └── utils/             # 工具函数
│   ├── scripts/               # 脚本工具
│   ├── requirements.txt        # Python依赖
│   └── .env.example          # 环境变量模板
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   ├── views/            # 页面视图
│   │   ├── services/          # API服务
│   │   ├── stores/           # 状态管理
│   │   └── types/            # TypeScript类型
│   ├── package.json           # Node依赖
│   └── vite.config.ts        # Vite配置
├── docs/                     # 项目文档
│   └── API接口文档设计v2.0.md
├── docker-compose.yml          # Docker编排文件
└── README.md                  # 项目说明
```

---

## 🔧 核心功能实现

### AI智能规划

系统使用HelloAgents框架构建智能体，通过大语言模型理解用户需求：

```python
from hello_agents import SimpleAgent

agent = SimpleAgent(
    name="旅行规划助手",
    system_prompt="你是一个专业的旅行规划助手...",
    tools=[amap_tool, weather_tool, poi_tool]
)

# 生成旅行计划
plan = agent.plan_trip(
    city="北京",
    days=3,
    preferences=["历史文化", "美食"]
)
```

### 地图服务集成

通过高德地图MCP服务提供地图功能：

- 景点搜索和推荐
- 路线规划（步行、驾车、公交）
- 天气查询
- 地图展示和标记

### 对话系统

支持多轮对话，用户可以：

- 调整旅行计划
- 询问景点信息
- 获取旅行建议
- 修改行程安排

---

## 📚 API文档

启动后端服务后，访问以下地址查看完整API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

主要API端点：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/trip/plan` | POST | 生成旅行计划 |
| `/api/plans` | GET | 获取旅行计划列表 |
| `/api/dialog/chat` | POST | 对话交互 |
| `/api/map/poi` | GET | 搜索景点 |
| `/api/map/weather` | GET | 查询天气 |

详细API文档请查看 [docs/API接口文档设计v2.0.md](docs/API接口文档设计v2.0.md)

---

## ❓ 常见问题

### Q1: Docker启动失败怎么办？

**A**: 检查以下几点：
1. 确认Docker和Docker Compose已正确安装
2. 检查端口是否被占用（80、8000、3306、27017、6379、4040）
3. 查看Docker日志：`docker-compose logs`
4. 确保有足够的内存和磁盘空间

### Q2: 如何获取unsplash API密钥？

**A**: 
1. 访问 [unsplash平台](https://unsplash.com/developers)
2. 注册账号并登录
3. 进入控制台，创建应用
4. 添加Key
5. 复制API Key到.env文件并放入系统环境变量

### Q3: 如何获取高德地图API密钥？

**A**: 
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册账号并登录
3. 进入控制台，创建应用
4. 复制API Key到.env文件并放入系统环境变量

### Q4: 如何获取DashScope API密钥？

**A**:
1. 访问 [阿里云百炼官网](https://www.aliyun.com/product/bailian)
2. 注册账号并登录
3. 进入API Keys页面
4. 创建新的API Key
5. 复制Key到.env文件并放入系统环境变量

### Q5: 如何获取ngrok 权限令牌？

**A**:
1. 访问 [ngrok官网](https://ngrok.com/)
2. 注册账号并登录
3. 进入AUTHTOKEN页面
4. 复制NGROK_AUTHTOKEN到.env文件并放入系统环境变量

### Q6: 前端无法连接后端怎么办？

**A**:
1. 检查后端服务是否正常运行
2. 检查前端.env文件中的API地址配置
3. 检查防火墙设置
4. 查看浏览器控制台的错误信息

### Q7: 如何部署到云服务器？

**A**: 参考项目中的 [部署文档.md](docs/%E9%83%A8%E7%BD%B2%E6%96%87%E6%A1%A3.md) 文档，包含详细的云服务器部署步骤。

### Q8: 数据库初始化失败怎么办？

**A**:
1. 检查数据库服务是否正常运行
2. 检查数据库连接配置是否正确
3. 查看初始化脚本的错误日志
4. 确保数据库用户有足够的权限

---

## 🤝 参与贡献

欢迎贡献代码、提出建议或报告问题！

### 贡献方式

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/travelai`)
3. 提交更改 (`git commit -m 'Add some travelai'`)
4. 推送到分支 (`git push origin feature/travelai`)
5. 提交Pull Request

### 开发规范

- 遵循PEP 8代码规范
- 添加必要的注释和文档
- 编写单元测试
- 更新相关文档

---

## 📄 开源协议

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议。

---

## 🙏 致谢

感谢以下开源项目和服务：

- [HelloAgents](https://github.com/jjyaoao/HelloAgents) - 智能体框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [高德地图](https://lbs.amap.com/) - 地图服务
- [Ant Design Vue](https://antdv.com/) - Vue组件库

---

## 📮 联系方式

- **项目地址**: [GitHub Repository](https://github.com/ScholarChen20/travel_agent)
- **问题反馈**: [Issues](https://github.com/ScholarChen20/travel_agent/issues)
- **邮箱**: 1523910137@qq.com

---

## 🌟 Star History

如果这个项目对你有帮助，请给我们一个Star ⭐️

---

**智能旅行助手** - 让旅行规划变得简单而智能 🌈

Made with ❤️ by Team

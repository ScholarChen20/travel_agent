#!/bin/bash

# Ngrok一键部署脚本
# 适用于Travel_agent项目的云服务器部署

set -e

echo "========================================"
echo "  Travel Agent - Ngrok 一键部署"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}提示: 建议使用sudo运行此脚本${NC}"
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    echo "请先安装Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装${NC}"
    echo "请先安装Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker环境检查通过${NC}"
echo ""

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}警告: .env文件不存在${NC}"
    echo "正在从.env.example创建.env文件..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env文件已创建${NC}"
    else
        echo -e "${RED}错误: .env.example文件不存在${NC}"
        exit 1
    fi
fi

# 提示输入ngrok authtoken
echo ""
echo "========================================"
echo "  Ngrok 配置"
echo "========================================"
echo ""
echo "请输入你的Ngrok Authtoken"
echo "获取地址: https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
read -p "Ngrok Authtoken: " NGROK_TOKEN

if [ -z "$NGROK_TOKEN" ]; then
    echo -e "${RED}错误: Authtoken不能为空${NC}"
    exit 1
fi

# 更新.env文件
if grep -q "^NGROK_AUTHTOKEN=" .env; then
    sed -i "s/^NGROK_AUTHTOKEN=.*/NGROK_AUTHTOKEN=$NGROK_TOKEN/" .env
else
    echo "NGROK_AUTHTOKEN=$NGROK_TOKEN" >> .env
fi
echo -e "${GREEN}✓ Ngrok Authtoken已配置${NC}"
echo ""

# 创建ngrok配置目录
mkdir -p backend/scripts/.ngrok2

# 配置ngrok authtoken（用于独立安装模式）
if command -v ngrok &> /dev/null; then
    echo "配置ngrok authtoken..."
    ngrok config add-authtoken "$NGROK_TOKEN"
    echo -e "${GREEN}✓ Ngrok authtoken已配置${NC}"
else
    echo -e "${YELLOW}提示: ngrok未安装，将使用Docker模式${NC}"
fi

echo ""
echo "========================================"
echo "  启动服务"
echo "========================================"
echo ""

# 停止现有服务
echo "停止现有服务..."
docker-compose -f docker-compose-with-ngrok.yml down 2>/dev/null || true

# 构建并启动服务
echo "构建并启动服务（包含ngrok）..."
docker-compose -f docker-compose-with-ngrok.yml up -d --build

echo ""
echo "========================================"
echo "  服务启动完成"
echo "========================================"
echo ""

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose-with-ngrok.yml ps

echo ""
echo "========================================"
echo "  获取Ngrok公网地址"
echo "========================================"
echo ""

# 获取ngrok公网地址
echo "正在获取ngrok公网地址..."
sleep 5

# 尝试从ngrok日志中提取公网地址
NGROK_URL=$(docker-compose -f docker-compose-with-ngrok.yml logs ngrok 2>&1 | grep -oP 'https://[a-z0-9-]+\.ngrok-free\.app' | head -1)

if [ -n "$NGROK_URL" ]; then
    echo -e "${GREEN}✓ Ngrok公网地址已获取${NC}"
    echo ""
    echo "========================================"
    echo "  访问信息"
    echo "========================================"
    echo ""
    echo -e "${GREEN}后端API: ${NGROK_URL}${NC}"
    echo -e "${GREEN}前端页面: ${NGROK_URL}${NC}"
    echo -e "${GREEN}Ngrok Web UI: http://$(hostname -I | awk '{print $1}'):4040${NC}"
    echo ""
    echo "========================================"
    echo "  重要提示"
    echo "========================================"
    echo ""
    echo "1. 免费版ngrok的域名可能会变化，这是正常现象"
    echo "2. 如需固定域名，请升级ngrok付费计划"
    echo "3. 生产环境建议使用固定域名或自建frp"
    echo "4. 可以通过以下命令查看ngrok日志:"
    echo "   docker-compose -f docker-compose-with-ngrok.yml logs -f ngrok"
    echo ""
else
    echo -e "${YELLOW}警告: 无法自动获取ngrok公网地址${NC}"
    echo ""
    echo "请手动查看ngrok日志获取公网地址:"
    echo "  docker-compose -f docker-compose-with-ngrok.yml logs -f ngrok"
    echo ""
    echo "或访问ngrok Web UI:"
    echo "  http://$(hostname -I | awk '{print $1}'):4040"
    echo ""
fi

echo "========================================"
echo "  部署完成！"
echo "========================================"

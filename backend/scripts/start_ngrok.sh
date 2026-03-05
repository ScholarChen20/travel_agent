#!/bin/bash

# Ngrok快速启动脚本

set -e

echo "========================================"
echo "  Ngrok 快速启动脚本"
echo "========================================"

# 检查ngrok是否已安装
if ! command -v ngrok &> /dev/null; then
    echo "错误: ngrok未安装"
    echo "请先运行: bash scripts/install_ngrok.sh"
    exit 1
fi

# 检查是否已配置authtoken
if [ ! -f ~/.ngrok2/ngrok.yml ]; then
    echo "错误: ngrok未配置authtoken"
    echo ""
    echo "请按以下步骤操作："
    echo "1. 注册ngrok账号: https://ngrok.com/signup"
    echo "2. 获取authtoken: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "3. 配置authtoken: ngrok config add-authtoken YOUR_AUTHTOKEN"
    echo ""
    exit 1
fi

# 检查配置文件
CONFIG_FILE="$(dirname "$0")/ngrok.yml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

echo "配置文件: $CONFIG_FILE"
echo ""

# 验证配置
echo "验证ngrok配置..."
ngrok config check --config "$CONFIG_FILE"

echo ""
echo "========================================"
echo "  启动Ngrok隧道"
echo "========================================"
echo ""

# 启动ngrok
ngrok start --all --config "$CONFIG_FILE"

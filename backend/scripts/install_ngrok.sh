#!/bin/bash

# Ngrok安装脚本 - 适用于Linux系统
# 支持Ubuntu/Debian/CentOS/Rocky Linux等

set -e

echo "========================================"
echo "  Ngrok 安装脚本"
echo "========================================"

# 检测系统架构
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        NGROK_ARCH="amd64"
        ;;
    aarch64|arm64)
        NGROK_ARCH="arm64"
        ;;
    *)
        echo "不支持的架构: $ARCH"
        exit 1
        ;;
esac

echo "检测到系统架构: $ARCH -> $NGROK_ARCH"

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "无法检测操作系统"
    exit 1
fi

echo "检测到操作系统: $OS"

# 安装依赖
echo "正在安装依赖..."
if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
    sudo apt-get update
    sudo apt-get install -y wget unzip
elif [[ "$OS" == "centos" || "$OS" == "rhel" || "$OS" == "rocky" || "$OS" == "almalinux" ]]; then
    sudo yum install -y wget unzip
elif [[ "$OS" == "fedora" ]]; then
    sudo dnf install -y wget unzip
else
    echo "警告: 未知的操作系统，尝试使用wget和unzip"
fi

# 下载ngrok
echo "正在下载ngrok..."
NGROK_VERSION="3.13.0"
NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-$NGROK_ARCH.zip"

wget -O /tmp/ngrok.zip "$NGROK_URL"

# 解压并安装
echo "正在安装ngrok..."
sudo unzip -o /tmp/ngrok.zip -d /usr/local/bin
sudo chmod +x /usr/local/bin/ngrok

# 清理
rm -f /tmp/ngrok.zip

# 验证安装
echo "验证安装..."
ngrok version

echo ""
echo "========================================"
echo "  Ngrok 安装完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo "1. 注册ngrok账号: https://ngrok.com/signup"
echo "2. 获取authtoken: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "3. 配置authtoken: ngrok config add-authtoken YOUR_AUTHTOKEN"
echo "4. 启动隧道: ngrok http 8000"
echo ""
echo "或者使用配置文件: ngrok config check"
echo "使用配置文件启动: ngrok start --all"
echo ""

#!/bin/sh

# Ngrok Docker 启动脚本 - 等待 Frontend 就绪后再启动

echo "=========================================="
echo "Ngrok 启动脚本"
echo "=========================================="

# 检查环境变量
if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "错误: NGROK_AUTHTOKEN 环境变量未设置"
    exit 1
fi

echo "等待 Frontend 服务就绪..."

# 最多等待 120 秒
max_attempts=120
attempt=0

while [ $attempt -lt $max_attempts ]; do
    # 尝试连接 frontend:80
    # 使用 wget 或 nc 检查端口
    if wget -q --spider --timeout=1 http://frontend:80 2>/dev/null; then
        echo "✓ Frontend 服务已就绪 (尝试 $attempt 次)"
        break
    fi

    attempt=$((attempt + 1))

    # 每 10 次输出一次进度
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "等待中... ($attempt/$max_attempts 秒)"
    fi

    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "✗ Frontend 服务启动超时 (等待了 $max_attempts 秒)"
    echo "请检查 Frontend 容器是否正常运行"
    exit 1
fi

# 额外等待 2 秒，确保服务完全稳定
echo "等待服务稳定..."
sleep 2

# 启动 Ngrok
echo "=========================================="
echo "启动 Ngrok 隧道..."
echo "目标: http://frontend:80"
echo "=========================================="

exec ngrok http frontend:80
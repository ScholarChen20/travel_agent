#!/bin/bash

# MongoDB备份脚本
# 功能：全量备份MongoDB数据库，保留30天

# 配置
BACKUP_DIR="/var/backups/mongodb"
MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
MONGODB_DATABASE="${MONGODB_DATABASE:-travel_agent}"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 生成备份文件名（带时间戳）
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/mongodb_backup_$TIMESTAMP"

echo "开始MongoDB备份..."
echo "数据库: $MONGODB_DATABASE"
echo "备份目录: $BACKUP_PATH"

# 执行备份
mongodump \
  --uri="$MONGODB_URI" \
  --db="$MONGODB_DATABASE" \
  --out="$BACKUP_PATH"

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "MongoDB备份成功: $BACKUP_PATH"

    # 压缩备份
    echo "压缩备份文件..."
    tar -czf "$BACKUP_PATH.tar.gz" -C "$BACKUP_DIR" "mongodb_backup_$TIMESTAMP"

    # 删除未压缩的备份目录
    rm -rf "$BACKUP_PATH"

    # 获取备份文件大小
    BACKUP_SIZE=$(du -h "$BACKUP_PATH.tar.gz" | cut -f1)
    echo "备份大小: $BACKUP_SIZE"

    # 删除超过保留期的备份
    echo "清理旧备份（保留${RETENTION_DAYS}天）..."
    find "$BACKUP_DIR" -name "mongodb_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

    echo "备份完成"
    exit 0
else
    echo "MongoDB备份失败"
    exit 1
fi

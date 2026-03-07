#!/bin/bash

# MySQL备份脚本
# 功能：全量备份MySQL数据库，保留30天

# 配置
BACKUP_DIR="/var/backups/mysql"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD}"
MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_DATABASE="${MYSQL_DATABASE:-travel_agent}"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 生成备份文件名（带时间戳）
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/mysql_backup_$TIMESTAMP.sql.gz"

echo "开始MySQL备份..."
echo "数据库: $MYSQL_DATABASE"
echo "备份文件: $BACKUP_FILE"

# 执行备份
mysqldump \
  --host="$MYSQL_HOST" \
  --port="$MYSQL_PORT" \
  --user="$MYSQL_USER" \
  --password="$MYSQL_PASSWORD" \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  "$MYSQL_DATABASE" | gzip > "$BACKUP_FILE"

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "MySQL备份成功: $BACKUP_FILE"

    # 获取备份文件大小
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "备份大小: $BACKUP_SIZE"

    # 删除超过保留期的备份
    echo "清理旧备份（保留${RETENTION_DAYS}天）..."
    find "$BACKUP_DIR" -name "mysql_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

    echo "备份完成"
    exit 0
else
    echo "MySQL备份失败"
    exit 1
fi

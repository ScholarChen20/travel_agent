# Cron配置示例
# 定时执行数据库备份

# 每天凌晨2点执行MySQL备份
0 2 * * * /path/to/backend/scripts/backup_mysql.sh >> /var/log/mysql_backup.log 2>&1

# 每天凌晨3点执行MongoDB备份
0 3 * * * /path/to/backend/scripts/backup_mongodb.sh >> /var/log/mongodb_backup.log 2>&1

# 安装方法：
# 1. 编辑crontab: crontab -e
# 2. 添加上述配置
# 3. 保存退出

# 查看cron日志：
# tail -f /var/log/mysql_backup.log
# tail -f /var/log/mongodb_backup.log

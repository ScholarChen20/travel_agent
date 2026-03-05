# 数据备份使用说明

## 功能概述

本系统提供完整的数据备份功能，包括：
1. MySQL数据库备份
2. MongoDB数据库备份
3. Redis数据持久化
4. 定时自动备份（每天凌晨2点）

## 备份功能使用

### 1. 手动执行备份

```bash
# 进入项目目录
cd d:\JavaPro\Travel_agent\backend

# 执行备份脚本
python scripts/backup/backup_databases.py
```

### 2. 定时自动备份

系统会在每天凌晨2点自动执行备份任务，无需手动干预。

备份文件会保存在 `backups` 目录下：
- `backups/mysql/` - MySQL备份文件
- `backups/mongodb/` - MongoDB备份文件
- `backups/redis/` - Redis备份文件

### 3. 备份文件格式

- MySQL: `mysql_backup_YYYYMMDD_HHMMSS.sql.gz`
- MongoDB: `mongodb_backup_YYYYMMDD_HHMMSS.tar.gz`
- Redis: `redis_backup_YYYYMMDD_HHMMSS.rdb`

### 4. 备份保留策略

默认保留30天的备份文件，超过30天的备份会自动删除。

## 数据恢复

### MySQL数据恢复

```bash
# 解压备份文件
gunzip mysql_backup_YYYYMMDD_HHMMSS.sql.gz

# 恢复数据库
mysql -u用户名 -p密码 数据库名 < mysql_backup_YYYYMMDD_HHMMSS.sql
```

### MongoDB数据恢复

```bash
# 解压备份文件
tar -xzf mongodb_backup_YYYYMMDD_HHMMSS.tar.gz

# 恢复数据库
mongorestore --uri="mongodb://用户名:密码@主机:端口" --db=数据库名 mongodb_backup_YYYYMMDD_HHMMSS
```

### Redis数据恢复

```bash
# 将RDB文件复制到Redis数据目录
cp redis_backup_YYYYMMDD_HHMMSS.rdb /path/to/redis/dump.rdb

# 重启Redis服务
redis-server /path/to/redis.conf
```

## Redis持久化配置

Redis已经配置了双重持久化策略：

### RDB持久化
- 15分钟内至少有1个key发生变化
- 5分钟内至少有10个key发生变化
- 1分钟内至少有10000个key发生变化

### AOF持久化
- 每秒同步一次（appendfsync everysec）
- 结合RDB和AOF的优点（混合持久化）

## 配置说明

备份配置位于 `scripts/backup/backup_databases.py`，可以修改以下参数：

- `backup_dir`: 备份文件保存目录
- `retention_days`: 备份文件保留天数（默认30天）

## 注意事项

1. 确保MySQL、MongoDB、Redis服务正常运行
2. 确保有足够的磁盘空间存储备份文件
3. 定期检查备份文件是否完整
4. 建议将备份文件复制到其他存储介质（如云存储）
5. 在迁移服务器时，使用备份文件可以快速恢复数据

## 故障排查

### 备份失败

1. 检查数据库连接配置是否正确
2. 检查磁盘空间是否充足
3. 检查数据库服务是否正常运行
4. 查看日志文件了解详细错误信息

### 恢复失败

1. 确保备份文件完整且未损坏
2. 检查目标数据库是否已创建
3. 检查数据库权限是否足够
4. 查看数据库日志了解详细错误信息

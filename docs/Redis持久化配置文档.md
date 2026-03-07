# Redis持久化配置说明

## 一、配置概述

已为Docker环境配置Redis的完整持久化策略，包括：

1. **RDB持久化**：定时快照备份
2. **AOF持久化**：实时日志记录
3. **混合持久化**：结合RDB和AOF的优点

## 二、配置文件位置

- **配置文件**：`redis.conf`（项目根目录）
- **Docker配置**：`docker-compose.yml`（已更新）

## 三、持久化策略详解

### 3.1 RDB持久化配置

```conf
# 在指定时间内，如果执行了指定数量的写操作，则保存数据到磁盘
save 900 1    # 900秒（15分钟）内至少有1个key发生变化
save 300 10   # 300秒（5分钟）内至少有10个key发生变化
save 60 10000 # 60秒（1分钟）内至少有10000个key发生变化

# RDB文件名
dbfilename dump.rdb

# RDB文件保存目录
dir /data

# 是否压缩RDB文件
rdbcompression yes

# 是否对RDB文件进行校验
rdbchecksum yes
```

**优点**：
- 文件紧凑，恢复速度快
- 适合备份
- 性能影响小

**缺点**：
- 可能丢失最后一次快照后的数据
- 需要定期保存

### 3.2 AOF持久化配置

```conf
# 开启AOF持久化
appendonly yes

# AOF文件名
appendfilename "appendonly.aof"

# AOF同步策略
appendfsync everysec  # 每秒同步一次（推荐）

# AOF重写配置
auto-aof-rewrite-percentage 100  # 文件增长100%时重写
auto-aof-rewrite-min-size 64mb   # 最小重写大小64MB

# 是否在AOF重写期间进行同步
no-appendfsync-on-rewrite no

# 是否加载损坏的AOF文件
aof-load-truncated yes
```

**优点**：
- 数据安全性高，最多丢失1秒数据
- 日志格式可读，易于恢复

**缺点**：
- 文件体积较大
- 性能影响相对较大

### 3.3 混合持久化配置

```conf
# 开启混合持久化，结合RDB和AOF的优点
aof-use-rdb-preamble yes
```

**优点**：
- 结合了RDB的快速恢复和AOF的数据安全
- 文件体积适中
- 恢复速度快

## 四、Docker配置

### 4.1 docker-compose.yml配置

```yaml
redis:
  image: redis/redis-stack-server:latest
  ports:
     - "6379:6379"
  command: redis-stack-server /etc/redis/redis.conf --requirepass R3d1s#Tr@vel2025!Secure
  volumes:
    - redis-data:/data
    - ./redis.conf:/etc/redis/redis.conf:ro
  restart: always
  networks:
    - travel-network
```

**关键配置说明**：
- `command`: 指定使用自定义配置文件
- `volumes`: 挂载配置文件和数据卷
- `redis-data`: Docker数据卷，用于持久化存储

### 4.2 数据卷配置

```yaml
volumes:
  redis-data:
```

数据卷会自动创建，用于存储：
- RDB文件：`/data/dump.rdb`
- AOF文件：`/data/appendonly.aof`

## 五、使用方法

### 5.1 启动Redis服务

```bash
# 启动所有服务（包括Redis）
docker-compose up -d

# 只启动Redis服务
docker-compose up -d redis

# 查看Redis日志
docker-compose logs -f redis
```

### 5.2 验证持久化配置

```bash
# 进入Redis容器
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure

# 查看持久化配置
INFO persistence

# 查看配置信息
CONFIG GET save
CONFIG GET appendonly
CONFIG GET appendfsync
```

### 5.3 测试持久化

```bash
# 连接Redis
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure

# 设置测试数据
SET test_key "test_value"

# 手动触发RDB保存
BGSAVE

# 查看保存状态
LASTSAVE

# 退出Redis
EXIT

# 重启Redis容器
docker-compose restart redis

# 再次连接Redis验证数据
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure
GET test_key
```

## 六、持久化文件管理

### 6.1 查看持久化文件

```bash
# 查看Redis数据卷中的文件
docker-compose exec redis ls -lh /data

# 应该看到以下文件：
# - dump.rdb (RDB文件)
# - appendonly.aof (AOF文件)
```

### 6.2 备份持久化文件

```bash
# 复制RDB文件到本地
docker cp travel_agent-redis-1:/data/dump.rdb ./backup_dump.rdb

# 复制AOF文件到本地
docker cp travel_agent-redis-1:/data/appendonly.aof ./backup_appendonly.aof
```

### 6.3 恢复持久化文件

```bash
# 停止Redis容器
docker-compose stop redis

# 复制备份文件到数据卷
docker cp ./backup_dump.rdb travel_agent-redis-1:/data/dump.rdb
docker cp ./backup_appendonly.aof travel_agent-redis-1:/data/appendonly.aof

# 启动Redis容器
docker-compose start redis
```

## 七、监控和维护

### 7.1 监控持久化状态

```bash
# 查看持久化信息
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure INFO persistence

# 关键指标：
# - rdb_last_bgsave_status: RDB最后保存状态
# - rdb_last_save_time: RDB最后保存时间
# - aof_enabled: AOF是否启用
# - aof_last_bgrewrite_status: AOF最后重写状态
# - aof_rewrite_in_progress: AOF重写是否进行中
```

### 7.2 查看日志

```bash
# 查看Redis容器日志
docker-compose logs redis

# 实时查看日志
docker-compose logs -f redis

# 查看最近100行日志
docker-compose logs --tail=100 redis
```

### 7.3 性能优化

```bash
# 查看内存使用情况
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure INFO memory

# 查看统计信息
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure INFO stats

# 查看客户端连接
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure CLIENT LIST
```

## 八、故障排查

### 8.1 常见问题

#### 问题1：Redis启动失败
```bash
# 查看容器日志
docker-compose logs redis

# 检查配置文件语法
docker-compose exec redis redis-stack-server --test-memory 1

# 检查文件权限
docker-compose exec redis ls -la /data
```

#### 问题2：持久化文件未生成
```bash
# 检查AOF是否启用
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure CONFIG GET appendonly

# 手动触发保存
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure BGSAVE

# 检查数据卷挂载
docker volume inspect travel_agent_redis-data
```

#### 问题3：数据丢失
```bash
# 检查持久化配置
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure CONFIG GET save
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure CONFIG GET appendfsync

# 检查持久化文件
docker-compose exec redis ls -lh /data

# 查看持久化状态
docker-compose exec redis redis-cli -a R3d1s#Tr@vel2025!Secure INFO persistence
```

## 九、安全建议

1. **密码保护**：已配置密码 `R3d1s#Tr@vel2025!Secure`
2. **网络隔离**：使用Docker网络隔离
3. **端口限制**：生产环境建议只绑定本地
4. **定期备份**：定期复制持久化文件到异地存储
5. **监控告警**：配置持久化失败的告警

## 十、性能调优

### 10.1 根据业务调整持久化策略

```conf
# 写入频繁的场景：减少save时间间隔
save 60 1000
save 30 5000
save 10 10000

# 写入较少的场景：增加save时间间隔
save 3600 1
save 1800 10
save 600 10000
```

### 10.2 调整AOF同步策略

```conf
# 最高安全性：每次写入都同步
appendfsync always

# 推荐配置：每秒同步一次
appendfsync everysec

# 最高性能：由操作系统决定
appendfsync no
```

### 10.3 调整内存淘汰策略

```conf
# 从设置了过期时间的key中淘汰最近最少使用的key
maxmemory-policy volatile-lru

# 从所有key中淘汰最近最少使用的key
maxmemory-policy allkeys-lru

# 从设置了过期时间的key中淘汰最不经常使用的key
maxmemory-policy volatile-lfu

# 从所有key中淘汰最不经常使用的key
maxmemory-policy allkeys-lfu

# 从设置了过期时间的key中随机淘汰
maxmemory-policy volatile-random

# 从所有key中随机淘汰
maxmemory-policy allkeys-random

# 从设置了过期时间的key中淘汰即将过期的key
maxmemory-policy volatile-ttl

# 不淘汰任何key，当内存满时返回错误
maxmemory-policy noeviction
```

## 十一、总结

通过以上配置，Redis在Docker环境中具备了完整的持久化能力：

1. **数据安全**：RDB + AOF双重保障，最多丢失1秒数据
2. **快速恢复**：混合持久化，恢复速度快
3. **易于管理**：配置文件集中管理，易于调整
4. **自动备份**：定时保存，无需手动干预
5. **容器化部署**：与Docker完美集成，易于迁移

建议定期检查持久化状态，确保数据安全。

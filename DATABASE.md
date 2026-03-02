# 数据库配置说明

本项目支持两种数据库：**SQLite** 和 **PostgreSQL**，可通过 `.env` 文件中的 `DATABASE_TYPE` 参数自动切换。

## 配置机制

系统会根据 `DATABASE_TYPE` 的值自动选择对应的数据库配置：

- `DATABASE_TYPE=sqlite` → 使用 `SQLITE_DB_PATH` 配置
- `DATABASE_TYPE=postgresql` → 使用 `POSTGRES_*` 系列配置

**`.env` 文件中同时包含两种数据库的完整配置，通过注释/取消注释 `DATABASE_TYPE` 行来切换。**

## .env 文件配置示例

```bash
# ============================================================
# 数据库配置 - Database Configuration
# ============================================================
# 选择数据库类型：取消注释（删除行首的 #）其中一个即可
# Choose database type: Uncomment (remove #) one of the following

# DATABASE_TYPE=sqlite          # ← 注释状态
DATABASE_TYPE=postgresql        # ← 激活状态

# ------------------ SQLite 配置 (开发环境推荐) ------------------
# SQLite Configuration (Development)
SQLITE_DB_PATH=./meeting_assistant.db

# ------------------ PostgreSQL 配置 (生产环境推荐) ------------------
# PostgreSQL Configuration (Production)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=meeting_assistant
POSTGRES_POOL_SIZE=5
POSTGRES_MAX_OVERFLOW=10
# ============================================================
```

## SQLite（适合开发/测试环境）

### 特点
- 无需额外服务
- 零配置，开箱即用
- 适合开发和测试
- 单文件存储，便于备份

### 配置步骤

1. 编辑 `.env` 文件：

```bash
# 取消注释 SQLite 行
DATABASE_TYPE=sqlite

# 注释 PostgreSQL 行
# DATABASE_TYPE=postgresql
```

2. 启动服务：

```bash
docker-compose up -d
```

数据库文件会自动创建在 `meeting-assistant-backend` 目录下。

## PostgreSQL（适合生产环境）

### 特点
- 高并发性能
- ACID 完整性保证
- 适合生产环境
- 支持连接池

### 配置步骤

1. 编辑 `.env` 文件：

```bash
# 注释 SQLite 行
# DATABASE_TYPE=sqlite

# 取消注释 PostgreSQL 行
DATABASE_TYPE=postgresql
```

2. 启动服务：

```bash
docker-compose --profile postgres up -d
```

这会启动三个容器：
- `meeting-postgres` - PostgreSQL 数据库
- `meeting-backend` - 后端 API
- `meeting-frontend` - 前端界面

### 数据持久化

PostgreSQL 数据存储在 Docker volume `postgres-data` 中，即使容器删除也不会丢失数据。

## 数据库切换

### 快速切换方法

**只需要在 `.env` 文件中切换注释即可！**

#### 从 SQLite 切换到 PostgreSQL

1. 停止服务：
```bash
docker-compose down
```

2. 修改 `.env` 文件：
```bash
# 注释 SQLite
# DATABASE_TYPE=sqlite

# 取消注释 PostgreSQL
DATABASE_TYPE=postgresql
```

3. 使用 PostgreSQL profile 启动：
```bash
docker-compose --profile postgres up -d
```

#### 从 PostgreSQL 切换到 SQLite

1. 停止服务：
```bash
docker-compose --profile postgres down
```

2. 修改 `.env` 文件：
```bash
# 取消注释 SQLite
DATABASE_TYPE=sqlite

# 注释 PostgreSQL
# DATABASE_TYPE=postgresql
```

3. 正常启动：
```bash
docker-compose up -d
```

### ⚠️ 重要提示

**数据不会自动迁移**。切换数据库类型后：
- 原数据库中的数据不会丢失
- 新数据库是空的，需要重新创建会议
- 如需迁移数据，请使用备份/恢复功能

## 生产环境建议

### PostgreSQL 配置优化

对于生产环境，建议调整以下参数：

```bash
# 在 .env 文件中
POSTGRES_POOL_SIZE=20        # 根据并发量调整
POSTGRES_MAX_OVERFLOW=40     # pool_size 的 2 倍
```

### 连接池说明

- `pool_size`: 常驻连接数
- `max_overflow`: 额外连接数（超过 pool_size）
- 总最大连接数 = pool_size + max_overflow

示例：pool_size=20, max_overflow=40，总共可以有 60 个并发连接

### 数据备份

**PostgreSQL 备份：**
```bash
# 备份
docker exec meeting-postgres pg_dump -U postgres meeting_assistant > backup.sql

# 恢复
docker exec -i meeting-postgres psql -U postgres meeting_assistant < backup.sql
```

**SQLite 备份：**
```bash
# 直接复制文件
cp meeting-assistant-backend/meeting_assistant.db backup.db
```

## 环境变量参考

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DATABASE_TYPE | sqlite | 数据库类型：sqlite 或 postgresql |
| SQLITE_DB_PATH | ./meeting_assistant.db | SQLite 数据库文件路径 |
| POSTGRES_HOST | postgres | PostgreSQL 主机名（Docker 内部） |
| POSTGRES_PORT | 5432 | PostgreSQL 端口 |
| POSTGRES_USER | postgres | PostgreSQL 用户名 |
| POSTGRES_PASSWORD | postgres | PostgreSQL 密码 |
| POSTGRES_DB | meeting_assistant | PostgreSQL 数据库名 |
| POSTGRES_POOL_SIZE | 5 | 连接池大小 |
| POSTGRES_MAX_OVERFLOW | 10 | 额外连接数 |

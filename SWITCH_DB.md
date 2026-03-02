# 快速参考：数据库类型切换

## 🎯 核心原理

**只需在 `.env` 文件中注释/取消注释 `DATABASE_TYPE` 行即可切换！**

系统会自动根据 `DATABASE_TYPE` 选择对应的配置：
- `sqlite` → 使用 `SQLITE_DB_PATH` 配置
- `postgresql` → 使用 `POSTGRES_*` 系列配置

## 📋 .env 文件配置示例

### 当前配置结构（两种数据库配置都存在）

```bash
# ============================================================
# 数据库配置 - Database Configuration
# ============================================================
# 选择数据库类型：取消注释（删除行首的 #）其中一个即可
# Choose database type: Uncomment (remove #) one of the following

# DATABASE_TYPE=sqlite          # ← 注释状态（不使用）
DATABASE_TYPE=postgresql        # ← 激活状态（当前使用）

# ------------------ SQLite 配置 (开发环境推荐) ------------------
SQLITE_DB_PATH=./meeting_assistant.db

# ------------------ PostgreSQL 配置 (生产环境推荐) ------------------
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=meeting_assistant
POSTGRES_POOL_SIZE=5
POSTGRES_MAX_OVERFLOW=10
# ============================================================
```

## 🔄 切换方法

### 方法一：注释切换（推荐）

**切换到 SQLite：**

```bash
# .env 文件中：
DATABASE_TYPE=sqlite            # 取消注释
# DATABASE_TYPE=postgresql      # 添加注释
```

**切换到 PostgreSQL：**

```bash
# .env 文件中：
# DATABASE_TYPE=sqlite          # 添加注释
DATABASE_TYPE=postgresql        # 取消注释
```

### 方法二：使用编辑器

1. 打开 `.env` 文件
2. 找到 `DATABASE_TYPE` 配置部分
3. 在两个 `DATABASE_TYPE` 行之间切换注释符 `#`
4. 保存文件

## 🚀 完整切换步骤

### SQLite → PostgreSQL

```bash
# 1. 编辑 .env 文件
#    将：DATABASE_TYPE=sqlite
#    改为：# DATABASE_TYPE=sqlite
#    将：# DATABASE_TYPE=postgresql
#    改为：DATABASE_TYPE=postgresql

# 2. 停止当前服务
docker-compose down

# 3. 启动 PostgreSQL 服务
docker-compose --profile postgres up -d
```

### PostgreSQL → SQLite

```bash
# 1. 编辑 .env 文件
#    将：DATABASE_TYPE=postgresql
#    改为：# DATABASE_TYPE=postgresql
#    将：# DATABASE_TYPE=sqlite
#    改为：DATABASE_TYPE=sqlite

# 2. 停止当前服务
docker-compose --profile postgres down

# 3. 启动服务
docker-compose up -d
```

## ⚠️ 重要提醒

切换数据库类型后，数据不会自动迁移：
- 原数据库保留，不会丢失
- 新数据库为空，需重新创建数据
- 建议在切换前备份数据

## ✅ 验证配置

运行验证命令：

```bash
docker exec meeting-backend python -c "from app.core.config import settings; print(f'DB Type: {settings.DATABASE_TYPE}')"
```

**输出示例：**

PostgreSQL 模式：
```
DB Type: postgresql
```

SQLite 模式：
```
DB Type: sqlite
```

## 📝 配置说明

### SQLite 模式
- **适用场景**：开发、测试环境
- **优点**：无需额外服务，开箱即用
- **配置文件**：`meeting_assistant.db`
- **启动命令**：`docker-compose up -d`

### PostgreSQL 模式
- **适用场景**：生产环境
- **优点**：高并发、数据完整性
- **连接池**：5 个常驻 + 10 个额外连接
- **启动命令**：`docker-compose --profile postgres up -d`

## 📁 相关文件

- `.env` - 环境配置文件（切换 `DATABASE_TYPE`）
- `.env.example` - 配置模板
- `DATABASE.md` - 详细数据库配置文档
- `meeting-assistant-backend/app/core/config.py` - 配置逻辑
- `meeting-assistant-backend/app/core/database.py` - 数据库连接逻辑

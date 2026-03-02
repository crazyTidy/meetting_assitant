# Docker Volume 配置说明

## PostgreSQL 数据存储配置

### 方式一：Named Volume（当前使用）

```yaml
# docker-compose.yml
volumes:
  - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
    driver: local
```

**说明：**
- **左侧** `postgres-data`: Docker Volume 名称（不是路径）
- **右侧** `/var/lib/postgresql/data`: 容器内的路径
- **实际存储位置**: `/var/lib/docker/volumes/meetting_assitant_postgres-data/_data`

**宿主机实际路径：**
```
Windows: \\wsl$\docker-desktop-data\data\docker\volumes\meetting_assitant_postgres-data\_data
Linux: /var/lib/docker/volumes/meetting_assitant_postgres-data/_data
Mac: /var/lib/docker/volumes/meetting_assitant_postgres-data/_data
```

**查看实际路径：**
```bash
docker volume inspect meetting_assitant_postgres-data
```

**优点：**
- ✅ Docker 自动管理
- ✅ 跨平台兼容
- ✅ 适合生产环境
- ✅ 备份简单（使用 docker volume 命令）

**缺点：**
- ❌ 路径不直观
- ❌ 需要特殊命令查看内容

---

### 方式二：Bind Mount（直接映射目录）

```yaml
# docker-compose.yml
volumes:
  - ./postgres-data:/var/lib/postgresql/data
```

**说明：**
- **左侧** `./postgres-data`: 宿主机相对路径（相对于 docker-compose.yml 文件）
- **右侧** `/var/lib/postgresql/data`: 容器内的路径
- **实际存储位置**: `C:\Users\JK-T-004\Desktop\wuguipeng\meetting_assitant\postgres-data`

**宿主机实际路径：**
```
项目目录下的 postgres-data 文件夹
C:\Users\JK-T-004\Desktop\wuguipeng\meetting_assitant\postgres-data
```

**优点：**
- ✅ 路径直观，一目了然
- ✅ 可以直接在文件管理器中查看
- ✅ 方便备份和迁移
- ✅ 适合开发环境

**缺点：**
- ❌ 需要手动创建目录
- ❌ Windows 可能有权限问题
- ❌ 路径依赖于项目位置

---

## 如何选择？

### 生产环境 → 使用 Named Volume（当前配置）
```yaml
volumes:
  - postgres-data:/var/lib/postgresql/data
```

### 开发环境 → 可以使用 Bind Mount
```yaml
volumes:
  - ./postgres-data:/var/lib/postgresql/data
```

---

## 当前配置详解

### PostgreSQL Volume 信息

**Volume 名称**: `meetting_assitant_postgres-data`

**容器内路径**: `/var/lib/postgresql/data`

**宿主机实际路径**:
```
Linux/Mac: /var/lib/docker/volumes/meetting_assitant_postgres-data/_data
Windows (WSL2): \\wsl$\docker-desktop-data\data\docker\volumes\...
Windows (Docker Desktop): 通过 Docker Desktop 界面查看
```

### 查看和管理命令

**1. 查看 Volume 详情：**
```bash
docker volume inspect meetting_assitant_postgres-data
```

**2. 列出所有 Volumes：**
```bash
docker volume ls
```

**3. 查看 Volume 大小：**
```bash
docker system df -v | grep postgres-data
```

**4. 备份数据：**
```bash
# 方式一：使用 pg_dump（推荐）
docker exec meeting-postgres pg_dump -U postgres meeting_assistant > backup.sql

# 方式二：直接备份 Volume
docker run --rm -v meetting_assitant_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

**5. 恢复数据：**
```bash
# 使用 pg_restore
docker exec -i meeting-postgres psql -U postgres meeting_assistant < backup.sql
```

**6. 删除 Volume（危险操作！）：**
```bash
# 先停止容器
docker-compose --profile postgres down

# 删除 volume
docker volume rm meetting_assitant_postgres-data
```

---

## 切换到 Bind Mount（可选）

如果您想直接在项目目录下存储数据，修改 `docker-compose.yml`:

```yaml
postgres:
  image: postgres:16-alpine
  container_name: meeting-postgres
  ports:
    - "5432:5432"
  environment:
    - POSTGRES_USER=${POSTGRES_USER:-postgres}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
    - POSTGRES_DB=${POSTGRES_DB:-meeting_assistant}
  volumes:
    - ./postgres-data:/var/lib/postgresql/data  # 改为本地路径
  networks:
    - meeting-network
  restart: unless-stopped
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
    interval: 10s
    timeout: 5s
    retries: 5
  profiles:
    - postgres
```

然后重启服务：
```bash
docker-compose --profile postgres down
docker-compose --profile postgres up -d
```

数据将存储在：`C:\Users\JK-T-004\Desktop\wuguipeng\meetting_assitant\postgres-data`

"""MinIO 存储配置说明

## 配置方式

在 `.env` 文件或环境变量中配置：

```bash
# 存储类型：local 或 minio
STORAGE_TYPE=minio

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=meeting-assistant
MINIO_SECURE=false
```

## 使用说明

### 本地存储（默认）
```bash
STORAGE_TYPE=local
```
文件保存在 `uploads/` 目录

### MinIO 存储
```bash
STORAGE_TYPE=minio
```
文件保存在 MinIO 对象存储

## 功能特性

✅ 自动切换存储后端
✅ 统一的存储接口
✅ 支持文件上传/下载/删除
✅ MinIO 自动创建 bucket
✅ 透明的文件路径处理

## 存储路径格式

- 本地：`uploads/filename.mp3`
- MinIO：`minio://bucket-name/filename.mp3`

# 知识库管理功能使用指南

## 功能概述

JoyAgent 知识库管理功能基于 RAGFlow 提供完整的知识管理解决方案，支持：

- 📚 **数据集管理**：创建、查看、删除知识库数据集
- 📄 **文档上传**：支持多种格式文档的批量上传和管理  
- 🔍 **智能检索**：基于语义相似度的知识检索
- 📊 **统计分析**：数据集和文档的详细统计信息

## 快速开始

### 1. 配置 RAGFlow

在 `genie-backend/src/main/resources/application.yml` 中配置 RAGFlow 连接信息：

```yaml
autobots:
  autoagent:
    ragflow:
      base_url: "http://127.0.0.1:9380"
      api_key: "your-ragflow-api-key"
      timeout: 30
      retry_attempts: 3
```

### 2. 启用知识库工具

在工具列表中添加 `ragflow`：

```yaml
tool_list: '{"default": "search,code,report,ragflow"}'
```

### 3. 启动服务

```bash
# 启动后端服务
cd genie-backend && sh start.sh

# 启动工具服务
cd genie-tool && uv run python server.py

# 启动前端
cd ui && pnpm dev
```

## 功能详解

### 数据集管理

#### 创建数据集
1. 进入知识库页面，点击"创建数据集"
2. 填写数据集名称和描述
3. 选择嵌入模型（推荐 `text-embedding-3-small`）
4. 确认创建

#### 数据集列表
- 显示所有数据集的基本信息
- 支持按名称搜索
- 显示文档数、块数等统计信息

### 文档管理

#### 上传文档
1. 点击数据集详情进入文档管理
2. 点击"上传文档"按钮
3. 选择支持的文件格式：
   - TXT（纯文本）
   - PDF（文档）
   - DOC/DOCX（Word文档）
   - MD（Markdown）

#### 文档列表
- 查看文档处理状态
- 显示文档块数统计
- 支持文档删除操作

### 知识检索

#### 检索设置
- **搜索内容**：输入要查找的问题或关键词
- **数据集选择**：可选择特定数据集或搜索全部
- **返回结果数**：设置最多返回的结果数量（1-50）
- **相似度阈值**：过滤低相似度结果（0-100%）

#### 检索结果
- 显示相关文档片段
- 高亮显示匹配关键词
- 显示相似度评分
- 展示关联的关键词标签

## API 接口

### Java 后端 API

```java
// 数据集管理
POST /api/knowledge/datasets          // 创建数据集
GET  /api/knowledge/datasets          // 获取数据集列表
DELETE /api/knowledge/datasets/{id}   // 删除数据集

// 文档管理  
POST /api/knowledge/datasets/{id}/documents     // 上传文档
GET  /api/knowledge/datasets/{id}/documents     // 获取文档列表
DELETE /api/knowledge/datasets/{id}/documents/{docId} // 删除文档

// 知识检索
POST /api/knowledge/search            // 知识检索
POST /api/knowledge/batch            // 批量操作
```

### Python 工具 API

```python
# FastAPI 路由
POST /v1/knowledge/datasets          # 创建数据集
GET  /v1/knowledge/datasets          # 数据集列表
GET  /v1/knowledge/datasets/{id}     # 数据集详情
DELETE /v1/knowledge/datasets/{id}   # 删除数据集

POST /v1/knowledge/search            # 知识检索
GET  /v1/knowledge/health            # 健康检查
```

## Agent 工具使用

在 Agent 对话中可以直接使用知识库功能：

```json
{
  "action": "create_dataset",
  "name": "技术文档库",
  "description": "存储技术文档和API说明"
}
```

```json
{
  "action": "search_knowledge", 
  "query": "如何配置数据库连接",
  "dataset_id": "dataset-id-here"
}
```

支持的操作：
- `create_dataset` - 创建数据集
- `list_datasets` - 列出数据集
- `upload_document` - 上传文档
- `list_documents` - 列出文档
- `search_knowledge` - 知识检索
- `delete_dataset` - 删除数据集
- `delete_document` - 删除文档

## 最佳实践

### 数据集组织
- 按主题或项目创建不同的数据集
- 使用清晰的命名和描述
- 合理选择嵌入模型

### 文档准备
- 确保文档内容结构清晰
- 使用标准的文件格式
- 控制单个文档的大小（≤10MB）

### 检索优化
- 使用具体的关键词和问题
- 适当调整相似度阈值
- 结合不同的检索参数

## 故障排除

### 常见问题

1. **RAGFlow 连接失败**
   - 检查 RAGFlow 服务是否正常运行
   - 验证配置中的 URL 和 API 密钥
   - 确认网络连接正常

2. **文档上传失败**
   - 检查文件格式是否支持
   - 确认文件大小不超过限制
   - 验证文件内容是否损坏

3. **检索结果不准确**
   - 调整相似度阈值
   - 尝试不同的关键词组合
   - 检查文档质量和内容结构

### 日志查看

```bash
# 查看后端日志
tail -f genie-backend/logs/application.log

# 查看工具服务日志  
tail -f genie-tool/logs/server.log
```

## 更新日志

### v1.0.0
- ✅ 基础数据集管理功能
- ✅ 文档上传和管理
- ✅ 知识检索功能
- ✅ 前端管理界面
- ✅ Agent 工具集成

### 计划功能
- 🔄 批量文档处理
- 🔄 文档预览功能
- 🔄 高级检索选项
- 🔄 知识图谱可视化
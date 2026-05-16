# 购房电话智能分析系统

一个专业的房产销售通话录音智能分析平台，支持音频上传、语音转文本、AI智能分析、客户评级、统计分析以及PDF报告导出。

## 核心功能

### 🎯 智能分析
- **语音转文本**: 使用火山引擎语音识别API，自动将MP3通话录音转换为带时间戳的文本
- **说话人分离**: 自动识别并分离置业顾问和客户对话
- **AI深度分析**: 基于DeepSeek大语言模型，提供全面的通话分析
  - 客户购房意向识别
  - 客户等级评定（A/B/C类）
  - 购房需求提取（面积、价格、区域、户型）
  - 购房阶段判断
  - 核心关注点分析
  - 竞品对比分析
  - 情感与沟通效果评估
  - 跟进策略建议

### 📊 数据管理
- **历史记录**: 自动保存所有分析记录，支持分页浏览
- **搜索筛选**: 支持关键词搜索和多条件筛选
- **记录对比**: 支持多记录对比分析
- **统计分析**: 客户等级分布、意向趋势、关注点排行等

### 📄 报告导出
- **PDF报告**: 生成专业的中文分析报告
- **批量导出**: 支持批量处理并导出ZIP压缩包
- **自定义标签**: 自动生成客户标签（高意向、学区关注等）

## 技术架构

### 后端技术栈
- **框架**: Flask 3.0.0
- **数据库**: SQLite（生产环境支持Vercel/Render云部署）
- **PDF生成**: ReportLab
- **HTTP请求**: Requests
- **CORS支持**: Flask-CORS

### 前端技术栈
- **模板引擎**: Jinja2
- **样式**: CSS3（响应式设计）
- **交互**: 原生JavaScript（无框架依赖）

### 第三方API集成
- **语音识别**: 火山引擎语音识别API（极速版/长音频版）
- **AI分析**: DeepSeek API（deepseek-v4-flash模型）
- **备用方案**: 飞书妙计API（语音识别）

## 项目结构

```
call_analyzer/
├── app.py                      # Flask主应用，包含所有API路由
├── requirements.txt            # Python依赖列表
├── .env.example               # 环境变量配置示例
├── Procfile                    # Railway部署配置
├── render.yaml                 # Render部署配置
│
├── templates/                 # HTML模板
│   ├── index.html             # 首页（文件上传与分析）
│   ├── history.html           # 历史记录页面
│   └── dashboard.html         # 统计分析仪表盘
│
├── static/                    # 静态资源
│   ├── css/
│   │   └── style.css          # 全局样式
│   └── js/
│       ├── main.js            # 首页交互逻辑
│       ├── history.js         # 历史记录交互
│       └── dashboard.js       # 仪表盘图表
│
├── services/                  # 业务服务模块
│   ├── ai_analyzer.py         # DeepSeek AI分析服务
│   ├── audio_processor.py     # 音频处理服务（说话人分离）
│   ├── database.py            # SQLite数据库服务
│   ├── pdf_generator.py       # PDF报告生成
│   └── speech_to_text.py      # 火山引擎语音识别
│
├── routes/                     # 路由模块
│   └── api.py                # API路由定义
│
├── data/                      # 数据存储
│   └── analysis.db           # SQLite数据库文件
│
└── uploads/                   # 文件上传目录（需手动创建）
```

## 快速开始

### 环境要求
- Python 3.8+
- FFmpeg（用于音频处理，可选）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd call_analyzer
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置API密钥：
```env
# DeepSeek API配置（AI分析必需）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

# 火山引擎语音识别配置（语音转文本必需）
VOLC_API_KEY=your-volc-api-key
VOLC_APP_ID=your-app-id
VOLC_USE_LONG_AUDIO=false

# 飞书API（备用语音识别，可选）
FEISHU_APP_ID=your-feishu-app-id
FEISHU_APP_SECRET=your-feishu-app-secret

# Flask配置
SECRET_KEY=your-secret-key
```

5. **启动应用**
```bash
python app.py
```

访问 `http://localhost:5000` 即可使用。

## API接口文档

### 文件上传
```
POST /api/upload
```
- **功能**: 上传MP3音频文件
- **参数**: `file` (表单文件字段)
- **返回**: 
```json
{
  "success": true,
  "filename": "uuid_filename.mp3",
  "file_id": "uuid"
}
```

### 音频处理
```
POST /api/process
```
- **功能**: 完整处理流程（语音转文本 + AI分析）
- **参数**: `{"filename": "uuid_filename.mp3"}`
- **返回**:
```json
{
  "success": true,
  "speaker1": [{"text": "...", "timestamp": "00:01", "speaker_id": 1}],
  "speaker2": [{"text": "...", "timestamp": "00:02", "speaker_id": 2}],
  "analysis": {
    "通话概要": {...},
    "客户评级": {...},
    "购房意向": {...},
    "购房阶段": {...},
    "客户核心关注点": {...},
    "竞品对比": {...},
    "情感与沟通": {...},
    "关键信息提取": {...},
    "跟进建议": {...},
    "总结": "..."
  }
}
```

### 批量处理
```
POST /api/batch-process
```
- **功能**: 批量处理多个音频文件
- **参数**: `{"batch_id": "uuid", "files": [...]}`
- **返回**: `{"success": true, "batch_id": "uuid", "total": 5}`

### 批量状态查询
```
GET /api/batch-status/<batch_id>
```
- **返回**: 处理进度和结果

### 批量导出
```
GET /api/batch-export/<batch_id>
```
- **功能**: 导出批量处理结果为ZIP
- **返回**: ZIP文件下载

### 文本分析
```
POST /api/analyze-transcript
```
- **功能**: 直接分析文本内容（跳过语音转文本）
- **参数**: `{"transcript": "说话人1 00:01\n对话内容..."}`
- **返回**: AI分析结果

### 历史记录
```
GET /api/history?limit=20&offset=0
```
- **功能**: 获取分析历史记录
- **返回**: 分页记录列表

### 历史搜索
```
POST /api/history/search
```
- **功能**: 搜索筛选历史记录
- **参数**: `{"keyword": "...", "grade": "A", "intention": "高"}`

### 记录对比
```
GET /api/history/compare?ids=1,2,3
```
- **功能**: 对比多条记录

### 统计面板
```
GET /api/dashboard/stats
GET /api/dashboard/grade-distribution
GET /api/dashboard/intention-trend
GET /api/dashboard/concerns-ranking
```
- **功能**: 统计分析数据

### PDF导出
```
POST /api/export-pdf
```
- **功能**: 导出单条分析记录为PDF
- **参数**: `{"analysis": {...}, "speaker1": [...], "speaker2": [...]}`

### 长音频处理
```
POST /api/process-url
GET /api/task-status/<task_id>
```
- **功能**: 通过URL处理长音频文件

## 使用指南

### 单文件分析
1. 访问首页 `http://localhost:5000`
2. 拖放或选择MP3文件上传
3. 点击"开始分析"按钮
4. 等待语音转文本和AI分析完成
5. 查看对话文本和分析结果
6. 可选择导出PDF报告或复制文本

### 批量分析
1. 上传多个MP3文件
2. 点击"批量处理"按钮
3. 查看处理进度
4. 处理完成后下载ZIP报告包

### 历史记录管理
1. 访问"历史记录"页面
2. 使用关键词或条件筛选记录
3. 查看单条记录详情
4. 选择多条记录进行对比分析
5. 删除不需要的记录

### 数据分析
1. 访问"仪表盘"页面
2. 查看客户等级分布饼图
3. 查看意向趋势折线图
4. 查看客户关注点排行
5. 使用日期筛选器查看不同时间段数据

## AI分析维度

系统使用DeepSeek API对通话进行多维度分析：

| 分析维度 | 说明 |
|---------|------|
| 通话概要 | 时长估算、有效沟通程度、客户响应积极性 |
| 客户评级 | 意向强度、购买力评估、决策周期、综合等级 |
| 购房意向 | 面积需求、价格区间、区域偏好、户型需求 |
| 购房阶段 | 初步咨询/需求明确/决策阶段/犹豫观望 |
| 核心关注点 | 第一、第二、第三关注点及其他关注 |
| 竞品对比 | 提及竞品、对比倾向、项目优劣势 |
| 情感分析 | 客户态度、置业顾问表现、沟通效果 |
| 跟进建议 | 话术要点、卖点强调、异议处理、下一步计划 |

## 部署说明

### 本地开发
```bash
python app.py
```

### Railway部署
1. 连接GitHub仓库
2. 设置环境变量
3. 自动部署

### Render部署
1. 创建Web Service
2. 配置构建命令：`pip install -r requirements.txt`
3. 配置启动命令：`gunicorn app:app`
4. 设置环境变量

### Vercel部署
配置`vercel.json`，使用serverless模式部署。

## 注意事项

1. **API密钥安全**: 生产环境请使用真实API密钥，勿使用示例密钥
2. **文件大小限制**: 单文件最大50MB，建议使用高质量录音
3. **网络连接**: 语音识别和AI分析需要稳定的网络连接
4. **数据存储**: SQLite数据库文件存储在`data/analysis.db`
5. **临时文件**: 上传的文件存储在`uploads/`或`/tmp/uploads/`

## 故障排查

### 常见问题

**Q: 文件上传失败？**
- 检查文件格式是否为MP3
- 确认文件大小不超过50MB
- 检查网络连接

**Q: 语音识别失败？**
- 确认火山引擎API密钥有效
- 检查录音音质是否清晰
- 验证API配额是否充足

**Q: AI分析失败？**
- 确认DeepSeek API密钥有效
- 检查网络连接
- 验证API调用配额

**Q: PDF中文显示为方框？**
- 系统会自动下载中文字体
- 确保网络连接正常
- 检查字体目录权限

## 许可证

MIT License

## 版本历史

- **v1.0**: 初始版本，支持单文件分析和基本AI分析
- **v1.1**: 添加批量处理和历史记录管理
- **v1.2**: 添加统计分析仪表盘和PDF导出
- **v1.3**: 优化说话人分离算法，添加长音频支持

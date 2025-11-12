# AI 旅行规划师 (AI Travel Planner)

基于 Python Flask 的 Web 版 AI 旅行规划应用，通过大语言模型自动生成个性化旅行计划。

## 功能特性

### 1. 智能行程规划
- 支持语音和文字输入旅行需求
- AI 自动生成详细的旅行路线
- 包含交通、住宿、景点、餐厅等完整信息

### 2. 费用预算与管理
- AI 智能预算分析
- 实时记录旅行开销
- 支持语音记录费用

### 3. 用户管理与数据存储
- 注册登录系统
- 保存和管理多份旅行计划
- 云端数据同步（可选）

### 4. 地图导航
- 集成高德地图
- 可视化展示旅行路线
- 地理位置服务

## 技术栈

- **后端**: Flask (Python)
- **前端**: HTML + CSS + JavaScript
- **AI**: 通义千问 (DashScope API)
- **语音识别**: Web Speech API (浏览器原生) / 科大讯飞 API
- **地图**: 高德地图 API
- **数据库**: SQLite (本地) / Supabase (云端可选)
- **认证**: Flask-Login

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Flask 配置
SECRET_KEY=your-secret-key-here

# AI 服务配置 - 通义千问
DASHSCOPE_API_KEY=
QWEN_MODEL=

# 科大讯飞语音识别（可选）
XFYUN_APP_ID=
XFYUN_API_KEY=
XFYUN_API_SECRET=

# 高德地图
AMAP_API_KEY=
```

### 3. 运行应用

```bash
python app.py
```

访问 http://localhost:5000

## API 密钥获取

### 通义千问 API
1. 访问阿里云百炼平台：https://dashscope.aliyun.com/
2. 登录/注册阿里云账号
3. 开通 DashScope 服务
4. 在控制台获取 API Key
5. 可选模型：
   - `qwen-turbo`: 快速响应，适合简单任务
   - `qwen-plus`: 平衡性能和成本（推荐）
   - `qwen-max`: 最强性能，适合复杂任务

### 高德地图 API（Web 端 JS API）
1. 访问 https://lbs.amap.com/
2. 注册开发者账号
3. 进入控制台 → 应用管理 → 我的应用
4. 创建新应用（或使用现有应用）
5. 添加 Key：
   - 服务平台：选择 "Web端(JS API)"
   - 填写应用名称
6. 获取 Key 和安全密钥（Jscode）

### 科大讯飞语音识别（可选）
1. 访问 https://www.xfyun.cn/
2. 注册并创建应用
3. 获取 APPID、API Key 和 API Secret

## 项目结构

```
ai-travel-planner/
├── app.py                 # Flask 主应用
├── config.py             # 配置文件
├── requirements.txt      # Python 依赖
├── .env                  # 环境变量（需自行创建）
├── static/               # 静态文件
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/            # HTML 模板
│   ├── index.html       # 首页
│   ├── login.html       # 登录/注册页
│   └── planner.html     # 规划器主页
└── utils/               # 工具模块
    ├── ai_service.py    # AI 服务
    ├── voice_service.py # 语音识别
    └── db_service.py    # 数据库服务
```

## 使用说明

### 1. 注册/登录
- 首次使用需要注册账号
- 登录后可保存和管理多个旅行计划

### 2. 创建旅行计划
- 点击"新建计划"
- 输入旅行需求（文字或语音）
- 例如："我想去日本，5天，预算1万元，喜欢美食和动漫，带孩子"
- 点击"生成计划"

### 3. 查看计划
- 左侧显示所有已保存的计划
- 点击计划可查看详情
- 包含地图、行程、住宿、预算等信息

### 4. 记录费用
- 在计划详情页底部
- 填写费用类别、金额、日期
- 支持语音输入

## 注意事项

1. **语音识别**: 浏览器原生语音识别需要 HTTPS 环境（本地开发除外）
2. **地图 API**: 需要在 `templates/planner.html` 中替换高德地图 Key
3. **AI 模型**: 默认使用 GPT-3.5，可根据需要调整模型
4. **数据库**: 默认使用 SQLite，生产环境建议使用 PostgreSQL

## 扩展功能

### 使用 Supabase 云端同步

**已配置完成！** 你的 Supabase 配置已添加到 `.env` 文件。

**设置步骤：**

1. **创建数据库表：**
   - 登录 Supabase 控制台：https://supabase.com/dashboard
   - 进入你的项目：vowpckjnqyegubqlsuki
   - 点击左侧 "SQL Editor"
   - 复制 `supabase_setup.sql` 文件内容并执行

2. **运行应用：**
   ```bash
   python app.py
   ```
   如果看到 "使用 Supabase 云端数据库"，说明配置成功！

3. **切换数据库：**
   - 有 Supabase 配置：自动使用云端数据库
   - 删除 Supabase 配置：使用本地 SQLite

详细说明请查看 `SUPABASE_SETUP.md`

### 使用科大讯飞语音识别
1. 获取科大讯飞 API 密钥
2. 在 `.env` 中配置
3. 修改前端 JavaScript 使用科大讯飞 WebSocket API

## 常见问题

**Q: 语音识别不工作？**
A: 确保使用 Chrome/Edge 浏览器，并允许麦克风权限。

**Q: AI 生成计划失败？**
A: 检查通义千问 API Key 是否正确，DashScope 服务是否已开通。

**Q: 地图不显示？**
A: 确保高德地图 API Key 已正确配置。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

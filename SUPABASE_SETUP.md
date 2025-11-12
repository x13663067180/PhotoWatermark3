# Supabase 云端数据库配置指南

## 1. 创建 Supabase 项目

1. 访问 https://supabase.com/
2. 注册/登录账号
3. 点击 "New Project"
4. 填写项目信息：
   - Name: ai-travel-planner
   - Database Password: 设置一个强密码
   - Region: 选择离你最近的区域（如 Singapore）
5. 等待项目创建完成（约 2 分钟）

## 2. 获取 API 密钥

1. 在项目控制台，点击左侧 "Settings" → "API"
2. 找到以下信息：
   - **Project URL**: 类似 `https://xxxxx.supabase.co`
   - **anon public key**: 以 `eyJ...` 开头的长字符串

## 3. 创建数据库表

1. 点击左侧 "SQL Editor"
2. 点击 "New query"
3. 复制 `supabase_setup.sql` 文件的全部内容
4. 粘贴到编辑器中
5. 点击 "Run" 执行

执行成功后，你会看到以下表被创建：
- `users` - 用户表
- `travel_plans` - 旅行计划表
- `expenses` - 费用记录表

## 4. 配置环境变量

在 `.env` 文件中添加：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

## 5. 验证配置

运行应用：
```bash
python app.py
```

如果看到 "使用 Supabase 云端数据库"，说明配置成功！

## 数据库表结构

### users 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL | 主键 |
| username | TEXT | 用户名（唯一） |
| email | TEXT | 邮箱（唯一） |
| password_hash | TEXT | 密码哈希 |
| created_at | TIMESTAMP | 创建时间 |

### travel_plans 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL | 主键 |
| user_id | BIGINT | 用户 ID（外键） |
| title | TEXT | 计划标题 |
| plan_data | JSONB | 计划详情（JSON） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### expenses 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL | 主键 |
| plan_id | BIGINT | 计划 ID（外键） |
| user_id | BIGINT | 用户 ID（外键） |
| category | TEXT | 费用类别 |
| amount | DECIMAL | 金额 |
| description | TEXT | 描述 |
| date | DATE | 日期 |
| created_at | TIMESTAMP | 创建时间 |

## 安全策略 (RLS)

Supabase 已启用行级安全策略（Row Level Security），确保：
- 用户只能访问自己的数据
- 防止未授权访问
- 数据隔离和安全

## 优势

✅ **云端同步**: 多设备自动同步数据
✅ **实时更新**: 支持实时数据订阅
✅ **自动备份**: Supabase 自动备份数据
✅ **可扩展性**: 支持大量用户和数据
✅ **免费额度**: 每月 500MB 数据库存储，50,000 次 API 请求

## 切换回本地数据库

如果想使用本地 SQLite 数据库，只需：
1. 在 `.env` 中删除或注释掉 `SUPABASE_URL` 和 `SUPABASE_KEY`
2. 重启应用

应用会自动检测并切换到本地数据库。

## 常见问题

**Q: 表创建失败？**
A: 确保 SQL 脚本完整执行，检查是否有错误提示。

**Q: 连接失败？**
A: 检查 URL 和 Key 是否正确，网络是否正常。

**Q: 数据不同步？**
A: 确认 `.env` 配置正确，重启应用。

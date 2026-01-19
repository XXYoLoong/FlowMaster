# FlowMaster AI - 每日流水统计与管理系统

Copyright 2026 Jiacheng Ni

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

一个功能完整的每日流水统计与管理系统，支持数据录入、多级报表统计、员工管理，并集成AI对话功能。

## 功能特性

### 核心功能
- ✅ **数据录入**：支持录入日期、员工、数量、总金额、金额明细
- ✅ **数据加密**：金额明细等敏感数据采用AES加密存储
- ✅ **权限管理**：前台员工和店长两级权限控制
- ✅ **多级报表**：
  - 每日小结：统计每日各员工的服务次数和总收入
  - 每周小结：统计每周各员工的业绩
  - 每月小结：统计每月各员工的业绩，包含日均金额
  - 年报：统计全年各员工的业绩，包含月度趋势
  - 管理层报表：综合指标分析，包含增长率、员工排名、支付方式统计等

### AI功能
- ✅ **LangChain + LangGraph工作流**：智能意图识别和参数提取
- ✅ **多AI支持**：支持Deep Seek API和通义千问API
- ✅ **自然语言交互**：通过对话完成数据录入、查询、报表生成等操作
- ✅ **双UI模式**：原版UI和AI对话UI两种界面

### UI特性
- ✅ **完全响应式设计**：完美适配手机和电脑
- ✅ **现代化界面**：创新的UI设计，美观易用
- ✅ **双界面模式**：原版UI和AI对话UI可自由切换

## 技术栈

### 后端
- Python 3.8+
- Flask 3.0.0
- SQLAlchemy（数据库ORM）
- Flask-JWT-Extended（JWT认证）
- Cryptography（数据加密）
- LangChain + LangGraph（AI工作流）

### 前端
- HTML5 + CSS3
- 原生JavaScript（无框架依赖）
- 响应式设计

### 数据库
- SQLite（默认，适合小型应用）
- 支持MySQL（生产环境）

## 安装和运行

### 1. 克隆项目

```bash
git clone <repository-url>
cd FlowMaster-AI
```

### 2. 创建虚拟环境（推荐）

为了隔离项目依赖，建议使用虚拟环境。如果您的电脑安装了多个Python版本，可以指定版本创建虚拟环境。

#### Windows系统

```bash
# 方式1：使用默认Python版本创建虚拟环境
python -m venv venv

# 方式2：指定Python版本创建虚拟环境（例如使用Python 3.10）
py -3.10 -m venv venv
# 或者
python3.10 -m venv venv

# 方式3：使用完整路径指定Python版本
C:\Python310\python.exe -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

#### Linux/Mac系统

```bash
# 方式1：使用默认Python版本创建虚拟环境
python3 -m venv venv

# 方式2：指定Python版本创建虚拟环境（例如使用Python 3.10）
python3.10 -m venv venv
# 或者
/usr/bin/python3.10 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

#### 查看已安装的Python版本

**Windows:**
```bash
# 查看所有已安装的Python版本
py --list

# 或查看Python版本
python --version
python3 --version
```

**Linux/Mac:**
```bash
# 查看Python版本
python3 --version
python3.8 --version
python3.9 --version
python3.10 --version
python3.11 --version

# 查看所有Python可执行文件位置
which -a python3
```

**注意：**
- 推荐使用 Python 3.8 或更高版本
- 虚拟环境创建成功后，命令提示符前会显示 `(venv)` 标识
- 退出虚拟环境：输入 `deactivate` 命令

### 3. 安装依赖

```bash
# 确保已激活虚拟环境（命令提示符前有 (venv)）
pip install -r requirements.txt

# 如果使用国内网络，可以使用清华镜像加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 配置环境变量

创建 `.env` 文件（参考 `env.txt`，配置完成后请将 `env.txt` 重命名为 `.env`）：

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key-here!!

# AI API配置（可选）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_BASE=https://api.deepseek.com

# 通义千问API配置（可选）
# 支持两种环境变量名：DASHSCOPE_API_KEY 或 QIANWEN_API_KEY
QIANWEN_API_KEY=your-qianwen-api-key
QIANWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 数据库配置（可选，默认使用SQLite）
DATABASE_URL=sqlite:///flowmaster.db
```

### 5. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 默认账户

- **示例账户（只读）**
  - 用户名：`admin`
  - 密码：`admin123`
  - 权限：只能查看界面，**不能进行任何数据操作**
  - 用途：用于演示和查看系统界面

**注意**：
- 示例账号只能查看，不能录入、修改、删除数据
- 实际使用需要在数据库中手动创建账号
- 店长权限通过 `role='manager'` 字段识别
- 前台员工权限通过 `role='staff'` 字段识别

## 使用说明

### 原版UI模式

1. 访问 `http://localhost:5000` 进入原版UI
2. 使用默认账户登录
3. 功能标签页：
   - **数据录入**：录入每日流水数据
   - **流水列表**：查看和筛选流水记录
   - **报表统计**：生成各类报表
   - **员工管理**（仅店长）：添加和管理员工

### AI对话模式

1. 访问 `http://localhost:5000/ai` 进入AI对话UI
2. 使用默认账户登录
3. 直接通过自然语言与AI交互，例如：
   - "录入今天的流水：张三，数量6，总金额560，金额明细：微信80, 微信100"
   - "查询今天的流水数据"
   - "显示今天的日报"
   - "显示本周的周报"（仅店长）
   - "显示管理层综合报表"（仅店长）

## API文档

### 认证接口

#### 登录
```
POST /api/auth/login
Body: { "username": "admin", "password": "admin123" }
```

#### 获取当前用户
```
GET /api/auth/me
Headers: Authorization: Bearer <token>
```

### 数据接口

#### 创建流水记录
```
POST /api/transactions
Headers: Authorization: Bearer <token>
Body: {
  "date": "2025-01-01",
  "employee_id": 1,
  "quantity": 6,
  "total_amount": 560.00,
  "amount_details": "微信80, 微信100, 支付宝100"
}
```

#### 获取流水列表
```
GET /api/transactions?page=1&per_page=20&start_date=2025-01-01&end_date=2025-01-31
Headers: Authorization: Bearer <token>
```

### 报表接口

#### 每日小结
```
GET /api/reports/daily?date=2025-01-01
Headers: Authorization: Bearer <token>
```

#### 每周小结
```
GET /api/reports/weekly?year=2025&week=1
Headers: Authorization: Bearer <token>
```

#### 每月小结
```
GET /api/reports/monthly?year=2025&month=1
Headers: Authorization: Bearer <token>
```

#### 年报
```
GET /api/reports/yearly?year=2025
Headers: Authorization: Bearer <token>
```

#### 管理层报表
```
GET /api/reports/management?start_date=2025-01-01&end_date=2025-01-31
Headers: Authorization: Bearer <token>
```

### AI接口

#### AI对话
```
POST /api/ai/chat
Headers: Authorization: Bearer <token>
Body: {
  "message": "查询今天的流水数据",
  "history": []
}
```

## 数据加密

系统使用Fernet对称加密对金额明细等敏感数据进行加密存储。加密密钥通过PBKDF2从配置的密钥派生，确保数据安全。

## 安全建议

1. **生产环境配置**：
   - 修改所有默认密钥（SECRET_KEY、JWT_SECRET_KEY、ENCRYPTION_KEY）
   - 使用强密码策略
   - 启用HTTPS

2. **数据库**：
   - 生产环境建议使用MySQL或PostgreSQL
   - 定期备份数据库

3. **API密钥**：
   - 妥善保管AI API密钥
   - 不要将密钥提交到版本控制系统

## 项目结构

```
FlowMaster-AI/
├── app.py                 # 主应用入口
├── config.py              # 配置文件
├── models.py              # 数据库模型
├── ai_workflow.py         # AI工作流
├── requirements.txt       # Python依赖
├── README.md              # 项目说明
├── env.txt                # 环境变量示例（配置后重命名为.env）
├── routes/                # 路由模块
│   ├── __init__.py
│   ├── auth.py           # 认证路由
│   ├── api.py            # API路由
│   └── ai.py             # AI路由
├── templates/             # HTML模板
│   ├── index.html        # 原版UI
│   └── ai_chat.html      # AI对话UI
└── static/               # 静态文件
    ├── css/
    │   ├── style.css     # 原版UI样式
    │   └── ai_chat.css   # AI对话UI样式
    └── js/
        ├── app.js        # 原版UI脚本
        └── ai_chat.js    # AI对话UI脚本
```

## 用户管理说明

### 创建实际用户账号

系统初始化时只创建示例账号 `admin/admin123`（只读模式）。实际使用需要在数据库中手动创建账号：

#### 方法1：通过系统界面创建（推荐）

1. 使用管理员账号（`role='manager'`）登录
2. 进入"员工管理"标签页
3. 点击"添加员工"按钮
4. 填写信息并选择角色：
   - `role='manager'` → 店长（最高权限）
   - `role='staff'` → 前台员工（只能录入和查看当日数据）

#### 方法2：直接在数据库中创建

```sql
-- 创建店长账号
INSERT INTO users (username, password_hash, role, real_name, is_active, is_demo)
VALUES ('manager1', '<加密后的密码>', 'manager', '店长姓名', 1, 0);

-- 创建前台员工账号
INSERT INTO users (username, password_hash, role, real_name, is_active, is_demo)
VALUES ('staff1', '<加密后的密码>', 'staff', '员工姓名', 1, 0);
```

**重要说明**：
- `role='manager'` → 店长，拥有最高权限（查看所有数据、生成所有报表、管理员工）
- `role='staff'` → 前台员工，只能录入和查看当日数据
- `is_demo=0` → 实际账号，可以进行所有操作
- `is_demo=1` → 示例账号，只能查看，不能写入数据

### 密码加密

如果直接在数据库中创建账号，需要使用Python生成密码哈希：

```python
from werkzeug.security import generate_password_hash
password_hash = generate_password_hash('your_password')
print(password_hash)
```

## 开发说明

### 添加新的报表类型

1. 在 `routes/api.py` 中添加新的报表路由
2. 在前端 `static/js/app.js` 中添加报表加载和渲染函数
3. 在AI工作流 `ai_workflow.py` 中添加意图识别

### 扩展AI功能

1. 在 `ai_workflow.py` 中修改意图分类和参数提取逻辑
2. 在 `routes/ai.py` 中添加对应的API调用处理
3. 更新前端AI对话UI以支持新功能

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。


# 快速启动指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 初始化数据库（可选）

```bash
python init_db.py
```

## 3. 启动应用

```bash
python run.py
```

或者直接运行：

```bash
python app.py
```

## 4. 访问系统

- **原版UI**: http://localhost:5000
- **AI对话UI**: http://localhost:5000/ai

## 5. 登录

使用默认账户登录：

- **管理员**: admin / admin123
- **前台员工**: staff / staff123

## 功能测试

### 原版UI测试

1. 登录后，切换到"数据录入"标签
2. 填写表单并提交一条流水记录
3. 切换到"流水列表"查看记录
4. 切换到"报表统计"生成各类报表

### AI对话UI测试

1. 访问 `/ai` 页面
2. 登录后，尝试以下对话：
   - "录入今天的流水：张三，数量6，总金额560，金额明细：微信80, 微信100"
   - "查询今天的流水数据"
   - "显示今天的日报"

## 配置AI API（可选）

如果需要使用AI对话功能，需要配置API密钥：

1. 复制 `env.txt` 文件并重命名为 `.env`
2. 编辑 `.env` 文件，添加以下配置：

```env
DEEPSEEK_API_KEY=your-api-key
QIANWEN_API_KEY=your-api-key
```

如果不配置AI API，系统仍可正常使用，但AI对话功能会使用默认响应。

## 常见问题

### 1. 端口被占用

修改 `config.py` 中的 `PORT` 配置，或设置环境变量：

```bash
export PORT=5001
python run.py
```

### 2. 数据库错误

删除 `flowmaster.db` 文件，然后重新运行 `init_db.py`

### 3. AI功能不可用

检查 `.env` 文件中的API密钥配置是否正确（如果使用env.txt，请确保已重命名为.env）

## 生产环境部署

1. 修改所有默认密钥
2. 使用MySQL或PostgreSQL替代SQLite
3. 配置HTTPS
4. 使用Gunicorn或uWSGI部署

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```


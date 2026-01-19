import os
from datetime import timedelta
from dotenv import load_dotenv

# 尝试加载.env文件，如果不存在则尝试加载env.txt
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('env.txt'):
    load_dotenv('env.txt')
    print("提示: 检测到env.txt文件，建议将其重命名为.env")
else:
    load_dotenv()  # 默认尝试加载.env

class Config:
    """应用配置类"""
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///flowmaster.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # MySQL连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # 连接前测试连接是否有效
        'pool_recycle': 3600,  # 连接回收时间（秒）
        'connect_args': {
            'connect_timeout': 10  # 连接超时时间（秒）
        }
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production-2025'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 数据加密配置
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'your-32-byte-encryption-key-here!!'
    
    # AI API配置
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or ''
    DEEPSEEK_API_BASE = os.environ.get('DEEPSEEK_API_BASE') or 'https://api.deepseek.com'
    
    # 通义千问API配置（支持DASHSCOPE_API_KEY和QIANWEN_API_KEY）
    QIANWEN_API_KEY = os.environ.get('DASHSCOPE_API_KEY') or os.environ.get('QIANWEN_API_KEY') or ''
    QIANWEN_API_BASE = os.environ.get('QIANWEN_API_BASE') or 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    
    # 应用配置
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))


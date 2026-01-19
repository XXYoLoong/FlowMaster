"""
路由模块初始化
"""
from .auth import auth_bp
from .api import api_bp
from .ai import ai_bp

__all__ = ['auth_bp', 'api_bp', 'ai_bp']


"""
FlowMaster AI - 每日流水统计与管理系统
主应用入口文件

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
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db, init_db
from routes import api_bp, auth_bp, ai_bp
from ai_workflow import init_ai_workflow

def create_app():
    """创建Flask应用"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)
    
    # 如果使用MySQL，添加连接池配置
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('mysql'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = Config.SQLALCHEMY_ENGINE_OPTIONS
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    jwt = JWTManager(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # 初始化AI工作流
    init_ai_workflow()
    
    # 初始化数据库（连接失败时不影响应用启动）
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            print(f"警告: 数据库初始化失败: {e}")
            print("应用将继续启动，但数据库功能可能不可用")
            print("请检查数据库连接配置或网络连接")
    
    @app.route('/')
    def index():
        """首页 - 原版UI"""
        return render_template('index.html')
    
    @app.route('/ai')
    def ai_chat():
        """AI对话UI"""
        return render_template('ai_chat.html')
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# 创建应用实例（供gunicorn使用）
app = create_app()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FlowMaster AI 启动脚本
"""
import os
from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # 确保必要的目录存在
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 50)
    print("FlowMaster AI - 每日流水统计与管理系统")
    print("=" * 50)
    print(f"服务器地址: http://{app.config['HOST']}:{app.config['PORT']}")
    print(f"原版UI: http://{app.config['HOST']}:{app.config['PORT']}/")
    print(f"AI对话UI: http://{app.config['HOST']}:{app.config['PORT']}/ai")
    print("=" * 50)
    print("默认账户:")
    print("  管理员 - 用户名: admin, 密码: admin123")
    print("  前台员工 - 用户名: staff, 密码: staff123")
    print("=" * 50)
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )


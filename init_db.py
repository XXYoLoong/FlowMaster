#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""
from app import create_app
from models import db, init_db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("正在初始化数据库...")
        init_db()
        print("数据库初始化完成！")
        print("默认账户:")
        print("  管理员 - 用户名: admin, 密码: admin123")
        print("  前台员工 - 用户名: staff, 密码: staff123")


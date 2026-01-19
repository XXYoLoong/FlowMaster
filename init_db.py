#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本

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


"""
数据库迁移脚本：添加 is_demo 列到 users 表

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
import pymysql
import os
from config import Config

def migrate():
    """执行数据库迁移"""
    try:
        # 从 DATABASE_URL 解析连接信息
        db_url = Config.DATABASE_URL
        if not db_url:
            print("错误: 未找到数据库连接配置")
            return False
        
        # 解析 MySQL 连接字符串
        # 格式: mysql+pymysql://user:password@host:port/database
        if db_url.startswith('mysql+pymysql://'):
            db_url = db_url.replace('mysql+pymysql://', '')
        
        # 解析用户名、密码、主机、端口、数据库名
        parts = db_url.split('@')
        if len(parts) != 2:
            print("错误: 数据库连接字符串格式不正确")
            return False
        
        user_pass = parts[0].split(':')
        if len(user_pass) != 2:
            print("错误: 无法解析用户名和密码")
            return False
        
        username = user_pass[0]
        password = user_pass[1]
        
        host_port_db = parts[1].split('/')
        if len(host_port_db) != 2:
            print("错误: 无法解析主机、端口和数据库名")
            return False
        
        host_port = host_port_db[0].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        database = host_port_db[1]
        
        # URL 解码密码（如果有特殊字符）
        from urllib.parse import unquote
        password = unquote(password)
        
        print(f"正在连接到数据库: {host}:{port}/{database}")
        
        # 连接数据库
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        try:
            with connection.cursor() as cursor:
                # 检查并添加 is_demo 列
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'users' 
                    AND COLUMN_NAME = 'is_demo'
                """, (database,))
                
                if not cursor.fetchone():
                    print("正在添加 is_demo 列...")
                    cursor.execute("""
                        ALTER TABLE users 
                        ADD COLUMN is_demo BOOLEAN DEFAULT FALSE 
                        AFTER is_active
                    """)
                    connection.commit()
                    print("✓ 成功添加 is_demo 列")
                else:
                    print("✓ is_demo 列已存在")
                
                # 检查并添加 password_changed_at 列
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'users' 
                    AND COLUMN_NAME = 'password_changed_at'
                """, (database,))
                
                if not cursor.fetchone():
                    print("正在添加 password_changed_at 列...")
                    cursor.execute("""
                        ALTER TABLE users 
                        ADD COLUMN password_changed_at DATETIME DEFAULT NULL 
                        AFTER is_demo
                    """)
                    connection.commit()
                    print("✓ 成功添加 password_changed_at 列")
                else:
                    print("✓ password_changed_at 列已存在")
                
                # 更新 admin 用户的 is_demo 为 True
                cursor.execute("""
                    UPDATE users 
                    SET is_demo = TRUE 
                    WHERE username = 'admin'
                """)
                
                connection.commit()
                print("✓ 已设置 admin 用户为示例账号")
                
                # 创建店长账户和前台员工账户
                from werkzeug.security import generate_password_hash
                
                # 创建店长账户
                cursor.execute("SELECT id FROM users WHERE username = 'nzpmrylams'")
                if not cursor.fetchone():
                    manager_password_hash = generate_password_hash('yoloong819170')
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, role, real_name, is_active, is_demo, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """, ('nzpmrylams', manager_password_hash, 'manager', '店长账户', True, False))
                    connection.commit()
                    print("✓ 已创建店长账户: nzpmrylams")
                else:
                    print("⚠ 店长账户 nzpmrylams 已存在，跳过创建")
                
                # 创建前台员工账户
                cursor.execute("SELECT id FROM users WHERE username = 'cqyg'")
                if not cursor.fetchone():
                    staff_password_hash = generate_password_hash('123456')
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, role, real_name, is_active, is_demo, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """, ('cqyg', staff_password_hash, 'staff', '前台员工', True, False))
                    connection.commit()
                    print("✓ 已创建前台员工账户: cqyg")
                else:
                    print("⚠ 前台员工账户 cqyg 已存在，跳过创建")
                
                return True
                
        finally:
            connection.close()
            
    except pymysql.Error as e:
        print(f"数据库错误: {e}")
        return False
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("数据库迁移：添加 is_demo 列")
    print("=" * 50)
    
    if migrate():
        print("\n✓ 迁移完成！")
    else:
        print("\n✗ 迁移失败，请检查错误信息")
        exit(1)


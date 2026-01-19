#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MySQL连接诊断工具
用于排查数据库连接问题

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
import socket
import sys
from config import Config
import pymysql

def test_network_connectivity(host, port, timeout=5):
    """测试网络连通性"""
    print(f"\n{'='*60}")
    print(f"1. 测试网络连通性: {host}:{port}")
    print(f"{'='*60}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {port} 可达")
            return True
        else:
            print(f"❌ 端口 {port} 不可达 (错误代码: {result})")
            print(f"   可能原因: 端口未开放、防火墙阻止、服务未运行")
            return False
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {e}")
        print(f"   可能原因: 主机名无法解析")
        return False
    except socket.timeout:
        print(f"❌ 连接超时 (超过 {timeout} 秒)")
        print(f"   可能原因: 防火墙阻止、服务未运行、网络路由问题")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_mysql_connection():
    """测试MySQL连接"""
    print(f"\n{'='*60}")
    print("2. 测试MySQL数据库连接")
    print(f"{'='*60}")
    
    # 从配置获取连接信息
    db_url = Config.SQLALCHEMY_DATABASE_URI
    
    if not db_url or not db_url.startswith('mysql'):
        print("❌ 未配置MySQL数据库URL")
        return False
    
    # 解析连接字符串
    # mysql+pymysql://user:password@host:port/database
    try:
        # 移除 mysql+pymysql:// 前缀
        url_part = db_url.replace('mysql+pymysql://', '')
        
        # 分离认证信息和地址
        if '@' in url_part:
            auth_part, address_part = url_part.split('@', 1)
            user, password = auth_part.split(':', 1)
            password = password  # URL编码的密码，需要解码
        else:
            print("❌ 数据库URL格式错误")
            return False
        
        # 分离地址和数据库名
        if '/' in address_part:
            address, database = address_part.split('/', 1)
        else:
            address = address_part
            database = ''
        
        # 分离主机和端口
        if ':' in address:
            host, port = address.split(':')
            port = int(port)
        else:
            host = address
            port = 3306
        
        # URL解码密码
        import urllib.parse
        password = urllib.parse.unquote(password)
        
        print(f"连接信息:")
        print(f"  主机: {host}")
        print(f"  端口: {port}")
        print(f"  用户: {user}")
        print(f"  数据库: {database}")
        print(f"  密码: {'*' * len(password)}")
        
        # 先测试网络连通性
        if not test_network_connectivity(host, port):
            print("\n⚠️  网络连通性测试失败，无法继续MySQL连接测试")
            return False
        
        # 测试MySQL连接
        print(f"\n尝试连接MySQL...")
        try:
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database if database else None,
                connect_timeout=10,
                charset='utf8mb4'
            )
            
            print("✅ MySQL连接成功！")
            
            # 测试查询
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"   MySQL版本: {version[0]}")
                
                cursor.execute("SELECT DATABASE()")
                current_db = cursor.fetchone()
                print(f"   当前数据库: {current_db[0] if current_db[0] else 'None'}")
                
                cursor.execute("SELECT USER()")
                current_user = cursor.fetchone()
                print(f"   当前用户: {current_user[0]}")
            
            connection.close()
            return True
            
        except pymysql.err.OperationalError as e:
            error_code, error_msg = e.args
            print(f"❌ MySQL连接失败")
            print(f"   错误代码: {error_code}")
            print(f"   错误信息: {error_msg}")
            
            if error_code == 2003:
                print("\n   可能原因:")
                print("   - MySQL服务未运行")
                print("   - 防火墙阻止了连接")
                print("   - 主机地址或端口错误")
            elif error_code == 1045:
                print("\n   可能原因:")
                print("   - 用户名或密码错误")
                print("   - 用户不存在")
            elif error_code == 1049:
                print("\n   可能原因:")
                print("   - 数据库不存在")
            elif error_code == 1130:
                print("\n   可能原因:")
                print("   - 用户没有远程连接权限")
                print("   - MySQL配置不允许远程连接")
            
            return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 解析数据库URL失败: {e}")
        return False

def check_vpn_connectivity():
    """检查VPN连接"""
    print(f"\n{'='*60}")
    print("3. 检查VPN连接")
    print(f"{'='*60}")
    
    import subprocess
    try:
        # Windows下检查路由表
        result = subprocess.run(
            ['route', 'print'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if '10.99.0.0' in result.stdout or '10.99.0' in result.stdout:
            print("✅ 检测到VPN路由 (10.99.0.0/24)")
        else:
            print("⚠️  未检测到VPN路由，可能VPN未正确连接")
            
        # 检查是否能ping通目标主机
        host = "8.153.38.232"
        print(f"\n尝试ping {host}...")
        ping_result = subprocess.run(
            ['ping', '-n', '2', host],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if ping_result.returncode == 0:
            print(f"✅ 可以ping通 {host}")
        else:
            print(f"❌ 无法ping通 {host}")
            print("   可能原因: VPN路由配置问题、目标主机不可达")
            
    except Exception as e:
        print(f"⚠️  无法检查VPN状态: {e}")

def main():
    """主函数"""
    print("="*60)
    print("MySQL连接诊断工具")
    print("="*60)
    
    # 检查配置
    print(f"\n当前数据库配置:")
    db_url = Config.SQLALCHEMY_DATABASE_URI
    if db_url.startswith('mysql'):
        print(f"  {db_url[:50]}...")  # 只显示前50个字符，避免显示完整密码
    else:
        print(f"  {db_url}")
        print("\n⚠️  当前配置不是MySQL，请检查env.txt文件")
        return
    
    # 测试网络连通性
    if db_url.startswith('mysql'):
        # 解析主机和端口
        try:
            url_part = db_url.replace('mysql+pymysql://', '')
            if '@' in url_part:
                address_part = url_part.split('@', 1)[1]
                if '/' in address_part:
                    address = address_part.split('/', 1)[0]
                else:
                    address = address_part
                
                if ':' in address:
                    host, port = address.split(':')
                    port = int(port)
                else:
                    host = address
                    port = 3306
                
                # 测试网络连通性
                test_network_connectivity(host, port)
                
                # 检查VPN
                if host.startswith('8.153.38') or host.startswith('10.99'):
                    check_vpn_connectivity()
                
                # 测试MySQL连接
                test_mysql_connection()
            else:
                print("❌ 无法解析数据库URL")
        except Exception as e:
            print(f"❌ 解析失败: {e}")
    
    print(f"\n{'='*60}")
    print("诊断完成")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()


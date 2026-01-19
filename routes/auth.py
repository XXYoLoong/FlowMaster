"""
认证相关路由

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
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 403
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def public_register():
    """公开注册（创建普通工人账号）"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        real_name = data.get('real_name', '').strip()
        
        # 输入验证
        if not username or not password or not real_name:
            return jsonify({'error': '用户名、密码和真实姓名不能为空'}), 400
        
        # 用户名格式验证（防止注入）
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须在3-20个字符之间'}), 400
        
        if not username.replace('_', '').replace('-', '').isalnum():
            return jsonify({'error': '用户名只能包含字母、数字、下划线和连字符'}), 400
        
        # 密码强度验证
        if len(password) < 6:
            return jsonify({'error': '密码长度至少6个字符'}), 400
        
        # 真实姓名验证
        if len(real_name) < 2 or len(real_name) > 50:
            return jsonify({'error': '真实姓名长度必须在2-50个字符之间'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        # 创建普通工人账号（默认角色）
        user = User(
            username=username,
            real_name=real_name,
            role='worker'  # 默认创建为普通工人
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '注册成功！您现在可以登录了',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/register-manager', methods=['POST'])
@jwt_required()
def register_manager():
    """注册新用户（仅管理员可用，可创建任意角色）"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # 检查是否为示例账号
        if current_user and current_user.is_demo:
            return jsonify({'error': '示例账号不能创建新用户。请使用实际管理员账号登录。'}), 403
        
        if current_user.role != 'manager':
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        real_name = data.get('real_name', '').strip()
        role = data.get('role', 'staff')
        
        if not username or not password or not real_name:
            return jsonify({'error': '用户名、密码和真实姓名不能为空'}), 400
        
        # 用户名格式验证
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须在3-20个字符之间'}), 400
        
        if not username.replace('_', '').replace('-', '').isalnum():
            return jsonify({'error': '用户名只能包含字母、数字、下划线和连字符'}), 400
        
        # 密码强度验证
        if len(password) < 6:
            return jsonify({'error': '密码长度至少6个字符'}), 400
        
        # 角色验证
        if role not in ['worker', 'staff', 'manager']:
            return jsonify({'error': '无效的角色'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        user = User(
            username=username,
            real_name=real_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': '用户创建成功', 'user': user.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码（每天限制1次）"""
    try:
        from datetime import datetime, timedelta
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查是否为示例账号
        if user.is_demo:
            return jsonify({'error': '示例账号不能修改密码'}), 403
        
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'error': '原密码和新密码不能为空'}), 400
        
        # 验证原密码
        if not user.check_password(old_password):
            return jsonify({'error': '原密码错误'}), 400
        
        # 检查新密码强度
        if len(new_password) < 6:
            return jsonify({'error': '新密码长度至少6个字符'}), 400
        
        # 检查是否与原密码相同
        if user.check_password(new_password):
            return jsonify({'error': '新密码不能与原密码相同'}), 400
        
        # 检查今天是否已经修改过密码
        if user.password_changed_at:
            last_change_date = user.password_changed_at.date()
            today = datetime.now().date()
            if last_change_date == today:
                return jsonify({
                    'error': '每天只能修改一次密码，请明天再试',
                    'next_change_time': (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).isoformat()
                }), 403
        
        # 更新密码
        user.set_password(new_password)
        user.password_changed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': '密码修改成功',
            'password_changed_at': user.password_changed_at.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'修改密码失败: {str(e)}'}), 500


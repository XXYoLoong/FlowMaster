"""
数据库模型定义
包含数据加密功能
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json
import os

db = SQLAlchemy()

class EncryptionService:
    """数据加密服务"""
    
    @staticmethod
    def _get_key(password: str, salt: bytes = None) -> bytes:
        """生成加密密钥"""
        if salt is None:
            salt = b'flowmaster_salt_2025'  # 生产环境应使用随机salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    @staticmethod
    def encrypt_data(data: str, password: str = None) -> str:
        """加密数据"""
        if password is None:
            password = os.environ.get('ENCRYPTION_KEY', 'default-encryption-key-32-bytes-long!!')
        
        key = EncryptionService._get_key(password)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, password: str = None) -> str:
        """解密数据"""
        if password is None:
            password = os.environ.get('ENCRYPTION_KEY', 'default-encryption-key-32-bytes-long!!')
        
        try:
            key = EncryptionService._get_key(password)
            fernet = Fernet(key)
            decrypted = fernet.decrypt(base64.urlsafe_b64decode(encrypted_data.encode()))
            return decrypted.decode()
        except Exception as e:
            return encrypted_data  # 如果解密失败，返回原数据

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='worker')  # worker: 普通工人, staff: 前台员工, manager: 店长
    real_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_demo = db.Column(db.Boolean, default=False)  # 是否为示例账号（只读，不能写入数据）
    password_changed_at = db.Column(db.DateTime, default=None)  # 密码最后修改时间（用于限制每天修改次数）
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'real_name': self.real_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'is_demo': self.is_demo,
            'password_changed_at': self.password_changed_at.isoformat() if self.password_changed_at else None
        }

class Transaction(db.Model):
    """流水记录模型"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee = db.relationship('User', backref='transactions')
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    amount_details_encrypted = db.Column(db.Text, nullable=False)  # 加密存储的金额明细
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_amount_details(self, details: str):
        """设置金额明细（加密存储）"""
        self.amount_details_encrypted = EncryptionService.encrypt_data(details)
    
    def get_amount_details(self) -> str:
        """获取金额明细（解密）"""
        return EncryptionService.decrypt_data(self.amount_details_encrypted)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'employee_id': self.employee_id,
            'employee_name': self.employee.real_name if self.employee else None,
            'quantity': int(self.quantity) if self.quantity else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0.0,
            'amount_details': self.get_amount_details(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def init_db():
    """初始化数据库"""
    try:
        # 测试数据库连接
        db.engine.connect()
    except Exception as e:
        raise Exception(f"无法连接到数据库: {e}")
    
    db.create_all()
    
    # 只创建示例账号admin（只读，不能写入数据）
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            role='manager',
            real_name='示例管理员（只读）',
            is_demo=True  # 标记为示例账号
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("已创建示例账号: admin/admin123 (只读模式，不能写入数据)")


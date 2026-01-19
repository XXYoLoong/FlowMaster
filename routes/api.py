"""
API路由
包含数据录入、查询、报表等功能
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Transaction
from datetime import datetime, timedelta
from dateutil import parser
import calendar
from collections import defaultdict

api_bp = Blueprint('api', __name__)

def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def check_permission(user, required_role=None):
    """检查权限"""
    if required_role and user.role != required_role:
        return False
    return True

def check_demo_account(user):
    """检查是否为示例账号（示例账号禁止所有写操作）"""
    if user and user.is_demo:
        return jsonify({'error': '示例账号只能查看，不能进行写操作。请使用实际账号登录。'}), 403
    return None

def check_demo_account(user):
    """检查是否为示例账号（示例账号禁止所有写操作）"""
    if user and user.is_demo:
        return jsonify({'error': '示例账号只能查看，不能进行写操作。请使用实际账号登录。'}), 403
    return None

@api_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    """创建流水记录"""
    try:
        user = get_current_user()
        
        # 检查是否为示例账号
        demo_check = check_demo_account(user)
        if demo_check:
            return demo_check
        
        data = request.get_json()
        date_str = data.get('date')
        employee_id = data.get('employee_id')
        quantity = data.get('quantity')
        total_amount = data.get('total_amount')
        amount_details = data.get('amount_details', '')
        
        # 验证数据
        if not all([date_str, employee_id, quantity is not None, total_amount is not None]):
            return jsonify({'error': '日期、员工、数量、总金额不能为空'}), 400
        
        # 验证员工是否存在
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': '员工不存在'}), 404
        
        # 解析日期
        try:
            date = parser.parse(date_str).date()
        except:
            return jsonify({'error': '日期格式错误'}), 400
        
        # 权限检查：
        # - 普通工人只能录入自己的数据，且只能录入当日数据
        # - 前台员工和店长可以为任意员工录入数据，且可以选择任意日期
        if user.role == 'worker':
            if employee_id != user.id:
                return jsonify({'error': '您只能录入自己的数据'}), 403
            if date != datetime.now().date():
                return jsonify({'error': '您只能录入当日数据'}), 403
        # 店长和前台员工可以为任意员工录入任意日期的数据
        
        # 创建记录
        transaction = Transaction(
            date=date,
            employee_id=employee_id,
            quantity=int(quantity),
            total_amount=float(total_amount)
        )
        transaction.set_amount_details(amount_details)
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': '流水记录创建成功',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """获取流水记录列表"""
    try:
        user = get_current_user()
        
        # 查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        employee_id = request.args.get('employee_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # 构建查询
        query = Transaction.query
        
        # 权限过滤：前台员工和普通工人只能查看当日自己的数据
        if user.role in ['staff', 'worker']:
            query = query.filter(Transaction.date == datetime.now().date())
            query = query.filter(Transaction.employee_id == user.id)
        else:
            # 店长可以查看所有数据，但可以按日期和员工筛选
            if start_date:
                query = query.filter(Transaction.date >= parser.parse(start_date).date())
            if end_date:
                query = query.filter(Transaction.date <= parser.parse(end_date).date())
            if employee_id:
                query = query.filter(Transaction.employee_id == int(employee_id))
        
        # 分页
        pagination = query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        transactions = [t.to_dict() for t in pagination.items]
        
        return jsonify({
            'transactions': transactions,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """获取单条流水记录"""
    try:
        user = get_current_user()
        transaction = Transaction.query.get_or_404(transaction_id)
        
        # 权限检查：普通工人和前台员工只能查看自己的数据
        if user.role in ['staff', 'worker'] and transaction.employee_id != user.id:
            return jsonify({'error': '权限不足'}), 403
        
        return jsonify({'transaction': transaction.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """更新流水记录"""
    try:
        user = get_current_user()
        
        # 检查是否为示例账号
        demo_check = check_demo_account(user)
        if demo_check:
            return demo_check
        
        transaction = Transaction.query.get_or_404(transaction_id)
        
        # 权限检查：普通工人和前台员工只能修改自己的数据
        if user.role in ['staff', 'worker'] and transaction.employee_id != user.id:
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        
        if 'date' in data:
            transaction.date = parser.parse(data['date']).date()
        if 'employee_id' in data:
            if user.role in ['staff', 'worker'] and data['employee_id'] != user.id:
                return jsonify({'error': '您只能修改自己的数据'}), 403
            transaction.employee_id = data['employee_id']
        if 'quantity' in data:
            transaction.quantity = int(data['quantity'])
        if 'total_amount' in data:
            transaction.total_amount = float(data['total_amount'])
        if 'amount_details' in data:
            transaction.set_amount_details(data['amount_details'])
        
        transaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '流水记录更新成功',
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """删除流水记录"""
    try:
        user = get_current_user()
        
        # 检查是否为示例账号
        demo_check = check_demo_account(user)
        if demo_check:
            return demo_check
        
        if user.role != 'manager':
            return jsonify({'error': '权限不足'}), 403
        
        transaction = Transaction.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': '流水记录删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/daily', methods=['GET'])
@jwt_required()
def get_daily_report():
    """每日小结报表"""
    try:
        user = get_current_user()
        date_str = request.args.get('date', datetime.now().date().isoformat())
        
        try:
            target_date = parser.parse(date_str).date()
        except:
            return jsonify({'error': '日期格式错误'}), 400
        
        # 权限检查：普通工人和前台员工只能查看当日数据
        if user.role in ['staff', 'worker'] and target_date != datetime.now().date():
            return jsonify({'error': '您只能查看当日数据'}), 403
        
        # 查询数据
        query = Transaction.query.filter(Transaction.date == target_date)
        if user.role in ['staff', 'worker']:
            query = query.filter(Transaction.employee_id == user.id)
        
        transactions = query.all()
        
        # 统计
        stats = defaultdict(lambda: {'quantity': 0, 'total_amount': 0.0, 'transactions': []})
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            stats[emp_name]['quantity'] += t.quantity
            stats[emp_name]['total_amount'] += float(t.total_amount)
            stats[emp_name]['transactions'].append(t.to_dict())
        
        # 支付方式统计
        payment_stats = defaultdict(float)
        for t in transactions:
            details = t.get_amount_details()
            if details:
                # 解析金额明细：微信80, 支付宝100
                parts = details.split(',')
                for part in parts:
                    part = part.strip()
                    if '微信' in part or '支付宝' in part or '现金' in part:
                        try:
                            amount = float(''.join(filter(str.isdigit or str == '.', part)))
                            payment_type = '微信' if '微信' in part else ('支付宝' if '支付宝' in part else '现金')
                            payment_stats[payment_type] += amount
                        except:
                            pass
        
        result = {
            'date': target_date.isoformat(),
            'summary': {
                'total_quantity': sum(s['quantity'] for s in stats.values()),
                'total_amount': sum(s['total_amount'] for s in stats.values()),
                'employee_count': len(stats)
            },
            'by_employee': dict(stats),
            'payment_methods': dict(payment_stats)
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/weekly', methods=['GET'])
@jwt_required()
def get_weekly_report():
    """每周小结报表"""
    try:
        user = get_current_user()
        
        # 普通工人和前台员工不能查看周报
        if user.role in ['staff', 'worker']:
            return jsonify({'error': '权限不足'}), 403
        
        year = int(request.args.get('year', datetime.now().year))
        week = int(request.args.get('week', datetime.now().isocalendar()[1]))
        
        # 计算周的开始和结束日期
        # 使用ISO周计算
        jan1 = datetime(year, 1, 1)
        days_offset = (jan1.weekday() + 1) % 7  # 转换为ISO周（周一是0）
        first_monday = jan1 - timedelta(days=days_offset)
        if days_offset > 3:  # 如果1月1日是在周四之后，则第一周是下一周
            first_monday += timedelta(days=7)
        start_date = first_monday + timedelta(weeks=week-1)
        end_date = start_date + timedelta(days=6)
        
        # 查询数据
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # 统计
        stats = defaultdict(lambda: {'quantity': 0, 'total_amount': 0.0})
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            stats[emp_name]['quantity'] += t.quantity
            stats[emp_name]['total_amount'] += float(t.total_amount)
        
        result = {
            'year': year,
            'week': week,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'summary': {
                'total_quantity': sum(s['quantity'] for s in stats.values()),
                'total_amount': sum(s['total_amount'] for s in stats.values()),
                'employee_count': len(stats)
            },
            'by_employee': dict(stats)
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/monthly', methods=['GET'])
@jwt_required()
def get_monthly_report():
    """每月小结报表"""
    try:
        user = get_current_user()
        
        # 普通工人和前台员工不能查看月报
        if user.role in ['staff', 'worker']:
            return jsonify({'error': '权限不足'}), 403
        
        year = int(request.args.get('year', datetime.now().year))
        month = int(request.args.get('month', datetime.now().month))
        
        # 计算月的开始和结束日期
        start_date = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).date()
        
        # 查询数据
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # 统计
        stats = defaultdict(lambda: {'quantity': 0, 'total_amount': 0.0, 'daily_avg': 0.0})
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            stats[emp_name]['quantity'] += t.quantity
            stats[emp_name]['total_amount'] += float(t.total_amount)
        
        # 计算日均
        days_in_month = (end_date - start_date).days + 1
        for emp_name in stats:
            stats[emp_name]['daily_avg'] = stats[emp_name]['total_amount'] / days_in_month
        
        result = {
            'year': year,
            'month': month,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'summary': {
                'total_quantity': sum(s['quantity'] for s in stats.values()),
                'total_amount': sum(s['total_amount'] for s in stats.values()),
                'employee_count': len(stats),
                'days_in_month': days_in_month
            },
            'by_employee': dict(stats)
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/yearly', methods=['GET'])
@jwt_required()
def get_yearly_report():
    """年报"""
    try:
        user = get_current_user()
        
        # 普通工人和前台员工不能查看年报
        if user.role in ['staff', 'worker']:
            return jsonify({'error': '权限不足'}), 403
        
        year = int(request.args.get('year', datetime.now().year))
        
        # 查询数据
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # 统计
        stats = defaultdict(lambda: {
            'quantity': 0,
            'total_amount': 0.0,
            'monthly_stats': defaultdict(lambda: {'quantity': 0, 'total_amount': 0.0})
        })
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            stats[emp_name]['quantity'] += t.quantity
            stats[emp_name]['total_amount'] += float(t.total_amount)
            
            # 月度统计
            month = t.date.month
            stats[emp_name]['monthly_stats'][month]['quantity'] += t.quantity
            stats[emp_name]['monthly_stats'][month]['total_amount'] += float(t.total_amount)
        
        # 转换月度统计为字典
        for emp_name in stats:
            stats[emp_name]['monthly_stats'] = dict(stats[emp_name]['monthly_stats'])
        
        result = {
            'year': year,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'summary': {
                'total_quantity': sum(s['quantity'] for s in stats.values()),
                'total_amount': sum(s['total_amount'] for s in stats.values()),
                'employee_count': len(stats)
            },
            'by_employee': dict(stats)
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/management', methods=['GET'])
@jwt_required()
def get_management_report():
    """管理层综合报表（包含各项指标）"""
    try:
        user = get_current_user()
        
        if user.role != 'manager':
            return jsonify({'error': '权限不足'}), 403
        
        # 查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = parser.parse(start_date_str).date()
            end_date = parser.parse(end_date_str).date()
        else:
            # 默认查询最近30天
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        
        # 查询数据
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # 基础统计
        total_transactions = len(transactions)
        total_quantity = sum(t.quantity for t in transactions)
        total_amount = sum(float(t.total_amount) for t in transactions)
        
        # 按员工统计
        employee_stats = defaultdict(lambda: {
            'quantity': 0,
            'total_amount': 0.0,
            'transaction_count': 0,
            'avg_per_transaction': 0.0
        })
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            employee_stats[emp_name]['quantity'] += t.quantity
            employee_stats[emp_name]['total_amount'] += float(t.total_amount)
            employee_stats[emp_name]['transaction_count'] += 1
        
        # 计算平均单笔金额
        for emp_name in employee_stats:
            if employee_stats[emp_name]['transaction_count'] > 0:
                employee_stats[emp_name]['avg_per_transaction'] = \
                    employee_stats[emp_name]['total_amount'] / employee_stats[emp_name]['transaction_count']
        
        # 按日期统计
        daily_stats = defaultdict(lambda: {'quantity': 0, 'total_amount': 0.0, 'transaction_count': 0})
        for t in transactions:
            date_str = t.date.isoformat()
            daily_stats[date_str]['quantity'] += t.quantity
            daily_stats[date_str]['total_amount'] += float(t.total_amount)
            daily_stats[date_str]['transaction_count'] += 1
        
        # 支付方式统计
        payment_stats = defaultdict(float)
        for t in transactions:
            details = t.get_amount_details()
            if details:
                parts = details.split(',')
                for part in parts:
                    part = part.strip()
                    if '微信' in part or '支付宝' in part or '现金' in part:
                        try:
                            amount = float(''.join(filter(lambda x: x.isdigit() or x == '.', part)))
                            payment_type = '微信' if '微信' in part else ('支付宝' if '支付宝' in part else '现金')
                            payment_stats[payment_type] += amount
                        except:
                            pass
        
        # 计算增长率（与上一周期对比）
        prev_start = start_date - (end_date - start_date) - timedelta(days=1)
        prev_end = start_date - timedelta(days=1)
        
        prev_transactions = Transaction.query.filter(
            Transaction.date >= prev_start,
            Transaction.date <= prev_end
        ).all()
        
        prev_total_amount = sum(float(t.total_amount) for t in prev_transactions)
        growth_rate = 0.0
        if prev_total_amount > 0:
            growth_rate = ((total_amount - prev_total_amount) / prev_total_amount) * 100
        
        # 员工排名
        employee_ranking = sorted(
            employee_stats.items(),
            key=lambda x: x[1]['total_amount'],
            reverse=True
        )
        
        result = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days + 1
            },
            'summary': {
                'total_transactions': total_transactions,
                'total_quantity': total_quantity,
                'total_amount': total_amount,
                'avg_daily_amount': total_amount / max((end_date - start_date).days + 1, 1),
                'avg_per_transaction': total_amount / max(total_transactions, 1),
                'growth_rate': round(growth_rate, 2)
            },
            'by_employee': dict(employee_stats),
            'employee_ranking': [{'name': name, 'stats': stats} for name, stats in employee_ranking],
            'daily_stats': dict(daily_stats),
            'payment_methods': dict(payment_stats),
            'trends': {
                'highest_day': max(daily_stats.items(), key=lambda x: x[1]['total_amount'])[0] if daily_stats else None,
                'lowest_day': min(daily_stats.items(), key=lambda x: x[1]['total_amount'])[0] if daily_stats else None
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """获取员工列表"""
    try:
        user = get_current_user()
        
        employees = User.query.filter_by(is_active=True).all()
        
        return jsonify({
            'employees': [e.to_dict() for e in employees]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


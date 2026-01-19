"""
AI对话API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ai_workflow import get_ai_workflow
from models import User, Transaction, db
from datetime import datetime, timedelta
from dateutil import parser
import calendar

ai_bp = Blueprint('ai', __name__)

def execute_api_call(intent: str, parameters: dict, user_id: int):
    """根据意图执行实际的API调用"""
    user = User.query.get(user_id)
    
    # 检查是否为示例账号
    if user and user.is_demo:
        return {'success': False, 'message': '示例账号只能查看，不能进行写操作。请使用实际账号登录。'}
    
    if intent == 'create_transaction':
        # 创建流水记录
        if not all(k in parameters for k in ['date', 'employee_id', 'quantity', 'total_amount']):
            return {'success': False, 'message': '缺少必要参数：日期、员工、数量、总金额'}
        
        transaction = Transaction(
            date=parser.parse(parameters['date']).date(),
            employee_id=parameters['employee_id'],
            quantity=int(parameters['quantity']),
            total_amount=float(parameters['total_amount'])
        )
        transaction.set_amount_details(parameters.get('amount_details', ''))
        db.session.add(transaction)
        db.session.commit()
        return {'success': True, 'data': transaction.to_dict()}
    
    elif intent == 'query_transactions':
        query = Transaction.query
        if user.role in ['staff', 'worker']:
            query = query.filter(Transaction.employee_id == user.id)
            query = query.filter(Transaction.date == datetime.now().date())
        else:
            if 'start_date' in parameters:
                query = query.filter(Transaction.date >= parser.parse(parameters['start_date']).date())
            if 'end_date' in parameters:
                query = query.filter(Transaction.date <= parser.parse(parameters['end_date']).date())
            if 'employee_id' in parameters:
                query = query.filter(Transaction.employee_id == parameters['employee_id'])
        
        transactions = query.order_by(Transaction.date.desc()).limit(50).all()
        return {'success': True, 'data': [t.to_dict() for t in transactions]}
    
    elif intent == 'daily_report':
        if user.role in ['staff', 'worker'] and 'date' in parameters:
            date_obj = parser.parse(parameters['date']).date()
            if date_obj != datetime.now().date():
                return {'success': False, 'message': '您只能查看当日数据'}
        
        date_str = parameters.get('date', datetime.now().date().isoformat())
        query = Transaction.query.filter(Transaction.date == parser.parse(date_str).date())
        if user.role in ['staff', 'worker']:
            query = query.filter(Transaction.employee_id == user.id)
        
        transactions = query.all()
        stats = {}
        total_quantity = 0
        total_amount = 0.0
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            if emp_name not in stats:
                stats[emp_name] = {'quantity': 0, 'total_amount': 0.0}
            stats[emp_name]['quantity'] += t.quantity
            stats[emp_name]['total_amount'] += float(t.total_amount)
            total_quantity += t.quantity
            total_amount += float(t.total_amount)
        
        return {
            'success': True,
            'data': {
                'date': date_str,
                'total_quantity': total_quantity,
                'total_amount': total_amount,
                'by_employee': stats
            }
        }
    
    elif intent == 'weekly_report':
        if user.role in ['staff', 'worker']:
            return {'success': False, 'message': '权限不足'}
        year = int(parameters.get('year', datetime.now().year))
        week = int(parameters.get('week', datetime.now().isocalendar()[1]))
        
        # 计算周的开始和结束日期
        jan1 = datetime(year, 1, 1)
        days_offset = (jan1.weekday() + 1) % 7
        first_monday = jan1 - timedelta(days=days_offset)
        if days_offset > 3:
            first_monday += timedelta(days=7)
        start_date = first_monday + timedelta(weeks=week-1)
        end_date = start_date + timedelta(days=6)
        
        transactions = Transaction.query.filter(
            Transaction.date >= start_date.date(),
            Transaction.date <= end_date.date()
        ).all()
        
        stats = {}
        total_quantity = 0
        total_amount = 0.0
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            if emp_name not in stats:
                stats[emp_name] = {'quantity': 0, 'total_amount': 0.0}
            stats[emp_name]['quantity'] += t.quantity
            stats[emp_name]['total_amount'] += float(t.total_amount)
            total_quantity += t.quantity
            total_amount += float(t.total_amount)
        
        return {
            'success': True,
            'data': {
                'year': year,
                'week': week,
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'total_quantity': total_quantity,
                'total_amount': total_amount,
                'by_employee': stats
            }
        }
    
    elif intent == 'monthly_report':
        if user.role in ['staff', 'worker']:
            return {'success': False, 'message': '权限不足'}
        year = int(parameters.get('year', datetime.now().year))
        month = int(parameters.get('month', datetime.now().month))
        
        start_date = datetime(year, month, 1).date()
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).date()
        
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        stats = {}
        total_quantity = 0
        total_amount = 0.0
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            if emp_name not in stats:
                stats[emp_name] = {'quantity': 0, 'total_amount': 0.0}
            stats[emp_name]['quantity'] += t.quantity
            stats[emp_name]['total_amount'] += float(t.total_amount)
            total_quantity += t.quantity
            total_amount += float(t.total_amount)
        
        days_in_month = (end_date - start_date).days + 1
        
        return {
            'success': True,
            'data': {
                'year': year,
                'month': month,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_quantity': total_quantity,
                'total_amount': total_amount,
                'days_in_month': days_in_month,
                'by_employee': stats
            }
        }
    
    elif intent == 'yearly_report':
        if user.role in ['staff', 'worker']:
            return {'success': False, 'message': '权限不足'}
        year = int(parameters.get('year', datetime.now().year))
        
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        stats = {}
        total_quantity = 0
        total_amount = 0.0
        
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            if emp_name not in stats:
                stats[emp_name] = {'quantity': 0, 'total_amount': 0.0}
            stats[emp_name]['quantity'] += t.quantity
            stats[emp_name]['total_amount'] += float(t.total_amount)
            total_quantity += t.quantity
            total_amount += float(t.total_amount)
        
        return {
            'success': True,
            'data': {
                'year': year,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_quantity': total_quantity,
                'total_amount': total_amount,
                'by_employee': stats
            }
        }
    
    elif intent == 'management_report':
        if user.role != 'manager':
            return {'success': False, 'message': '权限不足'}
        
        from datetime import timedelta
        start_date_str = parameters.get('start_date')
        end_date_str = parameters.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = parser.parse(start_date_str).date()
            end_date = parser.parse(end_date_str).date()
        else:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        total_transactions = len(transactions)
        total_quantity = sum(t.quantity for t in transactions)
        total_amount = sum(float(t.total_amount) for t in transactions)
        
        employee_stats = {}
        for t in transactions:
            emp_name = t.employee.real_name if t.employee else '未知'
            if emp_name not in employee_stats:
                employee_stats[emp_name] = {
                    'quantity': 0,
                    'total_amount': 0.0,
                    'transaction_count': 0
                }
            employee_stats[emp_name]['quantity'] += t.quantity
            employee_stats[emp_name]['total_amount'] += float(t.total_amount)
            employee_stats[emp_name]['transaction_count'] += 1
        
        for emp_name in employee_stats:
            if employee_stats[emp_name]['transaction_count'] > 0:
                employee_stats[emp_name]['avg_per_transaction'] = \
                    employee_stats[emp_name]['total_amount'] / employee_stats[emp_name]['transaction_count']
        
        days = (end_date - start_date).days + 1
        
        return {
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'summary': {
                    'total_transactions': total_transactions,
                    'total_quantity': total_quantity,
                    'total_amount': total_amount,
                    'avg_daily_amount': total_amount / days if days > 0 else 0,
                    'avg_per_transaction': total_amount / total_transactions if total_transactions > 0 else 0
                },
                'by_employee': employee_stats
            }
        }
    
    elif intent == 'employee_list':
        employees = User.query.filter_by(is_active=True).all()
        return {'success': True, 'data': [e.to_dict() for e in employees]}
    
    return {'success': False, 'message': '未知的意图类型'}

@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """AI对话接口"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_input = data.get('message', '')
        history = data.get('history', [])
        
        if not user_input:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 获取AI工作流
        workflow = get_ai_workflow()
        
        if not workflow:
            return jsonify({
                'error': 'AI工作流未初始化，请检查AI API配置',
                'response': '抱歉，AI功能暂时不可用。请检查API配置或联系管理员。'
            }), 500
        
        # 处理用户输入（传入用户角色和ID用于权限检查）
        result = workflow.process(
            user_input, 
            history,
            user_role=user.role,
            user_id=user.id
        )
        
        # 检查是否被安全防护拦截
        if result.get('intent') == 'security_blocked':
            return jsonify({
                'response': result.get('error', '操作被安全系统拦截'),
                'messages': result.get('messages', []),
                'intent': 'security_blocked',
                'api_result': None
            }), 403
        
        # 如果识别到具体意图，尝试执行实际功能
        intent = result.get('intent', 'unknown')
        if intent != 'unknown' and intent != 'chat' and intent != 'security_blocked':
            parameters = result.get('parameters', {})
            
            # 强制权限检查：普通工人和前台员工只能操作自己的数据
            if user.role in ['staff', 'worker']:
                parameters['employee_id'] = user.id
                # 限制日期为今天
                if 'date' not in parameters:
                    from datetime import datetime
                    parameters['date'] = datetime.now().date().isoformat()
            
            # 执行API调用
            api_result = execute_api_call(intent, parameters, user_id)
            if api_result.get('success'):
                # 将API结果整合到响应中
                result['api_result'] = api_result
            else:
                # API调用失败，返回错误信息
                result['response'] = api_result.get('message', '操作失败')
        
        return jsonify({
            'response': result.get('response', ''),
            'messages': result.get('messages', []),
            'intent': intent,
            'api_result': result.get('api_result')
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500


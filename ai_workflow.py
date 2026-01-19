"""
AI工作流模块
集成LangChain和LangGraph，支持Deep Seek和Qianwen API
包含安全防护：SQL注入防护、权限绕过防护、话术注入防护

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
import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    # 如果LangGraph未安装，使用简化版本
    class StateGraph:
        def __init__(self, state_type):
            self.nodes = {}
            self.edges = []
            self.entry_point = None
        
        def add_node(self, name, func):
            self.nodes[name] = func
        
        def set_entry_point(self, name):
            self.entry_point = name
        
        def add_edge(self, from_node, to_node):
            self.edges.append((from_node, to_node))
        
        def compile(self):
            return CompiledGraph(self.nodes, self.edges, self.entry_point)
    
    class END:
        pass
    
    class CompiledGraph:
        def __init__(self, nodes, edges, entry_point):
            self.nodes = nodes
            self.edges = edges
            self.entry_point = entry_point
        
        def invoke(self, state):
            current_node = self.entry_point
            while current_node and current_node != END:
                if current_node in self.nodes:
                    state = self.nodes[current_node](state)
                    # 查找下一个节点
                    next_node = None
                    for from_node, to_node in self.edges:
                        if from_node == current_node:
                            next_node = to_node
                            break
                    current_node = next_node
                else:
                    break
            return state
from config import Config
from openai import OpenAI

class AIWorkflowState:
    """AI工作流状态"""
    def __init__(self):
        self.messages = []
        self.intent = None
        self.parameters = {}
        self.result = None

class DeepSeekAPI:
    """Deep Seek API客户端"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        self.api_base = api_base or Config.DEEPSEEK_API_BASE
        self.model = "deepseek-chat"
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )
            except Exception as e:
                print(f"Deep Seek API客户端初始化失败: {e}")
                self.client = None
    
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """调用Deep Seek API"""
        if not self.api_key:
            return "Deep Seek API密钥未配置"
        
        if not self.client:
            return "Deep Seek API客户端初始化失败"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Deep Seek API调用失败: {str(e)}"

class QianwenAPI:
    """通义千问API客户端（使用OpenAI兼容模式）"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        self.api_key = api_key or Config.QIANWEN_API_KEY
        self.api_base = api_base or Config.QIANWEN_API_BASE
        self.model = "qwen3-omni-flash"  # 使用用户指定的模型
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )
            except Exception as e:
                print(f"通义千问API客户端初始化失败: {e}")
                self.client = None
    
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """调用通义千问API（使用OpenAI兼容模式）"""
        if not self.api_key:
            return "通义千问API密钥未配置"
        
        if not self.client:
            return "通义千问API客户端初始化失败"
        
        try:
            # 使用OpenAI兼容模式调用
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"通义千问API调用失败: {str(e)}"

class FlowMasterAIWorkflow:
    """FlowMaster AI工作流"""
    
    def __init__(self):
        self.deepseek = DeepSeekAPI()
        self.qianwen = QianwenAPI()
        self.workflow = None
        self._build_workflow()
    
    def _build_workflow(self):
        """构建工作流图"""
        workflow = StateGraph(dict)
        
        # 添加节点
        workflow.add_node("intent_classifier", self._classify_intent)
        workflow.add_node("parameter_extractor", self._extract_parameters)
        workflow.add_node("function_executor", self._execute_function)
        workflow.add_node("response_generator", self._generate_response)
        
        # 设置入口
        workflow.set_entry_point("intent_classifier")
        
        # 添加边
        workflow.add_edge("intent_classifier", "parameter_extractor")
        workflow.add_edge("parameter_extractor", "function_executor")
        workflow.add_edge("function_executor", "response_generator")
        workflow.add_edge("response_generator", END)
        
        self.workflow = workflow.compile()
    
    def _sanitize_input(self, text: str) -> str:
        """输入清理和验证，防止SQL注入和话术注入"""
        if not text:
            return ""
        
        # 移除潜在的SQL注入关键词（记录但不直接拒绝，由后续验证处理）
        # 移除HTML/JavaScript标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 限制长度
        if len(text) > 1000:
            text = text[:1000]
        
        return text.strip()
    
    def _check_permission_bypass(self, message: str, user_role: str = None) -> Tuple[bool, str]:
        """检查权限绕过尝试"""
        if not user_role:
            return True, ""
        
        # 检测试图提升权限的话术
        bypass_patterns = [
            r'以.*?身份|作为.*?管理员|使用.*?权限|提升.*?权限|切换.*?角色',
            r'manager|admin|管理员|店长',
            r'绕过|跳过|忽略.*?检查|权限.*?提升'
        ]
        
        message_lower = message.lower()
        for pattern in bypass_patterns:
            if re.search(pattern, message_lower):
                return False, "检测到可疑的权限绕过尝试，操作已被拒绝。"
        
        # 检查是否试图访问受限功能
        restricted_keywords = {
            'worker': ['周报', '月报', '年报', '管理报表', '员工管理', '删除', '修改他人'],
            'staff': ['周报', '月报', '年报', '管理报表', '员工管理', '删除', '修改他人']
        }
        
        if user_role in restricted_keywords:
            for keyword in restricted_keywords[user_role]:
                if keyword in message:
                    return False, f"您的角色({user_role})无权访问此功能。"
        
        return True, ""
    
    def _classify_intent(self, state: Dict) -> Dict:
        """意图分类（带安全验证）"""
        messages = state.get('messages', [])
        user_role = state.get('user_role', None)
        
        if not messages:
            return {'intent': 'unknown', 'messages': messages}
        
        last_message = messages[-1]['content'] if messages else ""
        
        # 输入清理
        last_message = self._sanitize_input(last_message)
        
        # 权限绕过检查
        if user_role:
            allowed, error_msg = self._check_permission_bypass(last_message, user_role)
            if not allowed:
                return {
                    'intent': 'security_blocked',
                    'messages': messages,
                    'error': error_msg
                }
        
        # 简单的意图分类规则（可以改进为使用AI）
        intent = 'unknown'
        
        if any(keyword in last_message for keyword in ['录入', '添加', '创建', '新增']):
            intent = 'create_transaction'
        elif any(keyword in last_message for keyword in ['查询', '查看', '显示', '列表']):
            intent = 'query_transactions'
        elif any(keyword in last_message for keyword in ['日报', '每日', '今天']):
            intent = 'daily_report'
        elif any(keyword in last_message for keyword in ['周报', '每周', '本周']):
            intent = 'weekly_report'
        elif any(keyword in last_message for keyword in ['月报', '每月', '本月']):
            intent = 'monthly_report'
        elif any(keyword in last_message for keyword in ['年报', '每年', '今年']):
            intent = 'yearly_report'
        elif any(keyword in last_message for keyword in ['管理', '综合', '指标']):
            intent = 'management_report'
        elif any(keyword in last_message for keyword in ['员工', '人员']):
            intent = 'employee_list'
        else:
            intent = 'chat'
        
        return {'intent': intent, 'messages': messages}
    
    def _validate_parameter(self, param_name: str, param_value: Any) -> Tuple[bool, Any]:
        """参数验证和清理，防止注入攻击"""
        if param_value is None:
            return True, None
        
        # 字符串参数验证
        if isinstance(param_value, str):
            # 移除SQL注入字符
            dangerous_chars = ["'", '"', ';', '--', '/*', '*/', '<', '>', '&', '|']
            for char in dangerous_chars:
                if char in param_value:
                    param_value = param_value.replace(char, '')
            
            # 限制长度
            if len(param_value) > 200:
                param_value = param_value[:200]
        
        # 数字参数验证
        if param_name in ['quantity', 'employee_id', 'total_amount']:
            try:
                if param_name == 'employee_id':
                    param_value = int(param_value)
                    if param_value < 1:
                        return False, None
                elif param_name == 'quantity':
                    param_value = int(float(param_value))
                    if param_value < 0 or param_value > 1000000:
                        return False, None
                elif param_name == 'total_amount':
                    param_value = float(param_value)
                    if param_value < 0 or param_value > 100000000:
                        return False, None
            except (ValueError, TypeError):
                return False, None
        
        # 日期参数验证
        if param_name == 'date':
            if not isinstance(param_value, str):
                return False, None
            # 验证日期格式
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, param_value):
                return False, None
        
        return True, param_value
    
    def _extract_parameters(self, state: Dict) -> Dict:
        """参数提取（带安全验证）"""
        intent = state.get('intent', 'unknown')
        messages = state.get('messages', [])
        user_role = state.get('user_role', None)
        user_id = state.get('user_id', None)
        parameters = {}
        
        if not messages:
            return {'parameters': parameters, 'intent': intent, 'messages': messages}
        
        last_message = messages[-1]['content'] if messages else ""
        
        # 提取日期
        date_pattern = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})|(\d{1,2}[-/]\d{1,2})|(今天|今日|昨天|昨日|明天|明日)'
        date_match = re.search(date_pattern, last_message)
        if date_match:
            date_str = date_match.group(0)
            if date_str in ['今天', '今日']:
                from datetime import datetime
                date_str = datetime.now().date().isoformat()
            elif date_str in ['昨天', '昨日']:
                from datetime import datetime, timedelta
                date_str = (datetime.now() - timedelta(days=1)).date().isoformat()
            valid, cleaned_date = self._validate_parameter('date', date_str)
            if valid:
                parameters['date'] = cleaned_date
        
        # 提取数字（数量、金额）
        numbers = re.findall(r'\d+\.?\d*', last_message)
        if numbers:
            if '数量' in last_message or 'quantity' in last_message.lower():
                valid, cleaned_qty = self._validate_parameter('quantity', numbers[0])
                if valid:
                    parameters['quantity'] = cleaned_qty
            if '金额' in last_message or 'amount' in last_message.lower() or 'total_amount' in last_message.lower():
                valid, cleaned_amt = self._validate_parameter('total_amount', numbers[0])
                if valid:
                    parameters['total_amount'] = cleaned_amt
        
        # 提取员工姓名（仅限管理员）
        if user_role == 'manager':
            employee_pattern = r'员工[：:]\s*(\S+)|(\S+)\s*的'
            employee_match = re.search(employee_pattern, last_message)
            if employee_match:
                emp_name = employee_match.group(1) or employee_match.group(2)
                valid, cleaned_name = self._validate_parameter('employee_name', emp_name)
                if valid:
                    parameters['employee'] = cleaned_name
        else:
            # 普通工人和前台员工只能操作自己的数据
            if user_id:
                parameters['employee_id'] = user_id
        
        return {'parameters': parameters, 'intent': intent, 'messages': messages}
    
    def _execute_function(self, state: Dict) -> Dict:
        """执行功能"""
        intent = state.get('intent', 'unknown')
        parameters = state.get('parameters', {})
        messages = state.get('messages', [])
        
        # 这里应该调用实际的API，但为了演示，我们返回模拟结果
        result = {
            'success': True,
            'data': None,
            'message': ''
        }
        
        if intent == 'create_transaction':
            result['message'] = '已为您创建流水记录'
            result['data'] = {'id': 1, 'date': parameters.get('date', '2025-01-01')}
        elif intent in ['query_transactions', 'daily_report', 'weekly_report', 'monthly_report', 'yearly_report', 'management_report']:
            result['message'] = f'已为您查询{intent}数据'
            result['data'] = {'count': 10, 'total_amount': 10000}
        elif intent == 'employee_list':
            result['message'] = '已为您查询员工列表'
            result['data'] = {'employees': ['张三', '李四']}
        else:
            result['message'] = '我理解您的需求，但需要更多信息'
        
        return {'result': result, 'intent': intent, 'parameters': parameters, 'messages': messages}
    
    def _generate_response(self, state: Dict) -> Dict:
        """生成响应"""
        intent = state.get('intent', 'unknown')
        result = state.get('result', {})
        messages = state.get('messages', [])
        
        # 使用AI生成自然语言响应
        system_prompt = """你是一个友好的AI助手，帮助用户管理每日流水数据。
你可以帮助用户：
1. 录入流水记录
2. 查询流水数据
3. 生成各类报表（日报、周报、月报、年报）
4. 查看员工信息

请用自然、友好的语言回复用户。"""
        
        user_message = messages[-1]['content'] if messages else ""
        ai_response = result.get('message', '')
        
        # 构建消息
        chat_messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        
        # 优先使用Deep Seek，如果失败则使用通义千问
        response_text = self.deepseek.chat(chat_messages)
        if "API调用失败" in response_text or "未配置" in response_text:
            response_text = self.qianwen.chat(chat_messages)
        
        # 如果两个都失败，使用默认响应
        if "API调用失败" in response_text or "未配置" in response_text:
            response_text = f"{ai_response}\n\n如需更多帮助，请告诉我具体需求。"
        
        # 添加AI响应到消息历史
        new_messages = messages + [{'role': 'assistant', 'content': response_text}]
        
        return {'messages': new_messages, 'response': response_text}
    
    def process(self, user_input: str, history: List[Dict] = None, user_role: str = None, user_id: int = None) -> Dict:
        """处理用户输入（带安全参数）"""
        if history is None:
            history = []
        
        # 添加用户消息
        messages = history + [{'role': 'user', 'content': user_input}]
        
        # 运行工作流（传入用户角色和ID用于权限检查）
        initial_state = {
            'messages': messages,
            'user_role': user_role,
            'user_id': user_id
        }
        final_state = self.workflow.invoke(initial_state)
        
        # 提取参数（如果存在）
        parameters = final_state.get('parameters', {})
        
        return {
            'response': final_state.get('response', ''),
            'messages': final_state.get('messages', messages),
            'intent': final_state.get('intent', 'unknown'),
            'parameters': parameters,
            'result': final_state.get('result', {}),
            'error': final_state.get('error')
        }

# 全局工作流实例
_workflow_instance = None

def init_ai_workflow():
    """初始化AI工作流"""
    global _workflow_instance
    if _workflow_instance is None:
        try:
            _workflow_instance = FlowMasterAIWorkflow()
        except Exception as e:
            print(f"AI工作流初始化失败: {e}")
            print("AI功能将不可用，但系统其他功能仍可正常使用")
            _workflow_instance = None
    return _workflow_instance

def get_ai_workflow() -> FlowMasterAIWorkflow:
    """获取AI工作流实例"""
    global _workflow_instance
    if _workflow_instance is None:
        try:
            _workflow_instance = FlowMasterAIWorkflow()
        except Exception as e:
            print(f"AI工作流初始化失败: {e}")
            return None
    return _workflow_instance


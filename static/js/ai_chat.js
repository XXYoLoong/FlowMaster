// FlowMaster AI - AI对话UI JavaScript
const API_BASE = '/api';
let currentUser = null;
let chatHistory = [];

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    initEventListeners();
});

// 检查认证状态
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (token) {
        fetchCurrentUser();
    } else {
        showLogin();
    }
}

// 获取当前用户
async function fetchCurrentUser() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            showChat();
            updateQuickActions();
        } else {
            localStorage.removeItem('access_token');
            showLogin();
        }
    } catch (error) {
        console.error('获取用户信息失败:', error);
        showLogin();
    }
}

// 显示登录界面
function showLogin() {
    document.getElementById('aiLoginSection').style.display = 'flex';
    document.getElementById('aiChatSection').style.display = 'none';
    document.getElementById('aiLogoutBtn').style.display = 'none';
    document.getElementById('aiUserInfo').textContent = '未登录';
}

// 显示对话界面
function showChat() {
    document.getElementById('aiLoginSection').style.display = 'none';
    document.getElementById('aiChatSection').style.display = 'flex';
    document.getElementById('aiLogoutBtn').style.display = 'block';
    const roleText = currentUser ? (currentUser.role === 'manager' ? '店长' : 
                                    currentUser.role === 'staff' ? '前台员工' : '普通工人') : '未登录';
    document.getElementById('aiUserInfo').textContent = currentUser ? `${currentUser.real_name} (${roleText})` : '未登录';
}

// 更新快捷操作按钮
function updateQuickActions() {
    if (currentUser && currentUser.role === 'manager') {
        document.getElementById('quickWeeklyReport').style.display = 'inline-block';
        document.getElementById('quickMonthlyReport').style.display = 'inline-block';
        document.getElementById('quickManagementReport').style.display = 'inline-block';
    } else {
        document.getElementById('quickWeeklyReport').style.display = 'none';
        document.getElementById('quickMonthlyReport').style.display = 'none';
        document.getElementById('quickManagementReport').style.display = 'none';
    }
}

// 显示注册表单
function showRegisterForm() {
    document.getElementById('aiLoginFormContainer').style.display = 'none';
    document.getElementById('aiRegisterFormContainer').style.display = 'block';
}

// 显示登录表单
function showLoginForm() {
    document.getElementById('aiRegisterFormContainer').style.display = 'none';
    document.getElementById('aiLoginFormContainer').style.display = 'block';
}

// 初始化事件监听器
function initEventListeners() {
    // 登录表单
    document.getElementById('aiLoginForm').addEventListener('submit', handleLogin);
    
    // 注册表单
    document.getElementById('aiRegisterForm').addEventListener('submit', handleRegister);
    
    // 切换登录/注册界面
    document.getElementById('aiShowRegisterBtn').addEventListener('click', showRegisterForm);
    document.getElementById('aiShowLoginBtn').addEventListener('click', showLoginForm);
    
    // 退出登录
    document.getElementById('aiLogoutBtn').addEventListener('click', handleLogout);
    
    // 切换到原版界面
    document.getElementById('switchToMain').addEventListener('click', () => {
        window.location.href = '/';
    });
    
    // 发送消息
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    
    // 输入框回车发送
    const chatInput = document.getElementById('chatInput');
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 自动调整输入框高度
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    
    // 快捷操作按钮
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            chatInput.value = action;
            sendMessage();
        });
    });
}

// 处理注册
async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('aiRegUsername').value.trim();
    const password = document.getElementById('aiRegPassword').value;
    const realName = document.getElementById('aiRegRealName').value.trim();
    
    // 客户端验证
    if (username.length < 3 || username.length > 20) {
        alert('用户名长度必须在3-20个字符之间');
        return;
    }
    
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
        alert('用户名只能包含字母、数字、下划线和连字符');
        return;
    }
    
    if (password.length < 6) {
        alert('密码长度至少6个字符');
        return;
    }
    
    if (realName.length < 2 || realName.length > 50) {
        alert('真实姓名长度必须在2-50个字符之间');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password, real_name: realName })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message || '注册成功！请登录');
            // 清空表单
            document.getElementById('aiRegisterForm').reset();
            // 切换到登录界面
            showLoginForm();
        } else {
            alert(data.error || '注册失败');
        }
    } catch (error) {
        console.error('注册错误:', error);
        alert('网络错误，请稍后重试');
    }
}

// 登录处理
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('aiUsername').value;
    const password = document.getElementById('aiPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            currentUser = data.user;
            showChat();
            updateQuickActions();
            addSystemMessage('登录成功！我是您的AI助手，可以直接告诉我您的需求。');
        } else {
            alert(data.error || '登录失败');
        }
    } catch (error) {
        console.error('登录错误:', error);
        alert('网络错误，请稍后重试');
    }
}

// 退出登录
function handleLogout() {
    localStorage.removeItem('access_token');
    currentUser = null;
    chatHistory = [];
    showLogin();
    clearMessages();
}

// 发送消息
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 检查是否为示例账号（如果是写操作相关）
    if (currentUser && currentUser.is_demo) {
        const writeKeywords = ['录入', '添加', '创建', '新增', '删除', '修改', '更新'];
        if (writeKeywords.some(keyword => message.includes(keyword))) {
            addAIMessage('抱歉，示例账号只能查看，不能进行数据操作。请使用实际账号登录。', null);
            input.value = '';
            return;
        }
    }
    
    // 清空输入框
    input.value = '';
    input.style.height = 'auto';
    
    // 添加用户消息
    addUserMessage(message);
    
    // 显示加载动画
    const loadingId = addLoadingMessage();
    
    try {
        // 调用AI API
        const response = await fetch(`${API_BASE}/ai/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            })
        });
        
        // 移除加载动画
        removeLoadingMessage(loadingId);
        
        if (response.ok) {
            const data = await response.json();
            
            // 更新历史记录
            chatHistory = data.messages || [];
            
            // 添加AI回复
            addAIMessage(data.response, data.api_result);
        } else {
            const errorData = await response.json();
            addAIMessage(`抱歉，发生了错误：${errorData.error || '未知错误'}`, null);
        }
    } catch (error) {
        console.error('发送消息错误:', error);
        removeLoadingMessage(loadingId);
        addAIMessage('网络错误，请稍后重试', null);
    }
}

// 添加用户消息
function addUserMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    
    // 移除欢迎消息
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-item message-user';
    messageDiv.innerHTML = `
        <div class="message-bubble">
            <div class="message-content">${escapeHtml(message)}</div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// 添加AI消息
function addAIMessage(message, apiResult = null) {
    const messagesContainer = document.getElementById('chatMessages');
    
    // 移除欢迎消息
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-item message-ai';
    
    let content = `<div class="message-content">${formatMessage(message)}</div>`;
    
    // 如果有API结果，显示数据
    if (apiResult && apiResult.success && apiResult.data) {
        content += renderAPIResult(apiResult);
    }
    
    content += `<div class="message-time">${getCurrentTime()}</div>`;
    
    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${content}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// 添加系统消息
function addSystemMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    
    // 移除欢迎消息
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-item message-ai';
    messageDiv.innerHTML = `
        <div class="message-bubble">
            <div class="message-content">${escapeHtml(message)}</div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// 添加加载动画
function addLoadingMessage() {
    const messagesContainer = document.getElementById('chatMessages');
    
    // 移除欢迎消息
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const loadingId = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = loadingId;
    messageDiv.className = 'message-item message-ai';
    messageDiv.innerHTML = `
        <div class="message-bubble">
            <div class="message-loading">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return loadingId;
}

// 移除加载动画
function removeLoadingMessage(loadingId) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
}

// 渲染API结果
function renderAPIResult(apiResult) {
    if (!apiResult.data) return '';
    
    let html = '<div class="report-display" style="margin-top: 1rem;">';
    
    // 如果是交易数据
    if (Array.isArray(apiResult.data)) {
        if (apiResult.data.length > 0 && apiResult.data[0].date) {
            html += '<h4>查询结果</h4>';
            html += '<table class="data-table" style="width: 100%; font-size: 0.9rem;"><thead><tr><th>日期</th><th>员工</th><th>数量</th><th>总金额</th></tr></thead><tbody>';
            apiResult.data.slice(0, 10).forEach(item => {
                html += `<tr>
                    <td>${item.date}</td>
                    <td>${item.employee_name || '未知'}</td>
                    <td>${item.quantity}</td>
                    <td>¥${item.total_amount.toFixed(2)}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            if (apiResult.data.length > 10) {
                html += `<p style="margin-top: 0.5rem; color: var(--text-secondary);">共 ${apiResult.data.length} 条记录，仅显示前10条</p>`;
            }
        } else if (apiResult.data.length > 0 && apiResult.data[0].username) {
            html += '<h4>员工列表</h4><ul>';
            apiResult.data.forEach(emp => {
                html += `<li>${emp.real_name} (${emp.role === 'manager' ? '店长' : '前台员工'})</li>`;
            });
            html += '</ul>';
        }
    } else if (typeof apiResult.data === 'object') {
        // 如果是报表数据
        html += '<h4>报表数据</h4>';
        if (apiResult.data.total_amount !== undefined) {
            html += `<p>总金额：¥${apiResult.data.total_amount.toFixed(2)}</p>`;
        }
        if (apiResult.data.total_quantity !== undefined) {
            html += `<p>总数量：${apiResult.data.total_quantity}</p>`;
        }
    }
    
    html += '</div>';
    return html;
}

// 格式化消息（支持Markdown）
function formatMessage(message) {
    // 简单的Markdown支持
    message = escapeHtml(message);
    
    // 加粗
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 换行
    message = message.replace(/\n/g, '<br>');
    
    // 数字高亮
    message = message.replace(/(¥?\d+\.?\d*)/g, '<span style="color: var(--primary-color); font-weight: 600;">$1</span>');
    
    return message;
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 获取当前时间
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

// 滚动到底部
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 清空消息
function clearMessages() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">🤖</div>
            <h3>欢迎使用 FlowMaster AI</h3>
            <p>我是您的智能助手，可以帮助您：</p>
            <ul>
                <li>录入流水数据</li>
                <li>查询流水记录</li>
                <li>生成各类报表</li>
                <li>查看员工信息</li>
            </ul>
            <p>请直接告诉我您的需求，例如：</p>
            <ul>
                <li>"录入今天的流水：张三，数量6，总金额560"</li>
                <li>"查询今天的流水数据"</li>
                <li>"显示今天的日报"</li>
            </ul>
        </div>
    `;
    chatHistory = [];
}


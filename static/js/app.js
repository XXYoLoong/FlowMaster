// FlowMaster AI - 原版UI JavaScript
const API_BASE = '/api';
let currentUser = null;
let currentPage = 1;
let totalPages = 1;

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
            showMain();
            loadInitialData();
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
    document.getElementById('loginSection').style.display = 'block';
    document.getElementById('mainSection').style.display = 'none';
    document.getElementById('logoutBtn').style.display = 'none';
    document.getElementById('userInfo').textContent = '未登录';
}

// 显示主界面
function showMain() {
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    document.getElementById('logoutBtn').style.display = 'block';
    
    // 显示用户信息和角色
    if (currentUser) {
        const roleText = currentUser.role === 'manager' ? '店长' : 
                         currentUser.role === 'staff' ? '前台员工' : '普通工人';
        const demoText = currentUser.is_demo ? ' (示例账号-只读)' : '';
        document.getElementById('userInfo').textContent = `${currentUser.real_name} (${roleText})${demoText}`;
        
        // 如果是示例账号，显示提示
        if (currentUser.is_demo) {
            showMessage('您当前使用的是示例账号，只能查看，不能进行数据操作', 'warning');
        }
    } else {
        document.getElementById('userInfo').textContent = '未登录';
    }
    
    // 根据角色显示/隐藏功能
    const isManager = currentUser && currentUser.role === 'manager';
    const isStaff = currentUser && currentUser.role === 'staff';
    const isWorker = currentUser && currentUser.role === 'worker';
    const isManagement = isManager || isStaff; // 店长和前台员工
    
    // 店长专属功能
    if (isManager) {
        document.getElementById('employeesTab').style.display = 'block';
        document.getElementById('weeklyReportBtn').style.display = 'inline-block';
        document.getElementById('monthlyReportBtn').style.display = 'inline-block';
        document.getElementById('yearlyReportBtn').style.display = 'inline-block';
        document.getElementById('managementReportBtn').style.display = 'inline-block';
        document.getElementById('actionHeader').style.display = 'table-cell';
    } else {
        document.getElementById('employeesTab').style.display = 'none';
        document.getElementById('weeklyReportBtn').style.display = 'none';
        document.getElementById('monthlyReportBtn').style.display = 'none';
        document.getElementById('yearlyReportBtn').style.display = 'none';
        document.getElementById('managementReportBtn').style.display = 'none';
        document.getElementById('actionHeader').style.display = 'none';
    }
    
    // 店长和前台员工可以查看所有员工数据，普通工人只能看自己的
    if (isManagement) {
        // 显示员工选择器和提示
        const employeeFormGroup = document.getElementById('employeeFormGroup');
        if (employeeFormGroup) {
            employeeFormGroup.style.display = 'block';
        }
        const employeeHint = document.getElementById('employeeHint');
        if (employeeHint) {
            employeeHint.textContent = '（可选择任意员工）';
        }
        const dateHint = document.getElementById('dateHint');
        if (dateHint) {
            dateHint.textContent = '（可选择任意日期）';
        }
        // 显示快捷录入提示
        const quickInputHint = document.getElementById('quickInputHint');
        if (quickInputHint) {
            quickInputHint.style.display = 'block';
        }
        const roleHintText = document.getElementById('roleHintText');
        if (roleHintText) {
            roleHintText.textContent = isManager ? '店长' : '前台员工';
        }
        // 显示日期选择器（可以选择任意日期）
        const dateInput = document.getElementById('transactionDate');
        if (dateInput) {
            dateInput.removeAttribute('readonly');
            dateInput.style.pointerEvents = 'auto';
            if (!dateInput.value) {
                dateInput.value = new Date().toISOString().split('T')[0];
            }
        }
    } else if (isWorker) {
        // 隐藏员工选择器（普通工人只能录入自己的数据）
        const employeeFormGroup = document.getElementById('employeeFormGroup');
        if (employeeFormGroup) {
            employeeFormGroup.style.display = 'none';
        }
        // 隐藏快捷录入提示
        const quickInputHint = document.getElementById('quickInputHint');
        if (quickInputHint) {
            quickInputHint.style.display = 'none';
        }
        const dateHint = document.getElementById('dateHint');
        if (dateHint) {
            dateHint.textContent = '（仅限今日）';
        }
        // 日期固定为今天
        const dateInput = document.getElementById('transactionDate');
        if (dateInput) {
            dateInput.value = new Date().toISOString().split('T')[0];
            dateInput.setAttribute('readonly', 'readonly');
            dateInput.style.pointerEvents = 'none';
        }
    }
    
    // 添加角色标识到body，用于CSS样式区分
    document.body.className = document.body.className.replace(/role-\w+/g, '');
    if (isManager) {
        document.body.classList.add('role-manager');
    } else if (isStaff) {
        document.body.classList.add('role-staff');
    } else if (isWorker) {
        document.body.classList.add('role-worker');
    }
}

// 初始化事件监听器
function initEventListeners() {
    // 登录表单
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // 注册表单
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // 切换登录/注册界面
    document.getElementById('showRegisterBtn').addEventListener('click', showRegisterForm);
    document.getElementById('showLoginBtn').addEventListener('click', showLoginForm);
    
    // 退出登录
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // 修改密码表单
    document.getElementById('changePasswordForm').addEventListener('submit', handleChangePassword);
    
    // 切换到AI模式（直接切换，保持登录状态）
    document.getElementById('switchToAI').addEventListener('click', () => {
        // 保存当前登录状态
        const token = localStorage.getItem('access_token');
        if (token) {
            window.location.href = '/ai';
        } else {
            // 如果未登录，先跳转到AI界面，让用户登录
            window.location.href = '/ai';
        }
    });
    
    // 标签页切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });
    
    // 数据录入表单
    document.getElementById('transactionForm').addEventListener('submit', handleCreateTransaction);
    
    // 筛选按钮
    document.getElementById('filterBtn').addEventListener('click', loadTransactions);
    
    // 报表查询按钮
    document.getElementById('loadDailyReport').addEventListener('click', loadDailyReport);
    document.getElementById('loadWeeklyReport').addEventListener('click', loadWeeklyReport);
    document.getElementById('loadMonthlyReport').addEventListener('click', loadMonthlyReport);
    document.getElementById('loadYearlyReport').addEventListener('click', loadYearlyReport);
    document.getElementById('loadManagementReport').addEventListener('click', loadManagementReport);
    
    // 报表标签切换
    document.querySelectorAll('.report-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const report = btn.dataset.report;
            switchReportTab(report);
        });
    });
    
    // 员工管理
    document.getElementById('addEmployeeBtn').addEventListener('click', () => {
        document.getElementById('addEmployeeModal').style.display = 'block';
    });
    
    document.getElementById('addEmployeeForm').addEventListener('submit', handleAddEmployee);
    
    document.querySelector('.close').addEventListener('click', () => {
        document.getElementById('addEmployeeModal').style.display = 'none';
    });
    
    // 设置默认日期
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('transactionDate').value = today;
    document.getElementById('dailyReportDate').value = today;
    document.getElementById('filterStartDate').value = today;
    document.getElementById('filterEndDate').value = today;
    
    // 设置默认年份和月份
    const now = new Date();
    document.getElementById('weeklyReportYear').value = now.getFullYear();
    document.getElementById('weeklyReportWeek').value = getWeekNumber(now);
    document.getElementById('monthlyReportYear').value = now.getFullYear();
    document.getElementById('monthlyReportMonth').value = now.getMonth() + 1;
    document.getElementById('yearlyReportYear').value = now.getFullYear();
    document.getElementById('managementStartDate').value = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
    document.getElementById('managementEndDate').value = today;
}

// 登录处理
// 显示注册表单
function showRegisterForm() {
    document.getElementById('loginFormContainer').style.display = 'none';
    document.getElementById('registerFormContainer').style.display = 'block';
}

// 显示登录表单
function showLoginForm() {
    document.getElementById('registerFormContainer').style.display = 'none';
    document.getElementById('loginFormContainer').style.display = 'block';
}

// 处理注册
async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const realName = document.getElementById('regRealName').value.trim();
    
    // 客户端验证
    if (username.length < 3 || username.length > 20) {
        showMessage('用户名长度必须在3-20个字符之间', 'error');
        return;
    }
    
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
        showMessage('用户名只能包含字母、数字、下划线和连字符', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('密码长度至少6个字符', 'error');
        return;
    }
    
    if (realName.length < 2 || realName.length > 50) {
        showMessage('真实姓名长度必须在2-50个字符之间', 'error');
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
            showMessage(data.message || '注册成功！请登录', 'success');
            // 清空表单
            document.getElementById('registerForm').reset();
            // 切换到登录界面
            setTimeout(() => {
                showLoginForm();
            }, 1500);
        } else {
            showMessage(data.error || '注册失败', 'error');
        }
    } catch (error) {
        console.error('注册错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
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
            showMain();
            loadInitialData();
            showMessage('登录成功', 'success');
        } else {
            showMessage(data.error || '登录失败', 'error');
        }
    } catch (error) {
        console.error('登录错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 退出登录
function handleLogout() {
    localStorage.removeItem('access_token');
    currentUser = null;
    showLogin();
    showMessage('已退出登录', 'info');
}

// 加载初始数据
async function loadInitialData() {
    await loadEmployees();
    await loadTransactions();
}

// 加载员工列表
async function loadEmployees() {
    try {
        const response = await fetch(`${API_BASE}/employees`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            let employees = data.employees || [];
            
            // 普通工人只能看到自己
            if (currentUser && currentUser.role === 'worker') {
                employees = employees.filter(emp => emp.id === currentUser.id);
            }
            
            // 填充员工选择框
            const employeeSelect = document.getElementById('transactionEmployee');
            employeeSelect.innerHTML = '';
            
            if (currentUser && (currentUser.role === 'manager' || currentUser.role === 'staff')) {
                // 店长和前台员工可以选择所有员工
                employees.forEach(emp => {
                    const option = document.createElement('option');
                    option.value = emp.id;
                    const roleText = emp.role === 'manager' ? '店长' : 
                                   emp.role === 'staff' ? '前台员工' : '普通工人';
                    option.textContent = `${emp.real_name} (${roleText})`;
                    employeeSelect.appendChild(option);
                });
                // 默认选择第一个员工
                if (employees.length > 0) {
                    employeeSelect.value = employees[0].id;
                }
            } else if (currentUser && currentUser.role === 'worker') {
                // 普通工人只能选择自己
                const option = document.createElement('option');
                option.value = currentUser.id;
                option.textContent = `${currentUser.real_name} (普通工人)`;
                employeeSelect.appendChild(option);
                employeeSelect.value = currentUser.id;
            }
            
            // 填充筛选员工选择框
            const filterEmployeeSelect = document.getElementById('filterEmployee');
            filterEmployeeSelect.innerHTML = '<option value="">全部员工</option>';
            
            // 普通工人只能筛选自己，店长和前台员工可以筛选所有
            const filterEmployees = currentUser && currentUser.role === 'worker' 
                ? employees.filter(emp => emp.id === currentUser.id)
                : data.employees || [];
            
            filterEmployees.forEach(emp => {
                const option = document.createElement('option');
                option.value = emp.id;
                option.textContent = emp.real_name;
                filterEmployeeSelect.appendChild(option);
            });
            
            // 填充员工管理表格（仅店长可见）
            if (currentUser && currentUser.role === 'manager') {
                renderEmployeeList(data.employees || []);
            }
        }
    } catch (error) {
        console.error('加载员工列表失败:', error);
    }
}

// 渲染员工列表
function renderEmployeeList(employees) {
    const tbody = document.getElementById('employeeList');
    if (employees.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">暂无员工</td></tr>';
        return;
    }
    
    tbody.innerHTML = employees.map(emp => {
        const roleText = emp.role === 'manager' ? '店长' : 
                        emp.role === 'staff' ? '前台员工' : '普通工人';
        return `
        <tr>
            <td>${emp.username}</td>
            <td>${emp.real_name}</td>
            <td>${roleText}</td>
            <td>${emp.is_active ? '正常' : '禁用'}</td>
            <td>-</td>
        </tr>
    `;
    }).join('');
}

// 创建流水记录
async function handleCreateTransaction(e) {
    e.preventDefault();
    
    // 检查是否为示例账号
    if (currentUser && currentUser.is_demo) {
        showMessage('示例账号只能查看，不能进行数据操作。请使用实际账号登录。', 'error');
        return;
    }
    
    const date = document.getElementById('transactionDate').value;
    const employeeId = parseInt(document.getElementById('transactionEmployee').value);
    const quantity = parseInt(document.getElementById('transactionQuantity').value);
    const totalAmount = parseFloat(document.getElementById('transactionAmount').value);
    const amountDetails = document.getElementById('transactionDetails').value;
    
    // 获取员工列表用于显示名称
    let employees = [];
    try {
        const empResponse = await fetch(`${API_BASE}/employees`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        if (empResponse.ok) {
            const empData = await empResponse.json();
            employees = empData.employees || [];
        }
    } catch (error) {
        console.error('获取员工列表失败:', error);
    }
    
    try {
        const response = await fetch(`${API_BASE}/transactions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                date,
                employee_id: employeeId,
                quantity,
                total_amount: totalAmount,
                amount_details: amountDetails
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const employeeName = employees.find(e => e.id === employeeId)?.real_name || '员工';
            showMessage(`✅ 已成功为 ${employeeName} 录入流水数据！数据已实时同步`, 'success');
            document.getElementById('transactionForm').reset();
            
            // 根据角色设置默认值
            if (currentUser && (currentUser.role === 'manager' || currentUser.role === 'staff')) {
                document.getElementById('transactionDate').value = new Date().toISOString().split('T')[0];
                if (employees.length > 0) {
                    document.getElementById('transactionEmployee').value = employees[0].id;
                }
            } else if (currentUser && currentUser.role === 'worker') {
                document.getElementById('transactionDate').value = new Date().toISOString().split('T')[0];
                document.getElementById('transactionEmployee').value = currentUser.id;
            }
            
            loadTransactions();
            
            // 显示数据同步提示（仅店长和前台员工）
            if (currentUser && (currentUser.role === 'manager' || currentUser.role === 'staff')) {
                setTimeout(() => {
                    showMessage(`💡 提示：${employeeName} 登录账户后将看到这条新录入的流水数据`, 'info');
                }, 2000);
            }
        } else {
            showMessage(data.error || '创建失败', 'error');
        }
    } catch (error) {
        console.error('创建流水记录错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 加载流水列表
async function loadTransactions(page = 1) {
    try {
        const startDate = document.getElementById('filterStartDate').value;
        const endDate = document.getElementById('filterEndDate').value;
        const employeeId = document.getElementById('filterEmployee').value;
        
        let url = `${API_BASE}/transactions?page=${page}&per_page=20`;
        if (startDate) url += `&start_date=${startDate}`;
        if (endDate) url += `&end_date=${endDate}`;
        if (employeeId) url += `&employee_id=${employeeId}`;
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderTransactionList(data.transactions);
            currentPage = data.page;
            totalPages = data.pages;
            renderPagination();
        } else {
            const data = await response.json();
            showMessage(data.error || '加载失败', 'error');
        }
    } catch (error) {
        console.error('加载流水列表错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 渲染流水列表
function renderTransactionList(transactions) {
    const tbody = document.getElementById('transactionList');
    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">暂无数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = transactions.map(t => `
        <tr>
            <td>${t.date}</td>
            <td>${t.employee_name || '未知'}</td>
            <td>${t.quantity}</td>
            <td>¥${t.total_amount.toFixed(2)}</td>
            <td>${t.amount_details || '-'}</td>
            ${currentUser && currentUser.role === 'manager' ? `<td><button class="btn btn-secondary btn-sm" onclick="deleteTransaction(${t.id})">删除</button></td>` : ''}
        </tr>
    `).join('');
}

// 删除流水记录
async function deleteTransaction(id) {
    // 检查是否为示例账号
    if (currentUser && currentUser.is_demo) {
        showMessage('示例账号只能查看，不能进行数据操作。请使用实际账号登录。', 'error');
        return;
    }
    
    if (!confirm('确定要删除这条流水记录吗？')) return;
    
    try {
        const response = await fetch(`${API_BASE}/transactions/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            showMessage('删除成功', 'success');
            loadTransactions(currentPage);
        } else {
            const data = await response.json();
            showMessage(data.error || '删除失败', 'error');
        }
    } catch (error) {
        console.error('删除错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 渲染分页
function renderPagination() {
    const pagination = document.getElementById('pagination');
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    if (currentPage > 1) {
        html += `<button onclick="loadTransactions(${currentPage - 1})">上一页</button>`;
    }
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<button class="${i === currentPage ? 'active' : ''}" onclick="loadTransactions(${i})">${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += `<span>...</span>`;
        }
    }
    
    if (currentPage < totalPages) {
        html += `<button onclick="loadTransactions(${currentPage + 1})">下一页</button>`;
    }
    
    pagination.innerHTML = html;
}

// 切换标签页
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`${tab}Tab`).classList.add('active');
    
    if (tab === 'list') {
        loadTransactions();
    } else if (tab === 'employees' && currentUser && currentUser.role === 'manager') {
        loadEmployees();
    } else if (tab === 'profile') {
        loadProfile();
    }
}

// 切换报表标签
function switchReportTab(report) {
    document.querySelectorAll('.report-tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.report-content').forEach(content => content.classList.remove('active'));
    
    document.querySelector(`[data-report="${report}"]`).classList.add('active');
    document.getElementById(`${report}Report`).classList.add('active');
}

// 加载每日报表
async function loadDailyReport() {
    const date = document.getElementById('dailyReportDate').value;
    if (!date) {
        showMessage('请选择日期', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/reports/daily?date=${date}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderDailyReport(data);
        } else {
            const errorData = await response.json();
            showMessage(errorData.error || '加载失败', 'error');
        }
    } catch (error) {
        console.error('加载日报错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 渲染每日报表
function renderDailyReport(data) {
    const content = document.getElementById('dailyReportContent');
    
    let html = `
        <div class="report-summary">
            <div class="report-summary-item">
                <h3>总数量</h3>
                <div class="value">${data.summary.total_quantity}</div>
            </div>
            <div class="report-summary-item">
                <h3>总金额</h3>
                <div class="value">¥${data.summary.total_amount.toFixed(2)}</div>
            </div>
            <div class="report-summary-item">
                <h3>员工数</h3>
                <div class="value">${data.summary.employee_count}</div>
            </div>
        </div>
    `;
    
    if (Object.keys(data.by_employee).length > 0) {
        html += '<h3>按员工统计</h3><table class="data-table"><thead><tr><th>员工</th><th>数量</th><th>总金额</th></tr></thead><tbody>';
        for (const [emp, stats] of Object.entries(data.by_employee)) {
            html += `<tr><td>${emp}</td><td>${stats.quantity}</td><td>¥${stats.total_amount.toFixed(2)}</td></tr>`;
        }
        html += '</tbody></table>';
    }
    
    if (Object.keys(data.payment_methods).length > 0) {
        html += '<h3>支付方式统计</h3><table class="data-table"><thead><tr><th>支付方式</th><th>金额</th></tr></thead><tbody>';
        for (const [method, amount] of Object.entries(data.payment_methods)) {
            html += `<tr><td>${method}</td><td>¥${amount.toFixed(2)}</td></tr>`;
        }
        html += '</tbody></table>';
    }
    
    content.innerHTML = html;
}

// 加载每周报表
async function loadWeeklyReport() {
    const year = parseInt(document.getElementById('weeklyReportYear').value);
    const week = parseInt(document.getElementById('weeklyReportWeek').value);
    
    try {
        const response = await fetch(`${API_BASE}/reports/weekly?year=${year}&week=${week}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderWeeklyReport(data);
        } else {
            const errorData = await response.json();
            showMessage(errorData.error || '加载失败', 'error');
        }
    } catch (error) {
        console.error('加载周报错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 渲染每周报表
function renderWeeklyReport(data) {
    const content = document.getElementById('weeklyReportContent');
    
    let html = `
        <div class="report-summary">
            <div class="report-summary-item">
                <h3>总数量</h3>
                <div class="value">${data.summary.total_quantity}</div>
            </div>
            <div class="report-summary-item">
                <h3>总金额</h3>
                <div class="value">¥${data.summary.total_amount.toFixed(2)}</div>
            </div>
            <div class="report-summary-item">
                <h3>员工数</h3>
                <div class="value">${data.summary.employee_count}</div>
            </div>
        </div>
        <p>周期：${data.start_date} 至 ${data.end_date}</p>
    `;
    
    if (Object.keys(data.by_employee).length > 0) {
        html += '<h3>按员工统计</h3><table class="data-table"><thead><tr><th>员工</th><th>数量</th><th>总金额</th></tr></thead><tbody>';
        for (const [emp, stats] of Object.entries(data.by_employee)) {
            html += `<tr><td>${emp}</td><td>${stats.quantity}</td><td>¥${stats.total_amount.toFixed(2)}</td></tr>`;
        }
        html += '</tbody></table>';
    }
    
    content.innerHTML = html;
}

// 加载每月报表
async function loadMonthlyReport() {
    const year = parseInt(document.getElementById('monthlyReportYear').value);
    const month = parseInt(document.getElementById('monthlyReportMonth').value);
    
    try {
        const response = await fetch(`${API_BASE}/reports/monthly?year=${year}&month=${month}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderMonthlyReport(data);
        } else {
            const errorData = await response.json();
            showMessage(errorData.error || '加载失败', 'error');
        }
    } catch (error) {
        console.error('加载月报错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 渲染每月报表
function renderMonthlyReport(data) {
    const content = document.getElementById('monthlyReportContent');
    
    let html = `
        <div class="report-summary">
            <div class="report-summary-item">
                <h3>总数量</h3>
                <div class="value">${data.summary.total_quantity}</div>
            </div>
            <div class="report-summary-item">
                <h3>总金额</h3>
                <div class="value">¥${data.summary.total_amount.toFixed(2)}</div>
            </div>
            <div class="report-summary-item">
                <h3>员工数</h3>
                <div class="value">${data.summary.employee_count}</div>
            </div>
            <div class="report-summary-item">
                <h3>日均金额</h3>
                <div class="value">¥${(data.summary.total_amount / data.summary.days_in_month).toFixed(2)}</div>
            </div>
        </div>
        <p>周期：${data.start_date} 至 ${data.end_date}</p>
    `;
    
    if (Object.keys(data.by_employee).length > 0) {
        html += '<h3>按员工统计</h3><table class="data-table"><thead><tr><th>员工</th><th>数量</th><th>总金额</th><th>日均金额</th></tr></thead><tbody>';
        for (const [emp, stats] of Object.entries(data.by_employee)) {
            html += `<tr><td>${emp}</td><td>${stats.quantity}</td><td>¥${stats.total_amount.toFixed(2)}</td><td>¥${stats.daily_avg.toFixed(2)}</td></tr>`;
        }
        html += '</tbody></table>';
    }
    
    content.innerHTML = html;
}

// 加载年报
async function loadYearlyReport() {
    const year = parseInt(document.getElementById('yearlyReportYear').value);
    
    try {
        const response = await fetch(`${API_BASE}/reports/yearly?year=${year}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderYearlyReport(data);
        } else {
            const errorData = await response.json();
            showMessage(errorData.error || '加载失败', 'error');
        }
    } catch (error) {
        console.error('加载年报错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 渲染年报
function renderYearlyReport(data) {
    const content = document.getElementById('yearlyReportContent');
    
    let html = `
        <div class="report-summary">
            <div class="report-summary-item">
                <h3>总数量</h3>
                <div class="value">${data.summary.total_quantity}</div>
            </div>
            <div class="report-summary-item">
                <h3>总金额</h3>
                <div class="value">¥${data.summary.total_amount.toFixed(2)}</div>
            </div>
            <div class="report-summary-item">
                <h3>员工数</h3>
                <div class="value">${data.summary.employee_count}</div>
            </div>
        </div>
        <p>周期：${data.start_date} 至 ${data.end_date}</p>
    `;
    
    if (Object.keys(data.by_employee).length > 0) {
        html += '<h3>按员工统计</h3><table class="data-table"><thead><tr><th>员工</th><th>数量</th><th>总金额</th></tr></thead><tbody>';
        for (const [emp, stats] of Object.entries(data.by_employee)) {
            html += `<tr><td>${emp}</td><td>${stats.quantity}</td><td>¥${stats.total_amount.toFixed(2)}</td></tr>`;
        }
        html += '</tbody></table>';
        
        // 月度趋势
        html += '<h3>月度趋势</h3><table class="data-table"><thead><tr><th>员工</th>';
        for (let m = 1; m <= 12; m++) {
            html += `<th>${m}月</th>`;
        }
        html += '</tr></thead><tbody>';
        for (const [emp, stats] of Object.entries(data.by_employee)) {
            html += `<tr><td>${emp}</td>`;
            for (let m = 1; m <= 12; m++) {
                const monthData = stats.monthly_stats[m] || {total_amount: 0};
                html += `<td>¥${monthData.total_amount.toFixed(2)}</td>`;
            }
            html += '</tr>';
        }
        html += '</tbody></table>';
    }
    
    content.innerHTML = html;
}

// 加载管理层报表
async function loadManagementReport() {
    const startDate = document.getElementById('managementStartDate').value;
    const endDate = document.getElementById('managementEndDate').value;
    
    try {
        const response = await fetch(`${API_BASE}/reports/management?start_date=${startDate}&end_date=${endDate}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderManagementReport(data);
        } else {
            const errorData = await response.json();
            showMessage(errorData.error || '加载失败', 'error');
        }
    } catch (error) {
        console.error('加载管理层报表错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 渲染管理层报表
function renderManagementReport(data) {
    const content = document.getElementById('managementReportContent');
    
    let html = `
        <div class="report-summary">
            <div class="report-summary-item">
                <h3>总交易数</h3>
                <div class="value">${data.summary.total_transactions}</div>
            </div>
            <div class="report-summary-item">
                <h3>总数量</h3>
                <div class="value">${data.summary.total_quantity}</div>
            </div>
            <div class="report-summary-item">
                <h3>总金额</h3>
                <div class="value">¥${data.summary.total_amount.toFixed(2)}</div>
            </div>
            <div class="report-summary-item">
                <h3>日均金额</h3>
                <div class="value">¥${data.summary.avg_daily_amount.toFixed(2)}</div>
            </div>
            <div class="report-summary-item">
                <h3>单笔平均</h3>
                <div class="value">¥${data.summary.avg_per_transaction.toFixed(2)}</div>
            </div>
            <div class="report-summary-item">
                <h3>增长率</h3>
                <div class="value">${data.summary.growth_rate > 0 ? '+' : ''}${data.summary.growth_rate.toFixed(2)}%</div>
            </div>
        </div>
        <p>周期：${data.period.start_date} 至 ${data.period.end_date} (${data.period.days}天)</p>
    `;
    
    // 员工排名
    if (data.employee_ranking && data.employee_ranking.length > 0) {
        html += '<h3>员工排名</h3><table class="data-table"><thead><tr><th>排名</th><th>员工</th><th>数量</th><th>总金额</th><th>交易数</th><th>单笔平均</th></tr></thead><tbody>';
        data.employee_ranking.forEach((item, index) => {
            html += `<tr>
                <td>${index + 1}</td>
                <td>${item.name}</td>
                <td>${item.stats.quantity}</td>
                <td>¥${item.stats.total_amount.toFixed(2)}</td>
                <td>${item.stats.transaction_count}</td>
                <td>¥${item.stats.avg_per_transaction.toFixed(2)}</td>
            </tr>`;
        });
        html += '</tbody></table>';
    }
    
    // 支付方式统计
    if (Object.keys(data.payment_methods).length > 0) {
        html += '<h3>支付方式统计</h3><table class="data-table"><thead><tr><th>支付方式</th><th>金额</th><th>占比</th></tr></thead><tbody>';
        const totalAmount = data.summary.total_amount;
        for (const [method, amount] of Object.entries(data.payment_methods)) {
            const percentage = (amount / totalAmount * 100).toFixed(2);
            html += `<tr><td>${method}</td><td>¥${amount.toFixed(2)}</td><td>${percentage}%</td></tr>`;
        }
        html += '</tbody></table>';
    }
    
    // 趋势分析
    if (data.trends) {
        html += '<h3>趋势分析</h3>';
        html += `<p>最高日：${data.trends.highest_day || '无'}</p>`;
        html += `<p>最低日：${data.trends.lowest_day || '无'}</p>`;
    }
    
    content.innerHTML = html;
}

// 添加员工
async function handleAddEmployee(e) {
    e.preventDefault();
    
    const username = document.getElementById('newUsername').value;
    const password = document.getElementById('newPassword').value;
    const realName = document.getElementById('newRealName').value;
    const role = document.getElementById('newRole').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                username,
                password,
                real_name: realName,
                role
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('员工创建成功', 'success');
            document.getElementById('addEmployeeForm').reset();
            document.getElementById('addEmployeeModal').style.display = 'none';
            loadEmployees();
        } else {
            showMessage(data.error || '创建失败', 'error');
        }
    } catch (error) {
        console.error('创建员工错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}

// 显示消息
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // 警告和错误消息显示时间更长
    const displayTime = (type === 'warning' || type === 'error') ? 5000 : 3000;
    
    setTimeout(() => {
        messageDiv.style.animation = 'slideUp 0.3s ease-out reverse';
        setTimeout(() => messageDiv.remove(), 300);
    }, displayTime);
}

// 获取周数
function getWeekNumber(date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// 加载个人主页信息
async function loadProfile() {
    if (!currentUser) {
        await fetchCurrentUser();
    }
    
    if (currentUser) {
        // 填充用户信息
        document.getElementById('profileUsername').textContent = currentUser.username;
        document.getElementById('profileRealName').textContent = currentUser.real_name;
        
        const roleText = currentUser.role === 'manager' ? '店长' : 
                        currentUser.role === 'staff' ? '前台员工' : '普通工人';
        document.getElementById('profileRole').textContent = roleText;
        
        document.getElementById('profileStatus').textContent = currentUser.is_active ? '正常' : '禁用';
        
        if (currentUser.created_at) {
            const createdDate = new Date(currentUser.created_at);
            document.getElementById('profileCreatedAt').textContent = createdDate.toLocaleString('zh-CN');
        }
        
        // 检查是否有密码修改记录
        try {
            const response = await fetch(`${API_BASE}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                const user = data.user;
                
                if (user.password_changed_at) {
                    const changedDate = new Date(user.password_changed_at);
                    document.getElementById('profilePasswordChangedAt').textContent = changedDate.toLocaleString('zh-CN');
                    document.getElementById('passwordChangeInfo').style.display = 'block';
                    
                    // 检查今天是否已修改过密码
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const lastChange = new Date(changedDate);
                    lastChange.setHours(0, 0, 0, 0);
                    
                    if (lastChange.getTime() === today.getTime()) {
                        // 今天已修改过，显示提示
                        document.getElementById('passwordChangeHint').style.display = 'block';
                        const nextChange = new Date(today);
                        nextChange.setDate(nextChange.getDate() + 1);
                        document.getElementById('nextChangeTime').textContent = 
                            `下次可修改时间：${nextChange.toLocaleDateString('zh-CN')} 00:00`;
                        document.getElementById('changePasswordBtn').disabled = true;
                    } else {
                        document.getElementById('passwordChangeHint').style.display = 'none';
                        document.getElementById('changePasswordBtn').disabled = false;
                    }
                } else {
                    document.getElementById('passwordChangeInfo').style.display = 'none';
                    document.getElementById('passwordChangeHint').style.display = 'none';
                    document.getElementById('changePasswordBtn').disabled = false;
                }
            }
        } catch (error) {
            console.error('获取用户信息失败:', error);
        }
    }
}

// 处理修改密码
async function handleChangePassword(e) {
    e.preventDefault();
    
    const oldPassword = document.getElementById('oldPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // 验证新密码和确认密码是否一致
    if (newPassword !== confirmPassword) {
        showMessage('新密码和确认密码不一致', 'error');
        return;
    }
    
    // 检查是否为示例账号
    if (currentUser && currentUser.is_demo) {
        showMessage('示例账号不能修改密码', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('密码修改成功', 'success');
            document.getElementById('changePasswordForm').reset();
            // 重新加载个人主页信息
            setTimeout(() => {
                loadProfile();
            }, 1000);
        } else {
            showMessage(data.error || '修改密码失败', 'error');
            if (data.next_change_time) {
                const nextTime = new Date(data.next_change_time);
                document.getElementById('nextChangeTime').textContent = 
                    `下次可修改时间：${nextTime.toLocaleString('zh-CN')}`;
                document.getElementById('passwordChangeHint').style.display = 'block';
            }
        }
    } catch (error) {
        console.error('修改密码错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
}


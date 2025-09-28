let currentUserId = null;
let allUsers = [];
let allVenues = [];
let currentMatchRequestId = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadUsers();
    loadVenues();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 用户选择变化
    document.getElementById('currentUser').addEventListener('change', function() {
        currentUserId = parseInt(this.value);
        if (currentUserId) {
            loadReceivedRequests();
            loadSentRequests();
        }
    });

    // 匹配表单提交
    document.getElementById('matchForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitMatchRequest();
    });

    // 模态框关闭
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });

    // 点击模态框外部关闭
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// 加载所有用户
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        allUsers = await response.json();
        
        populateUserSelector();
        displayUsers();
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// 填充用户选择器
function populateUserSelector() {
    const selector = document.getElementById('currentUser');
    selector.innerHTML = '<option value="">请选择...</option>';
    
    allUsers.forEach(user => {
        const option = document.createElement('option');
        option.value = user.id;
        option.textContent = user.name;
        selector.appendChild(option);
    });
}

// 显示用户列表
function displayUsers() {
    const usersList = document.getElementById('usersList');
    
    if (!currentUserId) {
        usersList.innerHTML = '<div class="empty-state">请先选择你的身份</div>';
        return;
    }

    const otherUsers = allUsers.filter(user => user.id !== currentUserId);
    
    if (otherUsers.length === 0) {
        usersList.innerHTML = '<div class="empty-state">暂无其他用户</div>';
        return;
    }

    usersList.innerHTML = otherUsers.map(user => `
        <div class="user-card">
            <div class="user-header">
                <div class="user-info">
                    <h3>${user.name}</h3>
                    <p>${user.email}</p>
                </div>
                <button class="match-button" onclick="openMatchModal(${user.id}, '${user.name}')">
                    发起匹配
                </button>
            </div>
            <div class="user-bio">${user.bio}</div>
            <div class="time-slots">
                <h4>可用时间：</h4>
                ${user.available_slots.length > 0 ? 
                    user.available_slots.map(slot => 
                        `<span class="time-slot">${formatDateTime(slot.start_time)} - ${formatTime(slot.end_time)}</span>`
                    ).join('') 
                    : '<span style="color: #999;">暂无可用时间</span>'
                }
            </div>
        </div>
    `).join('');
}

// 加载场所信息
async function loadVenues() {
    try {
        const response = await fetch('/api/venues');
        allVenues = await response.json();
    } catch (error) {
        console.error('Error loading venues:', error);
    }
}

// 打开匹配模态框
async function openMatchModal(targetId, targetName) {
    if (!currentUserId) {
        alert('请先选择你的身份');
        return;
    }

    document.getElementById('targetUserId').value = targetId;
    document.getElementById('targetUserName').textContent = targetName;
    
    // 加载目标用户的时间槽
    await loadUserTimeSlots(targetId);
    
    // 加载场所列表
    populateVenueSelect();
    
    document.getElementById('matchModal').style.display = 'block';
}

// 加载用户时间槽
async function loadUserTimeSlots(userId) {
    try {
        const response = await fetch(`/api/users/${userId}/timeslots`);
        const timeSlots = await response.json();
        
        const select = document.getElementById('timeSlotSelect');
        select.innerHTML = '<option value="">请选择时间段...</option>';
        
        timeSlots.forEach(slot => {
            const option = document.createElement('option');
            option.value = slot.id;
            option.textContent = `${formatDateTime(slot.start_time)} - ${formatTime(slot.end_time)}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading time slots:', error);
    }
}

// 填充场所选择器
function populateVenueSelect() {
    const select = document.getElementById('venueSelect');
    select.innerHTML = '<option value="">请选择餐厅/咖啡店...</option>';
    
    allVenues.forEach(venue => {
        const option = document.createElement('option');
        option.value = venue.id;
        option.textContent = `${venue.name} (${venue.type === 'coffee' ? '咖啡店' : '餐厅'}) - ${venue.price_range}`;
        select.appendChild(option);
    });
}

// 根据类型筛选场所
function filterVenues() {
    const venueType = document.getElementById('venueType').value;
    const select = document.getElementById('venueSelect');
    
    select.innerHTML = '<option value="">请选择餐厅/咖啡店...</option>';
    
    const filteredVenues = venueType ? 
        allVenues.filter(venue => venue.type === venueType) : 
        allVenues;
    
    filteredVenues.forEach(venue => {
        const option = document.createElement('option');
        option.value = venue.id;
        option.textContent = `${venue.name} (${venue.type === 'coffee' ? '咖啡店' : '餐厅'}) - ${venue.price_range}`;
        select.appendChild(option);
    });
}

// 提交匹配请求
async function submitMatchRequest() {
    const formData = new FormData();
    formData.append('requester_id', currentUserId);
    formData.append('target_id', document.getElementById('targetUserId').value);
    formData.append('time_slot_id', document.getElementById('timeSlotSelect').value);
    formData.append('venue_id', document.getElementById('venueSelect').value);
    formData.append('message', document.getElementById('message').value);

    try {
        const response = await fetch('/api/matches', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            alert('匹配请求发送成功！');
            document.getElementById('matchModal').style.display = 'none';
            document.getElementById('matchForm').reset();
            loadSentRequests(); // 刷新发送的请求列表
        } else {
            alert('发送失败，请重试');
        }
    } catch (error) {
        console.error('Error submitting match request:', error);
        alert('发送失败，请重试');
    }
}

// 加载收到的请求
async function loadReceivedRequests() {
    if (!currentUserId) return;

    try {
        const response = await fetch(`/api/matches/received/${currentUserId}`);
        const requests = await response.json();
        
        const container = document.getElementById('receivedRequests');
        
        if (requests.length === 0) {
            container.innerHTML = '<div class="empty-state">暂无收到的邀请</div>';
            return;
        }

        container.innerHTML = requests.map(request => `
            <div class="request-card">
                <div class="request-header">
                    <h3>${request.requester_name}</h3>
                    <span class="request-status status-pending">待处理</span>
                </div>
                <p><strong>邮箱：</strong>${request.requester_email}</p>
                <p><strong>建议时间：</strong>${formatDateTime(request.proposed_time)}</p>
                <p><strong>建议地点：</strong>${request.venue_name} (${request.venue_type === 'coffee' ? '咖啡店' : '餐厅'})</p>
                <p><strong>留言：</strong>${request.message || '无'}</p>
                <p><strong>发送时间：</strong>${formatDateTime(request.created_at)}</p>
                <button class="match-button" onclick="openResponseModal(${request.id})">
                    响应邀请
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading received requests:', error);
    }
}

// 加载发送的请求
async function loadSentRequests() {
    if (!currentUserId) return;

    try {
        const response = await fetch(`/api/matches/sent/${currentUserId}`);
        const requests = await response.json();
        
        const container = document.getElementById('sentRequests');
        
        if (requests.length === 0) {
            container.innerHTML = '<div class="empty-state">暂无发送的邀请</div>';
            return;
        }

        container.innerHTML = requests.map(request => `
            <div class="request-card">
                <div class="request-header">
                    <h3>${request.target_name}</h3>
                    <span class="request-status status-${request.status}">${getStatusText(request.status)}</span>
                </div>
                <p><strong>邮箱：</strong>${request.target_email}</p>
                <p><strong>建议时间：</strong>${formatDateTime(request.proposed_time)}</p>
                <p><strong>建议地点：</strong>${request.venue_name}</p>
                <p><strong>留言：</strong>${request.message || '无'}</p>
                <p><strong>发送时间：</strong>${formatDateTime(request.created_at)}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading sent requests:', error);
    }
}

// 打开响应模态框
function openResponseModal(requestId) {
    currentMatchRequestId = requestId;
    
    // 这里可以加载更详细的请求信息
    document.getElementById('responseModal').style.display = 'block';
    document.getElementById('rescheduleForm').style.display = 'none';
}

// 显示重新安排表单
async function showRescheduleForm() {
    document.getElementById('rescheduleForm').style.display = 'block';
    
    // 加载当前用户的时间槽
    await loadCurrentUserTimeSlots();
    populateRescheduleVenues();
}

// 加载当前用户的时间槽（用于重新安排）
async function loadCurrentUserTimeSlots() {
    try {
        const response = await fetch(`/api/users/${currentUserId}/timeslots`);
        const timeSlots = await response.json();
        
        const select = document.getElementById('newTimeSlot');
        select.innerHTML = '<option value="">选择新时间...</option>';
        
        timeSlots.forEach(slot => {
            const option = document.createElement('option');
            option.value = slot.id;
            option.textContent = `${formatDateTime(slot.start_time)} - ${formatTime(slot.end_time)}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading time slots:', error);
    }
}

// 填充重新安排的场所选择器
function populateRescheduleVenues() {
    const select = document.getElementById('newVenue');
    select.innerHTML = '<option value="">选择新地点...</option>';
    
    allVenues.forEach(venue => {
        const option = document.createElement('option');
        option.value = venue.id;
        option.textContent = `${venue.name} (${venue.type === 'coffee' ? '咖啡店' : '餐厅'})`;
        select.appendChild(option);
    });
}

// 响应匹配请求
async function respondToMatch(action) {
    const formData = new FormData();
    formData.append('action', action);
    
    if (action === 'reschedule') {
        const newTimeSlotId = document.getElementById('newTimeSlot').value;
        const newVenueId = document.getElementById('newVenue').value;
        
        if (newTimeSlotId) formData.append('new_time_slot_id', newTimeSlotId);
        if (newVenueId) formData.append('new_venue_id', newVenueId);
    }

    try {
        const response = await fetch(`/api/matches/${currentMatchRequestId}/respond`, {
            method: 'PUT',
            body: formData
        });

        if (response.ok) {
            alert(`邀请已${getActionText(action)}！`);
            document.getElementById('responseModal').style.display = 'none';
            loadReceivedRequests(); // 刷新收到的请求列表
        } else {
            alert('操作失败，请重试');
        }
    } catch (error) {
        console.error('Error responding to match:', error);
        alert('操作失败，请重试');
    }
}

// 显示标签页
function showTab(tabName) {
    // 隐藏所有标签页内容
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 移除所有标签按钮的活动状态
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 显示选中的标签页
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // 根据标签页加载相应数据
    if (tabName === 'browse') {
        displayUsers();
    } else if (tabName === 'requests') {
        loadReceivedRequests();
    } else if (tabName === 'sent') {
        loadSentRequests();
    }
}

// 工具函数

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('zh-CN', {
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getStatusText(status) {
    const statusMap = {
        'pending': '待处理',
        'accepted': '已接受',
        'rejected': '已拒绝',
        'rescheduled': '已重新安排'
    };
    return statusMap[status] || status;
}

function getActionText(action) {
    const actionMap = {
        'accept': '接受',
        'reject': '拒绝',
        'reschedule': '重新安排'
    };
    return actionMap[action] || action;
}
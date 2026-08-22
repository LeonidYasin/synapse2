// Synapse Frontend - Single Page Application

const API_URL = window.API_URL || 'http://localhost:8000';

// State
let state = {
    token: localStorage.getItem('token'),
    user: null,
    currentView: 'chat',
    dialogues: [],
    currentDialogueId: null,
    messages: []
};

console.log('🔑 Initial token from localStorage:', state.token);

// DOM Elements
const app = document.getElementById('app');

// Navigation
function navigateTo(view) {
    state.currentView = view;
    render();
}

// API calls
async function apiCall(endpoint, options = {}, customToken = null) {
    const url = `${API_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    const token = customToken || state.token;
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        console.log(`🔑 Sending token for ${endpoint}:`, token.substring(0, 20) + '...');
    } else {
        console.log(`❌ No token for ${endpoint}`);
    }
    console.log(`📡 ${options.method || 'GET'} ${url}`);
    const response = await fetch(url, {
        ...options,
        headers
    });
    const data = await response.json();
    console.log(`📡 Response ${response.status}:`, data);
    if (!response.ok) {
        throw new Error(data.detail || 'API error');
    }
    return data;
}

// Auth functions
async function register(username, email, password) {
    try {
        console.log('📝 Registering:', username, email);
        const data = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
        console.log('✅ Registration success:', data);
        state.token = data.access_token;
        localStorage.setItem('token', state.token);
        console.log('🔑 Token saved:', state.token);
        // Load user with the new token
        state.user = await apiCall('/auth/me', {}, state.token);
        console.log('👤 User loaded:', state.user);
        render();
        return { success: true };
    } catch (error) {
        console.error('❌ Register error:', error);
        return { success: false, error: error.message };
    }
}

async function login(username, password) {
    try {
        console.log('🔑 Logging in:', username);
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        const data = await apiCall('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
        console.log('✅ Login success:', data);
        state.token = data.access_token;
        localStorage.setItem('token', state.token);
        console.log('🔑 Token saved:', state.token);
        // Load user with the new token
        state.user = await apiCall('/auth/me', {}, state.token);
        console.log('👤 User loaded:', state.user);
        render();
        return { success: true };
    } catch (error) {
        console.error('❌ Login error:', error);
        return { success: false, error: error.message };
    }
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    render();
}

async function loadUser() {
    if (!state.token) return;
    try {
        state.user = await apiCall('/auth/me', {}, state.token);
        console.log('👤 User loaded:', state.user);
    } catch (error) {
        console.error('❌ Load user error:', error);
        state.user = null;
        state.token = null;
        localStorage.removeItem('token');
    }
}

// Render functions
function render() {
    console.log('🔄 Render, token:', !!state.token, 'user:', !!state.user);
    if (!state.token || !state.user) {
        renderAuth();
        return;
    }
    renderApp();
}

function renderAuth() {
    const isLogin = state.currentView === 'login';
    app.innerHTML = `
        <div class="auth-container">
            <div class="auth-card">
                <h1>Синапс</h1>
                <h2>${isLogin ? 'Вход' : 'Регистрация'}</h2>
                <form id="auth-form" class="auth-form">
                    <div class="form-group">
                        <label for="username">Имя пользователя</label>
                        <input type="text" id="username" placeholder="username" required>
                    </div>
                    ${!isLogin ? `
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" placeholder="email@example.com" required>
                    </div>
                    ` : ''}
                    <div class="form-group">
                        <label for="password">Пароль</label>
                        <input type="password" id="password" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn-primary">${isLogin ? 'Войти' : 'Зарегистрироваться'}</button>
                </form>
                <p class="auth-switch">
                    ${isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}
                    <a href="#" onclick="navigateTo('${isLogin ? 'register' : 'login'}'); return false;">
                        ${isLogin ? 'Зарегистрироваться' : 'Войти'}
                    </a>
                </p>
                <div id="auth-error" class="auth-error" style="display:none;"></div>
            </div>
        </div>
    `;
    
    document.getElementById('auth-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('auth-error');
        
        let result;
        if (isLogin) {
            result = await login(username, password);
        } else {
            const email = document.getElementById('email').value;
            result = await register(username, email, password);
        }
        
        if (!result.success) {
            errorEl.textContent = result.error;
            errorEl.style.display = 'block';
        } else {
            errorEl.style.display = 'none';
        }
    });
}

function renderApp() {
    app.innerHTML = `
        <div class="app-container">
            <header class="app-header">
                <h1>🧠 Синапс</h1>
                <div class="header-actions">
                    <span class="user-name">${state.user?.username || 'User'}</span>
                    <button onclick="logout()" class="btn-outline">Выйти</button>
                </div>
            </header>
            <div class="app-content">
                <div class="sidebar">
                    <button class="btn-primary new-chat-btn" onclick="startNewChat()">+ Новый чат</button>
                    <div class="dialogue-list">
                        ${state.dialogues.length === 0 ? '<p class="empty-state">Нет диалогов</p>' : ''}
                        ${state.dialogues.map(d => `
                            <div class="dialogue-item ${d.id === state.currentDialogueId ? 'active' : ''}" 
                                 onclick="loadDialogue(${d.id})">
                                ${d.title || 'Новый чат'}
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="main-content">
                    <div class="messages-container" id="messages-container">
                        ${state.messages.length === 0 ? '<p class="empty-state">Начните диалог</p>' : ''}
                        ${state.messages.map(m => `
                            <div class="message ${m.role}">
                                <div class="message-content">${m.content}</div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="input-container">
                        <input type="text" id="message-input" placeholder="Напишите сообщение..." />
                        <button onclick="sendMessage()" class="btn-primary">Отправить</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('message-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    const container = document.getElementById('messages-container');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

async function startNewChat() {
    try {
        const data = await apiCall('/chat', { method: 'POST' }, state.token);
        state.currentDialogueId = data.id;
        state.messages = [];
        await loadDialogues();
        render();
    } catch (error) {
        console.error('Failed to create chat:', error);
    }
}

async function loadDialogues() {
    try {
        state.dialogues = await apiCall('/chat', {}, state.token);
    } catch (error) {
        state.dialogues = [];
    }
}

async function loadDialogue(id) {
    try {
        state.currentDialogueId = id;
        state.messages = await apiCall(`/chat/${id}`, {}, state.token);
        render();
    } catch (error) {
        console.error('Failed to load dialogue:', error);
    }
}

async function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    
    state.messages.push({ role: 'user', content: text });
    render();
    
    try {
        const response = await apiCall('/chat/send', {
            method: 'POST',
            body: JSON.stringify({
                dialogue_id: state.currentDialogueId,
                message: text
            })
        }, state.token);
        state.messages.push({ role: 'assistant', content: response.response });
        render();
    } catch (error) {
        state.messages.push({ role: 'assistant', content: '⚠️ Ошибка: ' + error.message });
        render();
    }
}

// Initialize
async function init() {
    if (state.token) {
        await loadUser();
    }
    if (state.user) {
        await loadDialogues();
    }
    render();
}

// Make functions globally accessible
window.navigateTo = navigateTo;
window.logout = logout;
window.startNewChat = startNewChat;
window.loadDialogue = loadDialogue;
window.sendMessage = sendMessage;
window.API_URL = API_URL;

init();

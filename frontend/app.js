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

// DOM Elements
const app = document.getElementById('app');

// Navigation
function navigateTo(view) {
    state.currentView = view;
    render();
}
window.navigateTo = navigateTo;

// API calls
async function apiCall(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    const response = await fetch(url, {
        ...options,
        headers
    });
    let data;
    try {
        data = await response.json();
    } catch {
        data = { detail: 'Invalid response from server' };
    }
    if (!response.ok) {
        const errorMsg = typeof data === 'string' ? data : (data.detail || JSON.stringify(data) || 'Unknown error');
        throw new Error(errorMsg);
    }
    return data;
}

// Auth functions
async function register(username, email, password) {
    console.log('[REGISTER] username:', username);
    console.log('[REGISTER] email:', email);
    console.log('[REGISTER] password length:', password.length);
    
    try {
        const data = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ 
                username: username.trim(), 
                email: email.trim(), 
                password: password 
            })
        });
        console.log('[REGISTER] response:', data);
        if (data.access_token) {
            state.token = data.access_token;
            localStorage.setItem('token', state.token);
            await loadUser();
            render();
            return { success: true };
        } else {
            return { success: false, error: 'No token received' };
        }
    } catch (error) {
        console.error('[REGISTER] error:', error);
        return { success: false, error: error.message };
    }
}

async function login(username, password) {
    try {
        const formData = new URLSearchParams();
        formData.append('username', username.trim());
        formData.append('password', password);
        const data = await apiCall('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
        if (data.access_token) {
            state.token = data.access_token;
            localStorage.setItem('token', state.token);
            await loadUser();
            render();
            return { success: true };
        } else {
            return { success: false, error: 'No token received' };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    render();
}
window.logout = logout;

async function loadUser() {
    try {
        state.user = await apiCall('/auth/me');
        return true;
    } catch (error) {
        console.error('Failed to load user:', error);
        state.user = null;
        state.token = null;
        localStorage.removeItem('token');
        return false;
    }
}

// Render functions
function render() {
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
                <h1>🧠 Синапс</h1>
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
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('auth-error');
        
        if (!username || username.length < 2) {
            errorEl.textContent = 'Имя пользователя должно содержать минимум 2 символа';
            errorEl.style.display = 'block';
            return;
        }
        if (!password || password.length < 4) {
            errorEl.textContent = 'Пароль должен содержать минимум 4 символа';
            errorEl.style.display = 'block';
            return;
        }
        
        let result;
        if (isLogin) {
            result = await login(username, password);
        } else {
            const email = document.getElementById('email').value.trim();
            if (!email || !email.includes('@')) {
                errorEl.textContent = 'Пожалуйста, укажите корректный email';
                errorEl.style.display = 'block';
                return;
            }
            result = await register(username, email, password);
        }
        
        if (!result.success) {
            errorEl.textContent = result.error || 'Произошла ошибка';
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
        const data = await apiCall('/chat', { method: 'POST' });
        state.currentDialogueId = data.id;
        state.messages = [];
        await loadDialogues();
        render();
    } catch (error) {
        console.error('Failed to create chat:', error);
    }
}
window.startNewChat = startNewChat;

async function loadDialogues() {
    try {
        state.dialogues = await apiCall('/chat');
    } catch (error) {
        state.dialogues = [];
    }
}

async function loadDialogue(id) {
    try {
        state.currentDialogueId = id;
        state.messages = await apiCall(`/chat/${id}`);
        render();
    } catch (error) {
        console.error('Failed to load dialogue:', error);
    }
}
window.loadDialogue = loadDialogue;

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
        });
        state.messages.push({ role: 'assistant', content: response.response || 'Ответ получен' });
        render();
    } catch (error) {
        state.messages.push({ role: 'assistant', content: '⚠️ Ошибка: ' + error.message });
        render();
    }
}
window.sendMessage = sendMessage;

// Initialize
async function init() {
    console.log('[INIT] Starting...');
    console.log('[INIT] API_URL:', API_URL);
    if (state.token) {
        console.log('[INIT] Token found in localStorage');
        const ok = await loadUser();
        if (!ok) {
            state.token = null;
            localStorage.removeItem('token');
        }
    } else {
        console.log('[INIT] No token found');
    }
    if (state.user) {
        await loadDialogues();
    }
    render();
    console.log('[INIT] Complete');
}

window.API_URL = API_URL;

init();

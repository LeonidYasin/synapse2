// Synapse Frontend - Single Page Application

const API_URL = window.API_URL || 'http://localhost:8000';

// State
let state = {
    token: localStorage.getItem('token'),
    user: null,
    currentView: 'register',
    dialogues: [],
    currentDialogueId: null,
    messages: []
};

// DOM Elements
const app = document.getElementById('app');

function navigateTo(view) {
    state.currentView = view;
    render();
}
window.navigateTo = navigateTo;

async function apiCall(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    const response = await fetch(url, { ...options, headers });
    let data;
    try { data = await response.json(); } catch { data = { detail: 'Invalid response' }; }
    if (!response.ok) {
        throw new Error(data.detail || 'API error');
    }
    return data;
}

async function register(username, email, password) {
    console.log('REGISTER:', { username, email, password: '***' });
    try {
        const data = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username: username.trim(), email: email.trim(), password })
        });
        if (data.access_token) {
            state.token = data.access_token;
            localStorage.setItem('token', state.token);
            await loadUser();
            render();
            return { success: true };
        }
        return { success: false, error: 'No token' };
    } catch (error) {
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
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        if (data.access_token) {
            state.token = data.access_token;
            localStorage.setItem('token', state.token);
            await loadUser();
            render();
            return { success: true };
        }
        return { success: false, error: 'No token' };
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
    } catch {
        state.user = null;
        state.token = null;
        localStorage.removeItem('token');
        return false;
    }
}

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
                <form id="auth-form">
                    <div class="form-group">
                        <label>Имя пользователя</label>
                        <input type="text" id="username" placeholder="username" required>
                    </div>
                    ${!isLogin ? `
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="email" placeholder="email@example.com" required>
                    </div>
                    ` : ''}
                    <div class="form-group">
                        <label>Пароль</label>
                        <input type="password" id="password" placeholder="••••••••" required>
                    </div>
                    <button type="submit">${isLogin ? 'Войти' : 'Зарегистрироваться'}</button>
                </form>
                <p>
                    ${isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}
                    <a href="#" onclick="navigateTo('${isLogin ? 'register' : 'login'}'); return false;">
                        ${isLogin ? 'Зарегистрироваться' : 'Войти'}
                    </a>
                </p>
                <div id="auth-error" style="display:none;color:red;"></div>
            </div>
        </div>
    `;
    document.getElementById('auth-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('auth-error');
        
        if (!username || !password) {
            errorEl.textContent = 'Заполните все поля';
            errorEl.style.display = 'block';
            return;
        }
        
        let result;
        if (isLogin) {
            result = await login(username, password);
        } else {
            const email = document.getElementById('email').value.trim();
            if (!email || !email.includes('@')) {
                errorEl.textContent = 'Укажите корректный email';
                errorEl.style.display = 'block';
                return;
            }
            result = await register(username, email, password);
        }
        if (!result.success) {
            errorEl.textContent = result.error || 'Ошибка';
            errorEl.style.display = 'block';
        } else {
            errorEl.style.display = 'none';
        }
    });
}

function renderApp() {
    app.innerHTML = `
        <div>
            <h1>🧠 Синапс</h1>
            <p>Добро пожаловать, ${state.user?.username}!</p>
            <button onclick="logout()">Выйти</button>
            <div>
                <p>Диалоги:</p>
                <button onclick="startNewChat()">+ Новый чат</button>
                <div id="dialogue-list">
                    ${state.dialogues.length === 0 ? '<p>Нет диалогов</p>' : ''}
                    ${state.dialogues.map(d => `<div onclick="loadDialogue(${d.id})">${d.title || 'Чат'}</div>`).join('')}
                </div>
            </div>
            <div>
                <div id="messages">
                    ${state.messages.length === 0 ? '<p>Начните диалог</p>' : ''}
                    ${state.messages.map(m => `<div><b>${m.role}:</b> ${m.content}</div>`).join('')}
                </div>
                <div>
                    <input type="text" id="message-input" placeholder="Сообщение..." />
                    <button onclick="sendMessage()">Отправить</button>
                </div>
            </div>
        </div>
    `;
    document.getElementById('message-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
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
    try { state.dialogues = await apiCall('/chat'); } catch { state.dialogues = []; }
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
            body: JSON.stringify({ dialogue_id: state.currentDialogueId, message: text })
        });
        state.messages.push({ role: 'assistant', content: response.response || 'Ответ' });
        render();
    } catch (error) {
        state.messages.push({ role: 'assistant', content: '⚠️ ' + error.message });
        render();
    }
}
window.sendMessage = sendMessage;

async function init() {
    console.log('INIT: API_URL =', API_URL);
    console.log('INIT: token exists =', !!state.token);
    if (state.token) {
        const ok = await loadUser();
        if (!ok) {
            state.token = null;
            localStorage.removeItem('token');
        }
    }
    if (state.user) await loadDialogues();
    render();
    console.log('INIT: complete');
}

init();

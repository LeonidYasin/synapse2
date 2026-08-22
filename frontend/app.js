document.addEventListener('DOMContentLoaded', () => {
    const messagesDiv = document.getElementById('messages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const profileContent = document.getElementById('profileContent');
    const recommendationsContent = document.getElementById('recommendationsContent');
    const loginInput = document.getElementById('loginInput');
    const passwordInput = document.getElementById('passwordInput');
    const emailInput = document.getElementById('emailInput');
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    const API_BASE = window.API_URL || 'http://localhost:8000';
    let token = localStorage.getItem('token');
    let currentUser = localStorage.getItem('username');

    if (token) {
        showLoggedIn();
        loadProfile();
        loadRecommendations();
    }

    function showLoggedIn() {
        loginInput.style.display = 'none';
        passwordInput.style.display = 'none';
        if (emailInput) emailInput.style.display = 'none';
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
        const userSpan = document.querySelector('.user-name');
        if (!userSpan) {
            const span = document.createElement('span');
            span.className = 'user-name';
            span.textContent = `👤 ${currentUser}`;
            document.querySelector('.settings').appendChild(span);
        }
    }

    function showLoggedOut() {
        loginInput.style.display = 'inline-block';
        passwordInput.style.display = 'inline-block';
        if (emailInput) emailInput.style.display = 'inline-block';
        loginBtn.style.display = 'inline-block';
        registerBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
        const userSpan = document.querySelector('.user-name');
        if (userSpan) userSpan.remove();
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        token = null;
        currentUser = null;
    }

    registerBtn.addEventListener('click', async () => {
        const username = loginInput.value.trim();
        const password = passwordInput.value.trim();
        const email = emailInput ? emailInput.value.trim() : '';
        if (!username || !password || !email) {
            alert('Введите логин, email и пароль');
            return;
        }
        try {
            const response = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    username, 
                    password, 
                    email,
                    full_name: username 
                })
            });
            if (response.ok) {
                alert('Регистрация успешна! Теперь войдите.');
            } else {
                const data = await response.json();
                alert('Ошибка: ' + (data.detail || 'Неизвестная ошибка'));
            }
        } catch (error) {
            alert('Ошибка соединения с сервером');
        }
    });

    loginBtn.addEventListener('click', async () => {
        const username = loginInput.value.trim();
        const password = passwordInput.value.trim();
        if (!username || !password) {
            alert('Введите логин и пароль');
            return;
        }
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            const response = await fetch(`${API_BASE}/auth/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
            if (response.ok) {
                const data = await response.json();
                token = data.access_token;
                currentUser = username;
                localStorage.setItem('token', token);
                localStorage.setItem('username', username);
                showLoggedIn();
                loadProfile();
                loadRecommendations();
                alert('Вход выполнен!');
            } else {
                const data = await response.json();
                alert('Ошибка: ' + (data.detail || 'Неверный логин или пароль'));
            }
        } catch (error) {
            alert('Ошибка соединения с сервером');
        }
    });

    logoutBtn.addEventListener('click', () => {
        showLoggedOut();
        profileContent.innerHTML = '<p>Войдите в систему, чтобы увидеть свой профиль.</p>';
        recommendationsContent.innerHTML = '<p>Войдите в систему для получения рекомендаций.</p>';
        messagesDiv.innerHTML = '';
    });

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        if (!token) {
            alert('Пожалуйста, войдите в систему');
            return;
        }

        addMessage('user', text);
        userInput.value = '';

        const messageElements = messagesDiv.querySelectorAll('.message');
        const messages = [];
        messageElements.forEach(el => {
            const role = el.classList.contains('user') ? 'user' : 'assistant';
            messages.push({ role, content: el.textContent });
        });

        try {
            const response = await apiRequest('/chat', 'POST', {
                messages: messages,
                api_key: apiKeyInput.value || null,
                model: 'deepseek-chat'
            });
            const data = await response.json();
            if (response.ok) {
                addMessage('assistant', data.content);
            } else {
                addMessage('assistant', 'Ошибка: ' + (data.detail || 'Неизвестная ошибка'));
            }
        } catch (error) {
            addMessage('assistant', 'Не удалось соединиться с сервером.');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function loadProfile() {
        if (!token) return;
        try {
            const response = await apiRequest('/profile', 'GET');
            if (response.ok) {
                const data = await response.json();
                profileContent.innerHTML = `<p>👤 ${data.username}</p><p>📧 ${data.email}</p>`;
            }
        } catch (error) {
            profileContent.innerHTML = '<p>Ошибка загрузки профиля</p>';
        }
    }

    async function loadRecommendations() {
        if (!token) return;
        try {
            const response = await apiRequest('/recommendations', 'GET');
            if (response.ok) {
                const data = await response.json();
                if (data.length === 0) {
                    recommendationsContent.innerHTML = '<p>Пока нет рекомендаций. Начните диалог!</p>';
                } else {
                    recommendationsContent.innerHTML = data.map(r => 
                        `<div class="recommendation">📌 ${r.title}</div>`
                    ).join('');
                }
            }
        } catch (error) {
            recommendationsContent.innerHTML = '<p>Ошибка загрузки рекомендаций</p>';
        }
    }

    function addMessage(role, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.textContent = content;
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    async function apiRequest(endpoint, method = 'GET', body = null) {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        const options = { method, headers };
        if (body) {
            options.body = JSON.stringify(body);
        }
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        return response;
    }

    analyzeBtn.addEventListener('click', async () => {
        if (!token) {
            alert('Пожалуйста, войдите в систему');
            return;
        }
        try {
            const response = await apiRequest('/profile/analyze', 'POST');
            const data = await response.json();
            if (response.ok) {
                profileContent.innerHTML = `<p>🧠 Анализ выполнен</p><p>${data.summary}</p>`;
            }
        } catch (error) {
            alert('Ошибка анализа');
        }
    });
});

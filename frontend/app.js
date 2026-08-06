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
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    const API_BASE = 'http://localhost:8000';
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
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
        // Добавляем имя пользователя в интерфейс
        const userSpan = document.createElement('span');
        userSpan.style.marginLeft = '10px';
        userSpan.textContent = `👤 ${currentUser}`;
        document.querySelector('.settings').appendChild(userSpan);
    }

    function showLoggedOut() {
        loginInput.style.display = 'inline-block';
        passwordInput.style.display = 'inline-block';
        loginBtn.style.display = 'inline-block';
        registerBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        token = null;
        currentUser = null;
        profileContent.innerHTML = '<p>Войдите в систему, чтобы увидеть свой профиль.</p>';
        recommendationsContent.innerHTML = '<p>Войдите в систему для получения рекомендаций.</p>';
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
        const options = {
            method,
            headers,
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (response.status === 401) {
            showLoggedOut();
            throw new Error('Unauthorized');
        }
        return response;
    }

    async function login() {
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

            const data = await response.json();
            if (response.ok) {
                token = data.access_token;
                currentUser = username;
                localStorage.setItem('token', token);
                localStorage.setItem('username', username);
                showLoggedIn();
                loadProfile();
                loadRecommendations();
                addMessage('assistant', `Добро пожаловать, ${username}! Я ваш ИИ-ассистент Синапс.`);
            } else {
                alert('Ошибка входа: ' + data.detail);
            }
        } catch (error) {
            alert('Ошибка соединения с сервером');
        }
    }

    async function register() {
        const username = loginInput.value.trim();
        const password = passwordInput.value.trim();
        if (!username || !password) {
            alert('Введите логин и пароль');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            if (response.ok) {
                alert('Регистрация успешна! Теперь войдите.');
            } else {
                alert('Ошибка регистрации: ' + data.detail);
            }
        } catch (error) {
            alert('Ошибка соединения с сервером');
        }
    }

    function logout() {
        showLoggedOut();
        addMessage('assistant', 'Вы вышли из системы.');
    }

    async function sendMessage() {
        if (!token) {
            alert('Пожалуйста, войдите в систему, чтобы отправлять сообщения.');
            return;
        }

        const text = userInput.value.trim();
        if (!text) return;

        addMessage('user', text);
        userInput.value = '';

        const messageElements = messagesDiv.querySelectorAll('.message');
        const messages = [];
        messageElements.forEach(el => {
            const role = el.classList.contains('user') ? 'user' : 'assistant';
            if (role === 'assistant' && el.textContent.includes('Добро пожаловать')) return;
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
                addMessage('assistant', 'Ошибка: ' + data.detail);
            }
        } catch (error) {
            if (error.message !== 'Unauthorized') {
                addMessage('assistant', 'Не удалось соединиться с сервером.');
            }
        }
    }

    async function loadProfile() {
        if (!token) return;
        try {
            const response = await apiRequest('/agent/profile');
            const data = await response.json();
            if (response.ok) {
                profileContent.innerHTML = `
                    <h4>Ключевые темы</h4>
                    ${data.topics && data.topics.length > 0 ? 
                        `<ul>${data.topics.map(t => `<li>${t}</li>`).join('')}</ul>` : 
                        '<p>Пока нет тем. Начните общение с ИИ.</p>'}
                    <p><strong>Резюме:</strong> ${data.summary || 'Нет данных'}</p>
                `;
            }
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    }

    async function loadRecommendations() {
        if (!token) return;
        try {
            const response = await apiRequest('/recommendations/suggestions');
            const data = await response.json();
            if (response.ok && data.suggestions) {
                recommendationsContent.innerHTML = `
                    <ul>${data.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>
                `;
            }

            // Также загружаем матчи
            const matchesResponse = await apiRequest('/recommendations/matches');
            const matches = await matchesResponse.json();
            if (matchesResponse.ok && matches.length > 0) {
                const matchesHtml = matches.slice(0, 3).map(m => `
                    <div style="border:1px solid #ddd;border-radius:8px;padding:10px;margin-top:10px;">
                        <strong>👤 ${m.user_id}</strong>
                        <div>Совпадение: ${m.match_score}%</div>
                        <div>Общие темы: ${m.common_topics.join(', ')}</div>
                        <div style="font-size:12px;color:#666;">${m.summary}</div>
                    </div>
                `).join('');
                recommendationsContent.innerHTML += `
                    <h4 style="margin-top:20px;">Найдены совпадения</h4>
                    ${matchesHtml}
                `;
            }
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    }

    async function analyzeDialogues() {
        if (!token) {
            alert('Пожалуйста, войдите в систему для анализа диалогов.');
            return;
        }

        const messageElements = messagesDiv.querySelectorAll('.message');
        const messages = [];
        messageElements.forEach(el => {
            const role = el.classList.contains('user') ? 'user' : 'assistant';
            messages.push({ role, content: el.textContent });
        });

        try {
            const response = await apiRequest('/agent/analyze', 'POST', {
                user_id: currentUser,
                messages: messages
            });

            const data = await response.json();
            if (response.ok) {
                profileContent.innerHTML = `
                    <h4>Ключевые темы</h4>
                    ${data.topics && data.topics.length > 0 ? 
                        `<ul>${data.topics.map(t => `<li>${t}</li>`).join('')}</ul>` : 
                        '<p>Темы не найдены</p>'}
                    <p><strong>Резюме:</strong> ${data.summary || 'Нет данных'}</p>
                    ${data.entities && data.entities.length > 0 ? 
                        `<p><strong>Сущности:</strong> ${data.entities.join(', ')}</p>` : ''}
                    ${data.intentions && data.intentions.length > 0 ? 
                        `<p><strong>Намерения:</strong> ${data.intentions.join(', ')}</p>` : ''}
                `;
                loadRecommendations();
                addMessage('assistant', '✅ Профиль успешно обновлён!');
            } else {
                alert('Ошибка анализа: ' + data.detail);
            }
        } catch (error) {
            if (error.message !== 'Unauthorized') {
                alert('Сервер недоступен');
            }
        }
    }

    // Обработчики событий
    loginBtn.addEventListener('click', login);
    registerBtn.addEventListener('click', register);
    logoutBtn.addEventListener('click', logout);
    sendBtn.addEventListener('click', sendMessage);
    analyzeBtn.addEventListener('click', analyzeDialogues);

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Приветственное сообщение для новых пользователей
    if (!token) {
        addMessage('assistant', '👋 Добро пожаловать в Синапс! Войдите или зарегистрируйтесь, чтобы начать общение с ИИ-ассистентом.');
    }
});

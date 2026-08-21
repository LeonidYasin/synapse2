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

    // API_BASE определяется через переменную окружения или через window.API_URL
    // Если ничего не задано — используем localhost
    const API_BASE = window.API_URL || 'http://localhost:8000';
    let token = localStorage.getItem('token');
    let currentUser = localStorage.getItem('username');

    // Эмодзи для категорий
    const categoryEmojis = {
        'покупка': '🛒',
        'продажа': '💰',
        'услуги': '🚕',
        'доставка': '📦',
        'работа': '💼',
        'партнёрство': '🤝',
        'недвижимость': '🏠',
        'креатив': '🎨',
        'экспертиза': '🧠',
        'личное': '💞',
        'обучение': '📚',
        'unknown': '🔍'
    };

    const intentionLabels = {
        'buy': '🔍 Ищет купить',
        'sell': '💰 Предлагает продать',
        'find': '🔎 Ищет найти',
        'offer': '📢 Предлагает услугу',
        'unknown': '💬 Общий разговор'
    };

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

    function addMessage(role, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.textContent = content;
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    registerBtn.addEventListener('click', async () => {
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
            const response = await apiRequest('/agent/profile');
            if (response.ok) {
                const data = await response.json();
                const topics = data.topics || [];
                const category = data.category || 'unknown';
                const intention = data.intention || 'unknown';
                const location = data.location || null;
                const budget = data.budget || null;
                const urgency = data.urgency || null;

                let html = '';
                html += `<div style="background:#f0f4ff;padding:12px;border-radius:12px;margin-bottom:12px;">`;
                html += `<strong>${categoryEmojis[category] || '🔍'} Категория:</strong> ${category || 'Не определена'}<br>`;
                html += `<strong>${intentionLabels[intention] || '💬'}</strong>`;
                if (location) html += `<br>📍 <strong>Локация:</strong> ${location}`;
                if (budget) html += `<br>💰 <strong>Бюджет:</strong> ${budget}`;
                if (urgency) html += `<br>⏱️ <strong>Срочность:</strong> ${urgency}`;
                html += `</div>`;

                if (topics.length > 0) {
                    html += `<h4>📌 Ключевые темы</h4><ul>`;
                    topics.forEach(t => { html += `<li>${t}</li>`; });
                    html += `</ul>`;
                }

                html += `<p><strong>📝 Резюме:</strong> ${data.summary || 'Профиль формируется...'}</p>`;

                profileContent.innerHTML = html;
            }
        } catch (error) {
            profileContent.innerHTML = '<p>Ошибка загрузки профиля</p>';
        }
    }

    async function loadRecommendations() {
        if (!token) return;
        try {
            const response = await apiRequest('/recommendations/matches');
            if (response.ok) {
                const data = await response.json();
                if (data.length === 0) {
                    recommendationsContent.innerHTML = '<p>Пока нет совпадений. Продолжайте общаться с ИИ.</p>';
                } else {
                    let html = '<h4>🔗 Совпадения</h4>';
                    data.slice(0, 5).forEach(m => {
                        const cat = m.category || 'unknown';
                        html += `
                            <div style="border-bottom:1px solid #eee;padding:8px 0;">
                                <strong>${categoryEmojis[cat] || '👤'} ${m.user_id}</strong>
                                — ${m.match_score}%<br>
                                <small>📌 ${(m.common_topics || []).join(', ') || 'Общие интересы'}</small>
                            </div>
                        `;
                    });
                    recommendationsContent.innerHTML = html;
                }
            }
        } catch (error) {
            recommendationsContent.innerHTML = '<p>Ошибка загрузки рекомендаций</p>';
        }
    }

    analyzeBtn.addEventListener('click', async () => {
        if (!token) {
            alert('Пожалуйста, войдите в систему');
            return;
        }
        const messageElements = messagesDiv.querySelectorAll('.message');
        const messages = [];
        messageElements.forEach(el => {
            const role = el.classList.contains('user') ? 'user' : 'assistant';
            messages.push({ role, content: el.textContent });
        });

        if (messages.length === 0) {
            alert('Нет сообщений для анализа. Напишите что-нибудь в чат.');
            return;
        }

        analyzeBtn.textContent = '⏳ Анализирую...';
        analyzeBtn.disabled = true;

        try {
            const response = await apiRequest('/agent/analyze', 'POST', {
                user_id: currentUser,
                messages: messages
            });
            if (response.ok) {
                const data = await response.json();
                const topics = data.topics || [];
                const category = data.category || 'unknown';
                const intention = data.intention || 'unknown';
                const location = data.location || null;
                const budget = data.budget || null;
                const urgency = data.urgency || null;

                let html = '';
                html += `<div style="background:#f0f4ff;padding:12px;border-radius:12px;margin-bottom:12px;">`;
                html += `<strong>${categoryEmojis[category] || '🔍'} Категория:</strong> ${category || 'Не определена'}<br>`;
                html += `<strong>${intentionLabels[intention] || '💬'}</strong>`;
                if (location) html += `<br>📍 <strong>Локация:</strong> ${location}`;
                if (budget) html += `<br>💰 <strong>Бюджет:</strong> ${budget}`;
                if (urgency) html += `<br>⏱️ <strong>Срочность:</strong> ${urgency}`;
                html += `</div>`;

                if (topics.length > 0) {
                    html += `<h4>📌 Ключевые темы</h4><ul>`;
                    topics.forEach(t => { html += `<li>${t}</li>`; });
                    html += `</ul>`;
                }

                html += `<p><strong>📝 Резюме:</strong> ${data.summary || 'Профиль формируется...'}</p>`;

                profileContent.innerHTML = html;
                alert('✅ Анализ завершён! Профиль обновлён.');
                loadRecommendations();
            } else {
                const data = await response.json();
                alert('Ошибка анализа: ' + (data.detail || 'Неизвестная ошибка'));
            }
        } catch (error) {
            alert('Сервер недоступен');
        } finally {
            analyzeBtn.textContent = 'Анализировать';
            analyzeBtn.disabled = false;
        }
    });
});

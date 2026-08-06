document.addEventListener('DOMContentLoaded', () => {
    const messagesDiv = document.getElementById('messages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const profileContent = document.getElementById('profileContent');

    const API_BASE = 'http://localhost:8000';

    function addMessage(role, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.textContent = content;
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        addMessage('user', text);
        userInput.value = '';

        const messageElements = messagesDiv.querySelectorAll('.message');
        const messages = [];
        messageElements.forEach(el => {
            const role = el.classList.contains('user') ? 'user' : 'assistant';
            messages.push({ role, content: el.textContent });
        });

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: messages,
                    api_key: apiKeyInput.value || null,
                    model: 'deepseek-chat'
                })
            });
            const data = await response.json();
            if (response.ok) {
                addMessage('assistant', data.content);
            } else {
                addMessage('assistant', 'Ошибка: ' + data.detail);
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

    analyzeBtn.addEventListener('click', async () => {
        const messageElements = messagesDiv.querySelectorAll('.message');
        const messages = [];
        messageElements.forEach(el => {
            const role = el.classList.contains('user') ? 'user' : 'assistant';
            messages.push({ role, content: el.textContent });
        });

        try {
            const response = await fetch(`${API_BASE}/agent/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: 'demo-user',
                    messages: messages
                })
            });
            const data = await response.json();
            if (response.ok) {
                profileContent.innerHTML = `
                    <h4>Ключевые темы</h4>
                    <ul>${data.topics.map(t => `<li>${t}</li>`).join('')}</ul>
                    <p><strong>Резюме:</strong> ${data.summary}</p>
                `;
            } else {
                alert('Ошибка анализа: ' + data.detail);
            }
        } catch (error) {
            alert('Сервер недоступен');
        }
    });
});

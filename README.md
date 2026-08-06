# Синапс — ИИ-платформа для поиска связей

ИИ-ассистент, который анализирует ваши диалоги и находит связи с другими людьми.

## Быстрый старт

### Локальный запуск

1. Клонируйте репозиторий
```bash
git clone https://github.com/LeonidYasin/synapse2.git
cd synapse2
```

2. Создайте и активируйте виртуальное окружение
```bash
cd backend
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или venv\Scripts\activate для Windows
```

3. Установите зависимости
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в папке `backend` на основе `.env.example`
```bash
cp .env.example .env
# Отредактируйте .env, добавьте ваш DEEPSEEK_API_KEY
```

5. Запустите бэкенд
```bash
python run.py
```

6. Откройте `frontend/index.html` в браузере

## Деплой на Render

### Способ 1: Через render.yaml (автоматический)

1. Форкните этот репозиторий на GitHub
2. Зайдите на [Render.com](https://render.com) и нажмите "New + → Blueprint"
3. Подключите ваш GitHub репозиторий
4. Render автоматически обнаружит `render.yaml` и предложит создать все сервисы
5. Введите ваш `DEEPSEEK_API_KEY` в настройках сервиса
6. Нажмите "Apply"

### Способ 2: Вручную через веб-интерфейс

#### Бэкенд (Web Service)

1. На Render нажмите "New + → Web Service"
2. Подключите репозиторий
3. Настройки:
   - **Name**: `synapse-api`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
4. Добавьте переменные окружения:
   - `DEEPSEEK_API_KEY` = ваш ключ
   - `SECRET_KEY` = сгенерируйте случайную строку
5. Нажмите "Create Web Service"

#### Фронтенд (Static Site)

1. На Render нажмите "New + → Static Site"
2. Подключите репозиторий
3. Настройки:
   - **Name**: `synapse-frontend`
   - **Build Command**: (оставьте пустым, т.к. у нас уже готовые файлы)
   - **Publish Directory**: `frontend`
4. Нажмите "Create Static Site"

#### База данных PostgreSQL

1. На Render нажмите "New + → PostgreSQL"
2. Настройки:
   - **Name**: `synapse-db`
   - **Plan**: `Free`
3. Нажмите "Create Database"
4. Скопируйте строку подключения и добавьте как `DATABASE_URL` в переменные бэкенда

## API Эндпоинты

- `POST /auth/register` — регистрация
- `POST /auth/token` — получение JWT токена
- `GET /auth/me` — информация о текущем пользователе
- `POST /chat` — чат с ИИ (требуется аутентификация)
- `POST /chat/public` — публичный чат (без аутентификации)
- `POST /agent/analyze` — анализ диалогов
- `GET /agent/profile` — получение профиля
- `GET /recommendations/matches` — поиск совпадений
- `GET /recommendations/suggestions` — рекомендации

## 🎯 Гранты для проекта

Мы активно подаём заявки на грантовые программы для ИИ-стартапов. Это позволит нам получить бесплатные ресурсы (токены для LLM, GPU, облачный хостинг) и ускорить разработку.

### Приоритетные гранты

| Грант | Сумма | Что дают | Статус |
|-------|-------|----------|--------|
| [Modal for Startups](https://modal.com/startups) | $500–$50,000 | GPU для ML/AI | 🔄 В процессе |
| [Google Cloud Startup](https://startup.google.com/cloud/) | $2,000–$350,000 | Облачные сервисы, AI/ML | ⏳ Планируется |
| [Groq for Startups](https://groq.com/groq-for-startups) | $10,000 | Инференс LLM | ⏳ Планируется |
| [Microsoft for Startups](https://www.microsoft.com/en-us/startups) | $1,000–$5,000 | Azure, AI, базы данных | ⏳ Планируется |

**Подробности:** см. [GRANTS.md](./GRANTS.md)

## Технологии

- **Backend**: FastAPI, SQLAlchemy, JWT
- **LLM**: DeepSeek API (планируем Groq и Modal)
- **Database**: SQLite (локально) / PostgreSQL (продакшен)
- **Frontend**: Vanilla JS, HTML5, CSS3

## Лицензия

MIT

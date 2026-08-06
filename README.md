# Синапс — ИИ-платформа для поиска связей

ИИ-ассистент, который анализирует ваши диалоги и находит связи с другими людьми.

## Возможности

- 🔐 **Аутентификация** — регистрация и вход через JWT
- 💬 **Чат с ИИ** — общение с DeepSeek через собственный или общий API-ключ
- 🤖 **Агент-сканер** — анализ диалогов для извлечения тем, сущностей и намерений
- 🔗 **Рекомендации** — поиск пользователей с похожими интересами
- 💳 **Подписки** — интеграция с Stripe для монетизации
- 🌓 **Тёмная тема** — удобный интерфейс с переключением режимов
- 📱 **Адаптивный дизайн** — работает на всех устройствах

## Быстрый старт

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/LeonidYasin/synapse2.git
cd synapse2
```

### 2. Настройте бэкенд
```bash
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

### 3. Создайте файл `.env` в папке `backend`:
```env
DEEPSEEK_API_KEY=ваш_ключ_DeepSeek
SECRET_KEY=секретная_строка

# Опционально: для платежей
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 4. Запустите бэкенд
```bash
python run.py
```

### 5. Откройте фронтенд
Просто откройте `frontend/index.html` в браузере или используйте Live Server.

## Структура проекта

```
synapse/
├── backend/
│   ├── app/
│   │   ├── agent/          # Агент-сканер
│   │   ├── routers/        # API роутеры
│   │   ├── utils/          # Вспомогательные функции
│   │   ├── auth.py         # JWT аутентификация
│   │   ├── config.py       # Конфигурация
│   │   ├── database.py     # Модели базы данных
│   │   └── main.py         # Точка входа
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md
```

## API Эндпоинты

### Аутентификация
- `POST /auth/register` — регистрация
- `POST /auth/token` — вход (JWT)
- `GET /auth/me` — получить текущего пользователя

### Чат
- `POST /chat` — отправка сообщения (требуется аутентификация)
- `POST /chat/public` — публичный чат (без аутентификации)

### Агент
- `POST /agent/analyze` — анализ диалогов
- `GET /agent/profile` — получение профиля

### Рекомендации
- `GET /recommendations/matches` — поиск совпадений
- `GET /recommendations/suggestions` — предложения по улучшению

### Платежи
- `GET /payments/prices` — список цен
- `POST /payments/create-subscription` — создание подписки
- `GET /payments/status` — статус подписки
- `POST /payments/cancel` — отмена подписки

## Деплой на Render

1. Залейте код на GitHub
2. Создайте Web Service на Render.com
3. Укажите:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
   - **Root Directory**: `backend`
4. Добавьте переменные окружения из `.env`

## Технологии

- **Бэкенд**: Python, FastAPI, SQLAlchemy, JWT, Stripe
- **Фронтенд**: HTML5, CSS3, JavaScript (Vanilla)
- **ИИ**: DeepSeek API, LangChain (планируется)
- **База данных**: SQLite (разработка), PostgreSQL (продакшн)

## Лицензия

MIT

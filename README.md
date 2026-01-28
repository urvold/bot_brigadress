# BrigAdress Telegram Showcase (Bot + WebApp + API + Postgres)

Это демонстрационный проект под **БригАдрес**: Telegram-бот + WebApp (Mini App) + FastAPI + PostgreSQL.  
Цель — показать клиентам «что вы умеете»: авторизация через Telegram, контент из сайта, заявки в базу, админка, уведомления.

## Что внутри

- **Telegram Bot (aiogram 3)**  
  - `/start` — меню
  - заявки от клиента и заявки от подрядчика (FSM)
  - отправка PDF-документов (чек-листы/оферта)
  - уведомления админу о новых заявках

- **WebApp (Telegram Mini App)**  
  - вкладки: FAQ / Документы / Проекты / Оставить заявку / Админка
  - авторизация через `initData`, проверка на backend
  - создание заявки в PostgreSQL
  - админка: список заявок, смена статуса, экспорт CSV

- **Backend (FastAPI)**  
  - API для контента и заявок
  - PostgreSQL + SQLAlchemy (async)
  - авто-сеед из контента сайта (FAQ/Документы/Проекты)

## Быстрый старт (локально)

1) Создай бота через @BotFather и возьми токен.

2) Заполни переменные окружения:

- Скопируй `.env.example` → `.env`
- Укажи `BOT_TOKEN` и `ADMIN_TELEGRAM_IDS`

3) Запусти:

```bash
docker compose up --build
```

- API: http://localhost:8000  
- WebApp: http://localhost:8000/webapp/ (для локального просмотра в браузере)

> Для запуска WebApp внутри Telegram нужен **публичный HTTPS домен** (например, через VPS + reverse proxy или Cloudflare Tunnel).

## Деплой для Telegram WebApp

Telegram WebApp **требует HTTPS**. В README ниже есть подсказки для продакшн-развертывания.

## Структура

- `backend/` — FastAPI + DB + статика
- `bot/` — aiogram бот
- `seed_content.json` — контент, извлечённый из сайта BrigAdress (из архива)

---

Если захочешь, можно легко превратить этот шаблон в коммерческий продукт: добавь каталог подрядчиков, рейтинг, фото-галерею проектов, интеграции с CRM.

## Deploy (Railway)
See `RAILWAY_DEPLOY.md`.

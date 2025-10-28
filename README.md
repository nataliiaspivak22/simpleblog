# 📝 Simple Blog + Comments

## Опис проєкту
Цей проєкт реалізує простий блог із підтримкою постів та коментарів.  
Варіант реалізації: **In-memory storage** (дані зберігаються в пам'яті, без бази даних).  

**Схема:**

- **posts**: `id`, `title`, `body`, `created_at`
- **comments**: `id`, `post_id`, `author`, `content`, `created_at`

Підтримувані операції:  

- CRUD для постів (створення, читання, оновлення, видалення)  
- Додавання та видалення коментарів  
- Сторінкування при отриманні списку постів  

---

## Інструкції запуску

1. Клонувати репозиторій:

```bash
git clone <repository-url>
cd <repository-folder>
```

2. Запустити сервіси через Docker Compose:

```bash
docker compose up --build
```

---

## URL-и сервісів

- **Frontend (Streamlit):** [http://localhost:8501](http://localhost:8501)  
- **API docs (FastAPI Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints

### **Posts**

| Method | Endpoint          | Опис                       |
|--------|-----------------|----------------------------|
| GET    | `/posts`         | Список постів (з пагінацією) |
| POST   | `/posts`         | Створити новий пост         |
| GET    | `/posts/{id}`    | Отримати пост по ID         |
| PUT    | `/posts/{id}`    | Оновити пост по ID          |
| DELETE | `/posts/{id}`    | Видалити пост по ID         |

**Приклад створення поста:**

```bash
POST /posts
Content-Type: application/json

{
  "title": "Мій перший пост",
  "body": "Це тіло мого поста"
}
```

**Приклад відповіді:**

```json
{
  "id": 1,
  "title": "Мій перший пост",
  "body": "Це тіло мого поста",
  "created_at": "2025-10-28T09:01:54.676475",
  "comments": []
}
```

---

### **Comments**

| Method | Endpoint                        | Опис                       |
|--------|---------------------------------|----------------------------|
| GET    | `/posts/{post_id}/comments`     | Список коментарів поста    |
| POST   | `/posts/{post_id}/comments`     | Додати коментар            |
| GET    | `/posts/{post_id}/comments/{id}` | Отримати коментар по ID   |
| PUT    | `/posts/{post_id}/comments/{id}` | Оновити коментар по ID    |
| DELETE | `/posts/{post_id}/comments/{id}` | Видалити коментар по ID   |

**Приклад створення коментаря:**

```bash
POST /posts/1/comments
Content-Type: application/json

{
  "author": "Ivan",
  "content": "Це мій перший коментар"
}
```

**Приклад відповіді:**

```json
{
  "id": 1,
  "post_id": 1,
  "author": "Ivan",
  "content": "Це мій перший коментар",
  "created_at": "2025-10-28T09:15:32.123456"
}
```

---

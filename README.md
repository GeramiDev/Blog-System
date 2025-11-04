# 📝 Blog API with DRF and Docker

A complete backend REST API for a blog platform built with **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **Docker Compose**.  
It supports user authentication (JWT), blog management, comments, likes, and ratings.

---
## 🆕 Latest Changes
- Optimization in Apps Blogs and Comments
- Adding the ability to change and delete the profile avatar
- Change of authentication system for forget password
- Change user email with 6-digit authentication code
---

## 🚀 Features

✅ **Authentication & Authorization**
- JWT-based authentication (`djangorestframework-simplejwt`)
- User registration, login, logout, and token refresh
- Forgot password (send email with 6-digit code)

✅ **User Profile & Password Management**
- View user profile
- Change password (profile)
- Change Email
- Change Avatar
- Edit profile information (name, bio, etc.)

✅ **Blog System**
- Create, edit, delete posts (only authors)
- Publicly accessible list & detail views
- Like and rate posts

✅ **Comments System**
- Nested comments (reply support)
- Edit/Delete permissions for authors only

✅ **Dockerized Setup**
- Django + PostgreSQL in containers
- Ready-to-deploy configuration

✅ **Testing**
- Unit tests for users, blogs, and comments apps

---

## 🧱 Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | Django 5 + DRF |
| Database | PostgreSQL |
| Auth | JWT (SimpleJWT) |
| Containerization | Docker & Docker Compose |
| Documentation | drf-yasg (Swagger) |
| Testing | Django REST Framework APITestCase |
| Notifications | Django Email Backend (SMTP) |


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
   git clone http://185.130.78.44/devops-templates/blogfa.git
   cd blogfa
```

---
### 2️⃣ Email Config
Go to the config folder, open the setting.py file,
and in the Email Setting section, enter the following details
according to your chosen service.(This sample is for the Gmail service)
```commandline
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'Your Email'
EMAIL_HOST_PASSWORD = 'App Password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER Run with Docker Compose
```
---


### 3️⃣ Run with Docker Compose
Build and start all services:
```bash
   docker compose up --build
```

Once started:
- Backend: http://127.0.0.1:8000  
- Swagger docs: http://127.0.0.1:8000/swagger/

---

### 4️⃣ Create Superuser
```bash
   docker compose exec web python manage.py createsuperuser
```

---
## 🧩 API Endpoints

---

### 🔐 Authentication

| Method | Endpoint                            | Description                                                   |
|--------|-------------------------------------|---------------------------------------------------------------|
| `POST` | `/api/auth/register/`               | Register a new user                                           |
| `POST` | `/api/auth/login/`                  | Login and receive JWT tokens                                  |
| `POST` | `/api/auth/logout/`                 | Logout user                                                   |
| `POST` | `/api/auth/token/refresh/`          | Refresh access token                                          |
| `PUT`  | `/api/auth/profile/`                | Edit user profile                                             |
| `GET`  | `/api/auth/profile/`                | View user profile                                             |
| `PUT`  | `/api/auth/change-password/`        | Change password in the profile                                |
| `POST` | `/api/auth/email/change/`           | Send a request to change the email                            |
| `POST` | `/api/auth/email/verify/`           | Email verification with code                                  |
| `POST` | `/api/auth/forget-password/`        | Send request to reset password (Email verification with code) |
| `POST` | `/api/auth/forget-password/change/` | Change password and verify with code                          |


---

### 📰 Blog Posts
| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/api/blogs/` | List all posts |
| `POST` | `/api/blogs/` | Create new post |
| `GET` | `/api/blogs/{id}/` | Retrieve a post |
| `PUT` | `/api/blogs/{id}/` | Update a post |
| `DELETE` | `/api/blogs/{id}/` | Delete a post |
| `POST` | `/api/blogs/{id}/like/` | Like a post |
| `POST` | `/api/blogs/{id}/rate/` | Rate a post |


---

### 💬 Comments
| Method | Endpoint                         | Description                                     |
|--------|----------------------------------|-------------------------------------------------|
| `GET` | `/api/blogs/{id}/comments/`      | List comments for a post<br/>(id = BlogPost Id) |
| `POST` | `/api/blogs/{id}/comments/`      | Create a new comment<br/>(id = BlogPost Id)     |
| `PUT` | `/api/blogs/comments/{id}/crud/`     | Edit or delete comment<br/>(id = Comment Id)    |
| `DELETE` | `/api/blogs/comments/{id}/crud/` | Delete specific comment<br/>(id = Comment Id)                         |


---

## 🧪 Running Tests

Run tests inside the Docker container:
```bash
docker compose exec web python manage.py test
```

Example output:
```
Ran 8 tests in 11.045s
OK
```

---

## 🧰 Development (without Docker)

### 1️⃣ Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # on Linux/Mac
venv\Scripts\activate     # on Windows
pip install -r requirements.txt
```

### 2️⃣ Run migrations
```bash
python manage.py migrate
```

### 3️⃣ Start local server
```bash
python manage.py runserver
```
---

### 🔐 Users App

---
### 1️⃣ Register:

```bash
curl -X PATCH http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username":"UserTest"
    "first_name": "TestName",
    "last_name": "TestFamily",
    "email": "Test@example.com",
    "password":"12345!Ab",
    "password2":"12345!Ab"
    }'
```
#### Response Example:
```bash
{
  "username":"UserTest",
  "email":"Test@example.com",
  "first_name":"TestName",
  "last_name":"TestFamily"
}
```
---
### 2️⃣ Forget Password(request):

```bash
curl -X POST http://127.0.0.1:8000/api/auth/forget-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "Test@example.com",
    }'
```
#### Response Example:
```bash
{
  "message":"The password recovery code has been sent to your email"
}
```
---
### 3️⃣ Forget Password(verify):

```bash
curl -X POST http://127.0.0.1:8000/api/auth/forget-password/change/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "Test@example.com",
    "code": "<CODE>",
    "new_password": "new12345!Ab",
    "confirm_password": "new12345!Ab"
    }'
```
#### Response Example:
```bash
{
  "message":"Your password has been successfully changed"
}
```
---
### 4️⃣ Login:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "UserTest",
    "password": "new12345!Ab"
    }'
```
#### Response Example:
```bash
{
  "refresh":"<REFRESH_TOKEN>",
  "access":"<ACCESS_TOKEN>"
}
```
---
### 5️⃣ JWT Refresh Token Flow:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "refresh": "<REFRESH_TOKEN>"
    }'
```
#### Response Example:
```bash
{
  "access":"<ACCESS_TOKEN>",
  "refresh":"<REFRESH_TOKEN>"
}
```
---
### 6️⃣ View Profile:

```bash
curl -X GET http://127.0.0.1:8000/api/auth/profile/<USER_ID>/ \
```
#### Response Example:
```bash
{
  "id":<USER_ID>,
  "first_name":"TestName",
  "last_name":"TestFamily",
  "email":"Test@example.com",
  "bio":"This is a bio about me"  ,
  "avatar":"http://127.0.0.1:8000/media/avatars/default.png"
}
```
---
### 7️⃣ Update Profile:
```bash
curl -X PATCH http://127.0.0.1:8000/api/auth/profile/<USER_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "bio:This is new Bio" \
  -F "first_name:New First Name" \
  -F "last_name:New Last Name" \
  -F "avatar=@/absolute/path/to/avatar.jpg"
```
#### Response Example:
```bash
{
  "id":<USER_ID>,
  "first_name":"New First Name",
  "last_name":"New Last Name",
  "email":"Test@example.com",
  "bio":"This is new Bio",
  "avatar":"http://127.0.0.1:8000/media/avatars/user_4/avatar.jpg"}
}
```
---
### 8️⃣ Delete Avatar:
```bash
curl -X PATCH http://127.0.0.1:8000/api/auth/profile/<USER_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
  "remove_avatar": True
  }'
```
#### Response Example:
###### ( By removing the avatar, it changed to default )
```bash
{
  "id":<USER_ID>,
  "first_name":"New First Name",
  "last_name":"New Last Name",
  "email":"Test@example.com",
  "bio":"This is new Bio",
  "avatar":"http://127.0.0.1:8000/media/avatars/default.png"
}
```

---
### 9️⃣ Change Password:
```bash
curl -X PUT http://127.0.0.1:8000/api/auth/change-password/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password":"new12345!Ab",
    "new_password":"NewPass1!",
    "confirm_password":"NewPass1!"
    }'
```
#### Response Example:
```bash
{
  "message": "Password Changed"
}
```
---
### 🔟 Change Email(request):
```bash
curl -X POST http://127.0.0.1:8000/api/auth/email/change/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_email":"new@example.com"
    }'
```
#### Response Example:
```bash
{
  "message": "The verification code has been sent to the new email"
}
```
---
### 1️⃣1️⃣ Change Email(verify):
```bash
curl -X POST http://127.0.0.1:8000/api/auth/email/verify/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_email":"new@example.com",
    "code":"<CODE>"
    }'
```
#### Response Example:
```bash
{
  
  "message": "Your email has been successfully changed"
}
```
---
### 1️⃣2️⃣ Logout:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh":"<REFRESH_TOKEN>"
    }'
```
#### Response Example:
```bash
{
  "detail": "Logout was successful"
}
```
---

### 📰 Blogs App

---
### 1️⃣ Create Blog Post:
```bash
curl -X POST http://127.0.0.1:8000/api/blogs/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"title1",
    "content":"content1"
    }'
```
#### Response Example:
```bash
{
  "id": 1,
  "title": "title1",
  "content": "content1",
  "author": "UserTest",
  "created_at": "2025-10-19T07:30:32.339149Z",
  "updated_at": "2025-10-19T07:30:32.339122Z",
  "total_likes": 0,
  "average_rating": null
}
```
---
### 2️⃣ View All Blog Posts:
```bash
curl -X GET http://127.0.0.1:8000/api/blogs/ \
```
#### Response Example:
```bash
[
  {
    "id": <POST_ID>,
    "title": "title1",
    "content": "content1",
    "author": "UserTest",
    "created_at": "2025-10-19T07:30:32.339149Z",
    "updated_at": "2025-10-19T07:30:32.339122Z",
    "total_likes": 0,
    "average_rating": null
  },
  {
    "id": <POST_ID>,
    "title": "title2",
    "content": "content2",
    "author": "OtherUser",
    "created_at": "2025-10-19T07:37:37.235137Z",
    "updated_at": "2025-10-19T07:37:37.235137Z",
    "total_likes": 0,
    "average_rating": null
  }
]
```
---
### 3️⃣ View Selected Blog Post:
```bash
curl -X GET http://127.0.0.1:8000/api/blogs/<POST_ID>/ \
```
#### Response Example:
```bash
{
  "id": <POST_ID>,
  "title": "title1",
  "content": "content1",
  "author": "UserTest",
  "created_at": "2025-10-19T07:30:32.339149Z",
  "updated_at": "2025-10-19T07:30:32.339122Z",
  "total_likes": 0,
  "average_rating": null
}
```
---
### 4️⃣ Update Blog Post:
```bash
curl -X PUT http://127.0.0.1:8000/api/blogs/<POST_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "UpdateTitle",
    "content": "UpdateContent"
    }'
```
#### Response Example:
```bash
{
  "id": <POST_ID>,
  "title": "UpdateTitle",
  "content": "UpdateContent",
  "author": "UserTest",
  "created_at": "2025-10-19T07:30:32.339149Z",
  "updated_at": "2025-10-19T07:49:26.200218Z",
  "total_likes": 0,
  "average_rating": null
}
```
---
### 5️⃣ Like Blog Post:
```bash
curl -X POST http://127.0.0.1:8000/api/blogs/<POST_ID>/like/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" 
```
#### Response Example:
```bash
{
  "message": "Liked"
}
```
---
### 6️⃣ Rate Blog Post:
```bash
curl -X POST http://127.0.0.1:8000/api/blogs/<POST_ID>/rate/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "score":<1-5>
    }'
```
#### Response Example:
```bash
{
  "message": "Rating saved",
  "score": 4
}
```
---
### 7️⃣ Delete Blog Post:
```bash
curl -X DELETE http://127.0.0.1:8000/api/blogs/<POST_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" 
```
#### Response Example:
```bash
{
  "message": "Blog Post Deleted"
}
```
---
### 💬 Comments App

---
### 1️⃣ Add Comment For Blog Post:
```bash
curl -X POST http://127.0.0.1:8000/api/blogs/<POST_ID>/comments/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "blog":<POST_ID>,
    "content":"comment1"
    }'
```
#### Response Example:
```bash
{
    "id": <COMMENT_ID>,
    "blog": <POST_ID>,
    "author": "UserTest",
    "content": "comment1",
    "parent": null,
    "replies": [],
    "created_at": "2025-10-19T08:37:32.029713Z"
}
```
---
### 2️⃣ Nested Comments For Blog Post:
```bash
curl -X POST http://127.0.0.1:8000/api/blogs/<POST_ID>/comments/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "blog":<POST_ID>,
    "parent":<COMMENT_ID>,
    "content":"reply comment"
    }'
```
#### Response Example:
```bash
{
    "id": 2,
    "blog": <POST_ID>,
    "author": "UserTest",
    "content": "reply comment",
    "parent": 1,
    "replies": [],
    "created_at": "2025-10-19T08:44:22.671423Z"
}
```
---
### 3️⃣ View Comments For Blog Post:
```bash
curl -X GET http://127.0.0.1:8000/api/blogs/<POST_ID>/comments/ 
```
#### Response Example:
```bash
[
  {
    "id": 1,
    "blog": <POST_ID>,
    "author": "UserTest",
    "content": "comment1",
    "parent": null,
    "replies": [
        {
          "id": 2,
          "blog": <POST_ID>,
          "author": "OtherUser",
          "content": "reply comment",
          "parent": 1,
          "replies": [],
          "created_at": "2025-10-19T08:44:22.671423Z"
        }
    ],
    "created_at": "2025-10-19T08:37:32.029713Z"
  }
]
```
---
### 4️⃣ Update Comment:
```bash
curl -X PUT http://127.0.0.1:8000/api/blogs/comments/<COMMENT_ID>/crud/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "blog":<POST_ID>,
    "content":"Update comment"
    }'
```
#### Response Example:
```bash
{
    "id": <COMMENT_ID>,
    "blog": <POST_ID>,
    "author": "UserTest",
    "content": "Update comment",
    "parent": 1
    "replies": [],
    "created_at": "2025-10-19T08:44:22.671423Z"
}
```
---
### 5️⃣ Delete Blog Post:
```bash
curl -X DELETE http://127.0.0.1:8000/api/blogs/comments/<COMMENT_ID>/crud/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "blog":<POST_ID>
    }'
```
#### Response Example:
```bash
{
  "message": "Comment Deleted"
}
```

---

## 🧾 Project Structure
```
blog-api/
│
├── blogs/                 # Blog app (posts, likes, ratings)
├── comments/              # Comments & replies app
├── users/                 # Authentication & profile & password management
├── media/                 # Default avatar for profile and saved user avatars
│
├── config/                # Django settings, URLs, WSGI
├── manage.py
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 🧠 Permissions Summary

| Role | Action                                                                             | Allowed |
|------|------------------------------------------------------------------------------------|----------|
| Guest | Read posts/comments<br/>View Profile                                               | ✅ |
| Authenticated User | Create/Edit own posts/comments<br/>View and Edit Profile <br/> Like and Rate posts | ✅ |
| Admin | Full access                                                                        | ✅ |

---

## 🧩 API Docs
Swagger UI:  
👉 **[`http://127.0.0.1:8000/swagger/`](http://127.0.0.1:8000/swagger/)**  
ReDoc UI:  
👉 **[`http://127.0.0.1:8000/redoc/`](http://127.0.0.1:8000/redoc/)**  

---


## 🐳 Docker Commands Cheat Sheet

| Command | Description |
|----------|-------------|
| `docker compose up` | Start all containers |
| `docker compose down` | Stop and remove containers |
| `docker compose exec web python manage.py test` | Run tests |
| `docker compose exec web python manage.py createsuperuser` | Create admin |
| `docker compose logs -f web` | View live logs |

---

## 📄 License
MIT License © 2025 — Developed by [M.H Gerami](https://github.com/GeramiDev)

---

## 💡 Contact
For questions or collaboration:
📧 **GeramiDev@gmail.com**  
💼 [LinkedIn Profile](https://linkedin.com/in/geramidev)

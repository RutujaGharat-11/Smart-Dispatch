# 🚀 SmartDispatch – Intelligent Resource Allocation System

SmartDispatch is a full-stack web application designed to optimize public resource allocation using Operating System scheduling concepts. It simulates real-world dispatch systems (like police/fire services) with role-based access, dynamic resource management, and algorithm-driven task assignment.

🔗 **Live Demo:** https://smart-dispatch-six.vercel.app  

---

## 📌 Problem Statement

Efficient allocation of limited public resources (e.g., emergency services) is a critical challenge. Traditional systems may suffer from delays, unfair prioritization, or resource starvation.

SmartDispatch solves this by:
- Applying scheduling algorithms  
- Ensuring fair resource distribution  
- Minimizing request wait times  

---

## 🧠 Key Features

- 🔐 Role-based authentication (**User / Admin**)  
- 📝 Request submission & tracking system  
- 📊 Admin dashboard for monitoring requests  
- 🚓 Resource management (Available / Unavailable)  
- ⚙️ Algorithm-driven scheduling system  
- 🔄 Anti-starvation mechanism for fairness  
- 🌐 Full-stack deployment (Vercel + Render)  

---

## 🧠 Scheduling Algorithm

The core of this system is a scheduler inspired by Operating System concepts:

- Priority-based scheduling  
- Anti-starvation handling  
- Dynamic task-resource assignment  

### 🎯 Goals:
- Reduce waiting time  
- Ensure fairness across requests  
- Efficient utilization of resources  

---

## 🏗️ System Architecture

```
Frontend (Next.js)
↓
API Layer (Flask)
↓
Scheduler Module
↓
SQLite Database
```

---

## 🛠️ Tech Stack

### Frontend:
- Next.js (App Router)  
- React  
- TypeScript  
- Tailwind CSS  

### Backend:
- Flask  
- SQLite  
- Flask-CORS  
- Werkzeug (password hashing)  

### Deployment:
- Vercel (Frontend)  
- Render (Backend)  

---

## 📂 Project Structure

```
SmartDispatch/
│
├── app/                # Next.js frontend pages
├── components/         # UI components
├── scheduler/          # Scheduling logic
├── app.py              # Flask backend entry
├── auth.py             # Authentication logic
├── database.py         # DB operations
├── schema.sql          # Database schema
└── smartdispatch.db    # SQLite database
```

---

## 👥 User Roles

### 👤 USER
- Create account  
- Login  
- Submit service requests  
- Track request status  

### 🛠️ ADMIN
- Login to admin dashboard  
- View all requests  
- Manage resource availability  
- Run scheduling system  

---

## 📸 Screenshots
-User Dashboard
[User Dashboard.png]

- Admin Dashboard
[Admin Dashboard.png]

- Scheduler
  [scheduler.png]
  
---

## ⚙️ Run Locally

### 1️⃣ Backend (Flask)

```bash
python -m venv .venv
.venv\Scripts\activate   # (Windows)

pip install flask flask-cors werkzeug
python app.py
```

Backend runs at:  
http://localhost:5000  

---

### 2️⃣ Frontend (Next.js)

```bash
npm install
npm run dev
```

Frontend runs at:  
http://localhost:3000  

---

## 🔐 Authentication Notes

- Session-based authentication using Flask sessions  

API endpoints:
- POST /api/login  
- GET /api/check-auth  
- POST /api/logout  

---

## 🔌 API Overview

| Endpoint        | Method | Description        |
|----------------|--------|--------------------|
| /api/login     | POST   | User/Admin login   |
| /api/logout    | POST   | Logout             |
| /api/requests  | GET    | Fetch requests     |
| /api/schedule  | POST   | Run scheduler      |

---

## 📈 Resume Highlights

- Built a full-stack resource dispatch system using Next.js and Flask  
- Implemented OS-based scheduling algorithms with anti-starvation logic  
- Designed role-based authentication and admin control panel  
- Deployed scalable application using Vercel and Render  

---

## 🔮 Future Improvements

- 🤖 AI-based demand prediction  
- 📍 Real-time location tracking (Maps integration)  
- ⚡ WebSocket-based live updates  
- 📊 Advanced analytics dashboard  

---


## ⭐ Final Note

This project demonstrates how core Operating System concepts can be applied to solve real-world problems in resource management and dispatch systems.

# 🚀 SmartDispatch

SmartDispatch is a role-based public resource scheduling system that applies Operating System scheduling concepts to real-world governance problems.  

It enables citizens to submit public service requests while administrators manage resource availability and apply scheduling algorithms such as Priority Scheduling and Shortest Job First (SJF) for optimized allocation.

---

## 🎯 Problem Statement

Public resources like garbage trucks, water tankers, and emergency vehicles are often underutilized or poorly scheduled due to inefficient allocation systems.

SmartDispatch solves this by:
- Treating service requests as processes
- Treating resources as system components
- Applying OS scheduling algorithms for optimized assignment

---

## 👥 Roles & Access Control

### 👤 User
- Create account
- Login
- Submit service requests
- View personal request status

### 👨‍💼 Admin
- Login (pre-seeded accounts only)
- View all requests
- Manage resource availability
- Run scheduling algorithms
- View assignment logs

---

## 🧠 Core Features

- 🔐 Role-Based Authentication (RBAC)
- 📩 Request Submission System
- 📊 Admin Dashboard
- 🚛 Resource Management Module
- ⚙ OS Scheduling Algorithms:
  - Priority Scheduling
  - Shortest Job First (SJF)
  - Greedy Allocation
- 📈 Activity Logs
- 🗂 SQLite Database Integration

---

## 🛠 Tech Stack

**Frontend**
- Next.js (App Router)
- React
- CSS / Tailwind / Bootstrap (if used)

**Backend**
- Flask
- SQLite
- Flask Sessions
- Flask-CORS

---

## 🗂 Project Structure
backend/
│
├── app.py
├── database.py
├── scheduler/
│ ├── os_engine.py
│ ├── aoa_engine.py
│
frontend/
│
├── app/
│ ├── login/
│ ├── create-account/
│ ├── dashboard/
│ ├── user-dashboard/
│ ├── manage-resources/


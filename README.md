# Wiperino

Wiperino is a real-time web application designed for streamers, speedrunners, and their audiences. 
It allows users to manage gameplay sessions ("runs") by tracking segments with wipe counters timers and poll sessions.
The system includes a browser-based overlay for OBS, dashboards for updating run data, a moderator panel for 
controlling poll visibility and viewer access for live voting.

---

## 🚀 Features

* Manage gameplay runs with wipe counters and timers
* Create and moderate real-time polls during streams
* Public voting interface for viewers
* OBS-compatible overlay with real-time updates
* WebSocket-based live synchronization via Redis
* JWT-based authentication (with optional test user)

---

## 🔧 Technologies Used

* **Python 3.12**
* **Django 5.2**
* **Django REST Framework 3.16**
* **Django Channels 4.2** (WebSockets)
* **Redis 5.2** (real-time messaging + storage)
* **Daphne** (ASGI server)
* **JWT Auth** (`djangorestframework-simplejwt`)
* **PostgreSQL** (via `psycopg2-binary`)
* **Vanilla JavaScript** (frontend)
* **OBS Studio** (Browser Source integration)
* **pytest + factory\_boy** (testing)

---

## ⚙️ Installation

1. **Clone the repository:**

```bash
git clone <repo_url>
cd wiperino
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Make migrations & run the server:**

```bash
python manage.py migrate
python manage.py runserver
```

4. **Start Redis (locally):**

```bash
redis-server
```

5. **Create a user:**

You can register manually via the `/register/` view, or use this test account:

```
Username: testuser
Password: testuser
```

---

## 🖥️ Usage

### 🎮 Managing Runs

* Go to `/dashboard/` and create a new run
* Add segments with wipe counters or timers
* Access live dashboard per run

### 📊 Poll Sessions

* Go to `/polls/create/` to create a new poll session
* Copy links for moderator, viewer, and overlay
* Moderator can add, publish, unpublish, or delete questions
* Viewers vote live via their link

### 🖼️ OBS Integration

* Use the `overlay` URL as a **Browser Source** in OBS (e.g. `http://localhost:8000/polls/o/<token>/`)
* The overlay will show the currently published poll in real-time

---

## 🔌 API Overview

### 🧾 Authentication:

* `POST /api/login/` – obtain JWT
* `POST /api/register/` – create user

### 🧩 Runs:

* `GET /api/runs/` – list user runs
* `POST /api/runs/` – create run
* `GET/PUT/DELETE /api/runs/<id>/` – manage a single run

### 🧮 Wipe Counters / Timers:

* `POST /api/runs/<id>/wipecounters/` – add wipe counter
* `POST /api/runs/<id>/timers/` – add timer
* Similar routes for retrieve/update/delete

### 📊 Polls:

* `POST /api/polls/create_session/` – create new poll session
* `POST /api/polls/m/<token>/add_poll/` – add question
* `GET /api/polls/m/<token>/` – list questions
* `DELETE /api/polls/m/<token>/delete/<question_id>/` – delete question

### 🌐 WebSocket Routes:

* `ws/runs/<run_id>/` – wipe/timer dashboard communication
* `ws/overlay/runs/<run_id>/` – OBS overlay sync
* `ws/polls/<token>/` – poll control, overlay, voting

---

## 📂 License

MIT License – see [LICENSE](LICENSE) for details.

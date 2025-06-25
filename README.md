# Chat-Application

A real-time web chat application built with Django, allowing users to register, log in, and chat one-on-one. Users can send text messages and upload images within the chat. The app features secure authentication, responsive design, and persistent message history.

---

## 🚀 Features

- **Real-Time Messaging:** Instant, smooth conversations with WebSockets (Django Channels).
- **User Authentication:** Secure registration and login.
- **One-on-One Chat:** Private messaging between users.
- **Media Sharing:** Upload and share images in chat.
- **Responsive UI:** Works great on desktop and mobile.
- **Persistent History:** Your chats are always stored and accessible.
- **Django Powered:** Robust Python backend.
- **Modern Frontend:** Clean, intuitive interface.

<!-- If you plan to add video chat, uncomment below -->
<!-- - **Video Chat (Planned):** Integration with Twilio for secure video calling. -->

---

## 🛠️ Tech Stack

- **Backend:** Django, Django Channels (for real-time communication)
- **Frontend:** HTML, CSS, (Bootstrap for responsive design)
- **WebSockets:** Powered by Django Channels
- **Database:** SQLite (default, easily switchable to PostgreSQL or MySQL)
- **Authentication:** Django's built-in auth system
- **Image Handling:** Pillow
- **Media Storage:** Django's media framework
- **Testing:** Django Test Framework
- **Deployment:** Render

<!-- If you plan to use Twilio for video chat, add: -->
<!-- - **Video/Audio:** Twilio API (for future video chat functionality) -->

---



## 🔧 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/certifiedJ/Chat-Application.git
cd Chat-Application
```

### 2. Create and activate a virtual environment

<details>
<summary><strong>Windows</strong></summary>

```bash
python -m venv venv
venv\Scripts\activate
```
</details>

<details>
<summary><strong>macOS / Linux</strong></summary>

```bash
python3 -m venv venv
source venv/bin/activate
```
</details>

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```
*(Use `python3` instead of `python` if needed on macOS/Linux)*

### 5. Run the server

```bash
python manage.py runserver
```
*(Use `python3` instead of `python` if needed on macOS/Linux)*

### 6. Open your browser

Visit: [http://localhost:8000/](http://localhost:8000/)

---

## 💡 Usage

- Register a new account or log in.
- Start chatting with other users in real time.
- Send text messages or upload images.

---



---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.

---

## 📬 Contact

Created by [certifiedJ](https://github.com/certifiedJ) — feel free to reach out!

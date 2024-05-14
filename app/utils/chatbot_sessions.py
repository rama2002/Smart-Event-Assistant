import threading
from datetime import datetime, timedelta

class ChatbotSessions:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ChatbotSessions, cls).__new__(cls)
                    cls._instance.sessions = {}
        return cls._instance

    def get_session(self, session_id):
        return self.sessions.get(session_id, {"conversations": [], "expiry": datetime.utcnow()})

    def update_session(self, session_id, human_msg, bot_response):
        if session_id in self.sessions:
            self.sessions[session_id]["conversations"].extend([human_msg, bot_response])
            self.sessions[session_id]["expiry"] = datetime.utcnow() + timedelta(hours=1)
        else:
            self.sessions[session_id] = {
                "conversations": [human_msg, bot_response],
                "expiry": datetime.utcnow() + timedelta(hours=1)
            }

    def clean_sessions(self):
        current_time = datetime.utcnow()
        self.sessions = {k: v for k, v in self.sessions.items() if v["expiry"] > current_time}

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

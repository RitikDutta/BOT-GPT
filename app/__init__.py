from flask import Flask, request, jsonify, render_template
from .chat_flow import ask_bot
from .database.relational import init_db, list_sessions

def create_app():
    """ creates the flask application """
    
    app = Flask(__name__)

    init_db()
    
    @app.route("/chat", methods=["POST"])
    def chat():
        """
        simple api endpoint:
        expects: { "message": "...", "session_id": "optional" }
        returns: { "session_id": "...", "reply": "..." }
        """        
        data = request.get_json(force=True) or {}
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"error": "no message provided"}), 400
        
        session_id = data.get("session_id") or "default"
        reply = ask_bot(session_id=session_id, user_input=user_input)

        return jsonify({"session_id": session_id, "reply": reply})

    @app.route("/")
    @app.route("/sessions")
    def sessions_page():
        sessions = list_sessions()
        return render_template("sessions.html", sessions=sessions)

    return app
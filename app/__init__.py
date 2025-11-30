from flask import Flask, request, jsonify, render_template, redirect, url_for
from .chat_flow import ask_bot
from .database.relational import init_db, list_sessions, get_messages, delete_session, delete_from_message, add_session
import time

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

    @app.route("/sessions/<session_id>")
    def messages_page(session_id):
        # show all messages inside one session
        msgs = get_messages(session_id)
        return render_template("messages.html", session_id=session_id, messages=msgs)
    
    @app.route("/sessions/<session_id>/delete", methods=["POST"])
    def delete_session_route(session_id):
        delete_session(session_id)
        return redirect(url_for("sessions_page"))
    
    @app.route("/sessions/<session_id>/cut/<int:message_id>", methods=["POST"])
    def cut_from_message_view(session_id, message_id):
        """
        delete a message and all messages after it for that session
        """
        delete_from_message(session_id, message_id)
        return redirect(url_for("messages_page", session_id=session_id))

    @app.route("/sessions/create", methods=["POST"])
    def create_session():
        """
        create a new session
        """
        session_id = f"sess_{int(time.time())}"   # simple unique id
        add_session(session_id)
        return redirect(url_for("messages_page", session_id=session_id))

    return app
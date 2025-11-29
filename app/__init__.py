from flask import Flask, request, jsonify
from .chat_flow import ask_bot

def create_app():
    """ creates the flask application """
    
    app = Flask(__name__)
    
    @app.route("/chat", methods=["POST"])
    def chat():
        """ handles the chat endpoint """
        
        data = request.get_json(force=True) or {}
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"error": "no message provided"}), 400
        
        session_id = data.get("session_id") or "default"
        reply = ask_bot(session_id=session_id, user_input=user_input)

        return jsonify({"session_id": session_id, "reply": reply})

    return app
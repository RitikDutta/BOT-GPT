from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template, redirect, url_for
from .chat_flow import ask_bot, sync_history_from_db, clear_history
from .database.relational import init_db, list_sessions, get_messages, delete_session, delete_from_message, add_session
from .database.vector_store import store_document_for_session, delete_vectors_for_session
from .utils.pdf_utils import extract_text_from_pdf
import time
import os

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
        clear_history(session_id)
        return redirect(url_for("sessions_page"))
    
    @app.route("/sessions/<session_id>/cut/<int:message_id>", methods=["POST"])
    def cut_from_message_view(session_id, message_id):
        """
        delete a message and all messages after it for that session
        """
        delete_from_message(session_id, message_id)
        sync_history_from_db(session_id) # sync messages again (rebuilt)
        return redirect(url_for("messages_page", session_id=session_id))

    @app.route("/sessions/create", methods=["POST"])
    def create_session():
        """
        create a new session
        """
        session_id = f"sess_{int(time.time())}"   # simple unique id
        add_session(session_id)
        return redirect(url_for("messages_page", session_id=session_id))

    @app.route("/sessions/<session_id>/send", methods=["POST"])
    def send_message_view(session_id):
        """
        send a message to the bot
        """
        user_text = request.form.get("message", "").strip()
        if not user_text:
            return redirect(url_for("messages_page", session_id=session_id))

        ask_bot(session_id=session_id, user_input=user_text)
        return redirect(url_for("messages_page", session_id=session_id))

    @app.route("/sessions/<session_id>/upload", methods=["POST"])
    def upload_pdf_view(session_id):
        """
        handle pdf upload:
        - validate file
        - extract text
        - store in pinecone with this session_id
        """
        file = request.files.get("file")
        if not file or file.filename == "":
            # nothing selected
            return redirect(url_for("messages_page", session_id=session_id))

        filename = file.filename.lower()
        if not filename.endswith(".pdf"):
            # only pdf allowed for now
            print("[WARN] non-pdf file skipped:", filename)
            return redirect(url_for("messages_page", session_id=session_id))

        # extract text
        text = extract_text_from_pdf(file)
        if not text.strip():
            print("[WARN] no text extracted from pdf")
            return redirect(url_for("messages_page", session_id=session_id))

        # send to vector store
        store_document_for_session(session_id=session_id, raw_text=text)

        return redirect(url_for("messages_page", session_id=session_id))

    return app
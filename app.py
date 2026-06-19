import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from config import Config
from models import UserModel, ChatModel
from chatbot import ChatbotEngine

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)
ai_engine = ChatbotEngine()

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('chat_interface'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = UserModel.create_user(username, email, pw_hash)
        if user_id:
            return redirect(url_for('login'))
        return render_template('register.html', error="Username or Email already exists.")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = UserModel.find_by_username(username)
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['profile_pic'] = user['profile_pic']
            return redirect(url_for('chat_interface'))
        return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat')
def chat_interface():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    sessions = ChatModel.get_user_sessions(session['user_id'])
    return render_template('index.html', sessions=sessions, username=session['username'], profile_pic=session['profile_pic'])

@app.route('/sessions/new', methods=['POST'])
def new_session():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    sid = ChatModel.create_session(session['user_id'])
    return jsonify({"session_id": sid})

@app.route('/sessions/<int:sid>/messages', methods=['GET'])
def get_messages(sid):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    messages = ChatModel.get_session_messages(sid)
    return jsonify(messages)

@app.route('/chat/<int:sid>', methods=['POST'])
def handle_message(sid):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    user_text = data.get('message')
    
    # Advanced Feature: Real-time Sentiment Analysis
    sentiment = ai_engine.analyze_sentiment(user_text)
    ChatModel.save_message(sid, 'user', user_text, sentiment)
    
    # Fetch context history for systemic coherence
    history = ChatModel.get_session_messages(sid)[:-1] # Exclude just saved message to prevent duplication in context engine
    bot_reply = ai_engine.generate_response(history, user_text)
    
    ChatModel.save_message(sid, 'bot', bot_reply)
    
    return jsonify({
        "reply": bot_reply,
        "sentiment": sentiment
    })

@app.route('/profile/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    new_username = request.form.get('username')
    file = request.files.get('profile_pic')
    filename = session.get('profile_pic')
    
    if file and file.filename != '':
        filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session['profile_pic'] = filename

    UserModel.update_profile(session['user_id'], new_username, filename)
    session['username'] = new_username
    return redirect(url_for('chat_interface'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

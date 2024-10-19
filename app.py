from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, emit
from os import getenv
from supabase import create_client
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

URL = getenv('SUPABASE_URL')
KEY = getenv('SUPABASE_KEY')
supabase_client = create_client(
    URL, KEY
)

@app.route('/')
def index():
    if session.get("username", False):
        messages = supabase_client.from_("messages").select("sender, message").execute().data
        return render_template('index.html', messages = messages)
    return render_template('login.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = supabase_client.from_('users').select("username, password").eq("username", username).execute().data
        if len(users) > 0:
            user = users[0]
            if check_password_hash(user['password'], password):
                session['username'] = username
                return redirect('/')
            else:
                error = "Invalid username or password"
        else:
            error = "User not found"
    return render_template('login.html', error=error)


@socketio.on('message')
def handle_message(message):
    supabase_client.from_("messages").insert({"sender": session['username'], "message": message}).execute()
    emit('message', {"sender": session['username'], "message": message}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app)

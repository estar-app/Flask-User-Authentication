import os
import openai
import time
import io
import uuid
import pyttsx3
import ffmpeg
import requests
import speech_recognition as sr


from flask import Flask, render_template, request, jsonify, Response, redirect, url_for,  render_template_string, send_file
from flask_cors import CORS
from gtts import gTTS
from flask import session


from flask import Blueprint
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user




core_bp = Blueprint("core", __name__)

# Create a Flask application
app = Flask(__name__)

db = SQLAlchemy()
db.init_app(app)




from src.accounts.models import Message

@core_bp.route("/")
@login_required
def home():  
    user_id = current_user.id
    
    messages = Message.query.filter_by(user_id=user_id).all()
    return render_template("core/index.html", user_id=user_id, messages=messages)


@core_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash('Password successfully changed.', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Password change was unsuccessful.', 'danger')
            return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)



MODEL = "gpt-3.5-turbo-0301"



@core_bp.route('/examples')
@login_required
def examples():
    return render_template('core/home.html')


@core_bp.route('/talkgpt')
@login_required
def talkgpt():
    # Retrieve all chat messages from the database
    messages = Message.query.order_by(Message.created_at.asc()).all()
    chat_history = [{"id": m.id, "content": m.content} for m in messages]

    completion = openai.ChatCompletion.create(
        model=MODEL,
        max_tokens=3000,
        n=1,
        stop=None,
        temperature=0.6,
        messages=[{"role": "user", "content": "Hello!"}]
    )
    response = (completion.choices[0].message)
    return render_template("core/talkgpt.html", response=response, chat_history=chat_history)

def generate_response(prompt, user_id):
    user = User.query.get(user_id)
    message = Message(user_id=user.id, user_message=prompt, created_at=datetime.utcnow())
    db.session.add(message)
    db.session.commit()

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=3000,
        n=1,
        stop=None,
    )

    bot_response = response.choices[0].text
    message.bot_response = bot_response
    message.content = bot_response
    message.timestamp = datetime.utcnow()
    db.session.commit()

    return bot_response


@core_bp.route("/send_message", methods=["POST"])
def send_message():
    message = request.json["message"]
    user_id = session.get("user_id")
    response = generate_response(message, user_id)
    
    # Retrieve all chat messages from the database
    messages = Message.query.order_by(Message.created_at.asc()).all()
    chat_history = [{"id": m.id, "content": m.content} for m in messages]
    
    return jsonify({"message": response, "chat_history": chat_history})



def stream_response(prompt):
    def generate():
        time.sleep(0.5)  # add delay to allow user input to be sent first
        yield "data: {}\n\n".format("Hello! How can I assist you today?")

        while True:
            completions = openai.ChatCompletion.create(
                model=MODEL,
                prompt=prompt,
                max_tokens=3000,
                n=1,
                stop=None,
                temperature=0.5,
            )

            message = completions.choices[0].message
            prompt += message

            yield "data: {}\n\n".format(message)

    return Response(generate(), mimetype="text/event-stream")



def generate_audio_file(response_text):
    # Generate a unique filename for the audio file
    filename = str(uuid.uuid4()) + '.wav'
    file_path = os.path.join('audio', filename)

    # Generate the audio file using gTTS
    tts = gTTS(response_text)
    tts.save(file_path)

    # Return the filename so that it can be passed to the play_audio() function
    return filename


@core_bp.route('/process_input', methods=['POST'])
def process_input():
    user_input = request.json['user_input']
    # Process the user input and generate a response
    response_text = 'Hello, world!'
    generate_audio_file(response_text)
    return jsonify({'text': response_text})

@core_bp.route('/get-audio', methods=['POST'])
def get_audio():
    text = request.json.get('text')
    filename = f'{uuid.uuid4()}.mp3'
    filepath = os.path.join(app.static_folder, 'audio', filename)
    tts = gTTS(text=text)
    tts.save(filepath)
    return {'audio_file_path': f'audio/{filename}'}

@core_bp.route("/play-audio", methods=["POST"])
def play_audio():
    response = request.form["response"]
    language = 'en'
    filename = str(uuid.uuid4())
    audio_path = f"audio/{filename}.wav"
    tts = gTTS(text=response, lang=language)
    tts.save(audio_path)
    return send_file(audio_path, as_attachment=True)

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()

    # get the device index of the default input device
    device_index = None
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        if 'default' in name:
            device_index = i
            break

    # create a microphone instance using the default input device
    microphone = sr.Microphone(device_index=device_index)

    # adjust the recognizer sensitivity to ambient noise and record audio
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # transcribe the speech
    try:
        transcription = recognizer.recognize_google(audio)
        return {'success': True, 'transcription': transcription}
    except sr.UnknownValueError:
        # speech was unintelligible
        return {'success': False, 'error': 'Unable to recognize speech'}
    except sr.RequestError:
        # API was unreachable or unresponsive
        return {'success': False, 'error': 'API unavailable'}




@core_bp.route('/mobile')
@login_required
def mobile():
    
    return render_template("core/mobile.html")

@core_bp.route('/editor')
@login_required
def editor():
    return render_template('core/editor.html')


@core_bp.route('/image_generator')
@login_required
def image_generator():
    return render_template('core/image_generator.html')


@core_bp.route('/coder')
@login_required
def coder():
    return render_template('core/coder.html')

@core_bp.route('/get_messages')
def get_messages():
    # get page number from request parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # query chat history from database
    messages = Message.query.order_by(Message.timestamp.desc()).paginate(page, per_page)

    # format chat history as list of dictionaries
    messages_list = []
    for message in messages.items:
        messages_list.append({
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user': message.user,
            'message': message.message
        })

    # create dictionary response
    response = {
        'messages': messages_list,
        'prev_page': url_for('get_messages', page=messages.prev_num) if messages.has_prev else None,
        'next_page': url_for('get_messages', page=messages.next_num) if messages.has_next else None
    }

    # return JSON response
    return jsonify(response)


from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from utils.utils import load_data, get_end_options, filter_practice_items

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'supersecretkey'  # For session management

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

@app.route('/', methods=['GET', 'POST'])
def home():
    type_options = ['Hiragana', 'Katakana', 'Conversation']
    selected_type = request.form.get('type', 'Hiragana')
    method = request.form.get('method', 'Ordered')
    data = load_data(selected_type, DATA_DIR)
    end_options = get_end_options(selected_type, data)
    selected_end = request.form.get('end_at', end_options[0] if end_options else None)
    if request.method == 'POST' and 'start' in request.form:
        session['type'] = selected_type
        session['end_at'] = selected_end
        session['method'] = method
        session['idx'] = 0
        session['phase'] = 0
        return redirect(url_for('flashcard'))
    return render_template('home.html', type_options=type_options, end_options=end_options, selected_type=selected_type, selected_end=selected_end, method=method)

@app.route('/flashcard', methods=['GET', 'POST'])
def flashcard():
    type_ = session.get('type', 'Hiragana')
    end_at = session.get('end_at')
    method = session.get('method', 'Ordered')
    data = load_data(type_, DATA_DIR)
    items = filter_practice_items(type_, data, end_at)
    idx = session.get('idx', 0)
    phase = session.get('phase', 0)
    # Only shuffle once per session, not every request
    if method == 'Random' and request.method == 'POST' and 'home' in request.form:
        import random
        random.shuffle(items)
        session['idx'] = 0
        session['phase'] = 0
        idx = 0
        phase = 0
        return redirect(url_for('home'))
    elif method == 'Random' and request.method == 'POST' and not ('back' in request.form or 'home' in request.form):
        # Only go to next random item after phase 2
        if phase < 2:
            phase += 1
        else:
            import random
            if len(items) > 1:
                # Pick a new random index different from current idx
                next_idx = idx
                while next_idx == idx:
                    next_idx = random.randint(0, len(items)-1)
                idx = next_idx
            else:
                idx = 0
            phase = 0
        session['idx'] = idx
        session['phase'] = phase
        item = items[idx] if items else None
        display_jp = None
        display_pronounce = None
        display_romaji = None
        if item:
            if type_ == 'Hiragana':
                display_jp = item.get('hiragana')
                display_romaji = item.get('english')
            elif type_ == 'Katakana':
                display_jp = item.get('katakana')
                display_romaji = item.get('english')
            elif type_ == 'Conversation':
                display_jp = item.get('kanji')
                display_pronounce = item.get('pronounce')
                display_romaji = item.get('english')
        return render_template('flashcard.html', item=item, phase=phase, idx=idx, total=len(items), display_jp=display_jp, display_pronounce=display_pronounce, display_romaji=display_romaji)
    else:
        # Ordered method or initial load
        if request.method == 'POST':
            if 'back' in request.form:
                if idx > 0:
                    idx -= 1
                    phase = 0
            elif 'home' in request.form:
                session.pop('idx', None)
                session.pop('phase', None)
                return redirect(url_for('home'))
            else:
                if phase < 2:
                    phase += 1
                else:
                    if len(items) > 0:
                        idx = (idx + 1) % len(items)
                    else:
                        idx = 0
                    phase = 0
            session['idx'] = idx
            session['phase'] = phase
        item = items[idx] if items else None
        display_jp = None
        display_pronounce = None
        display_romaji = None
        if item:
            if type_ == 'Hiragana':
                display_jp = item.get('hiragana')
                display_romaji = item.get('english')
            elif type_ == 'Katakana':
                display_jp = item.get('katakana')
                display_romaji = item.get('english')
            elif type_ == 'Conversation':
                display_jp = item.get('kanji')
                display_pronounce = item.get('pronounce')
                display_romaji = item.get('english')
        if not items:
            # If no items, show a blank card or error message
            return render_template('flashcard.html', item=None, phase=0, idx=0, total=0, display_jp=None, display_romaji=None)
        return render_template('flashcard.html', item=item, phase=phase, idx=idx, total=len(items), display_jp=display_jp, display_pronounce=display_pronounce, display_romaji=display_romaji)

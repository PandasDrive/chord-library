import os
import io
import random # NEW: Added for the AI generator
from flask import Flask, request, jsonify, send_file, abort, render_template

app = Flask(__name__)

# --- COMPREHENSIVE DATA DEFINITIONS ---

CHORD_DEFINITIONS = {
    # --- A Chords ---
    'A':      { "frets": [-1, 0, 2, 2, 2, 0], "barres": [], "title": "A Major" },
    'Am':     { "frets": [-1, 0, 2, 2, 1, 0], "barres": [], "title": "A Minor" },
    'A7':     { "frets": [-1, 0, 2, 0, 2, 0], "barres": [], "title": "A Dominant 7th" },
    'Amaj7':  { "frets": [-1, 0, 2, 1, 2, 0], "barres": [], "title": "A Major 7th" },
    'Am7':    { "frets": [-1, 0, 2, 0, 1, 0], "barres": [], "title": "A Minor 7th" },
    'Asus4':  { "frets": [-1, 0, 2, 2, 3, 0], "barres": [], "title": "A Suspended 4th" },
    'Asus2':  { "frets": [-1, 0, 2, 2, 0, 0], "barres": [], "title": "A Suspended 2nd" },
    'Aadd9':  { "frets": [-1, 0, 2, 2, 0, 0], "barres": [], "title": "A Add 9" },
    'A6':     { "frets": [-1, 0, 2, 2, 2, 2], "barres": [], "title": "A Major 6th" },
    'Adim':   { "frets": [-1, -1, 1, 2, 1, 2], "barres": [], "title": "A Diminished" },
    'Aaug':   { "frets": [-1, 0, 3, 2, 2, 1], "barres": [], "title": "A Augmented" },

    # --- B Chords ---
    'B':      { "frets": [-1, 2, 4, 4, 4, 2], "barres": [{"fromString": 5, "toString": 1, "fret": 2 }], "title": "B Major" },
    'Bm':     { "frets": [-1, 2, 4, 4, 3, 2], "barres": [{"fromString": 5, "toString": 1, "fret": 2 }], "title": "B Minor" },
    'B7':     { "frets": [-1, 2, 1, 2, 0, 2], "barres": [], "title": "B Dominant 7th" },
    'Bmaj7':  { "frets": [-1, 2, 4, 3, 4, 2], "barres": [{"fromString": 5, "toString": 1, "fret": 2 }], "title": "B Major 7th" },
    'Bm7':    { "frets": [-1, 2, 0, 2, 0, 2], "barres": [], "title": "B Minor 7th" },
    'Bsus4':  { "frets": [-1, 2, 4, 4, 5, 2], "barres": [{"fromString": 5, "toString": 1, "fret": 2 }], "title": "B Suspended 4th" },
    'Bm7b5':  { "frets": [-1, 2, 3, 2, 3, -1], "barres": [], "title": "B Minor 7th flat 5 (Half-Diminished)" },

    # --- C Chords ---
    'C':      { "frets": [-1, 3, 2, 0, 1, 0], "barres": [], "title": "C Major" },
    'Cm':     { "frets": [-1, 3, 5, 5, 4, 3], "barres": [{"fromString": 5, "toString": 1, "fret": 3 }], "title": "C Minor" },
    'C7':     { "frets": [-1, 3, 2, 3, 1, 0], "barres": [], "title": "C Dominant 7th" },
    'Cmaj7':  { "frets": [-1, 3, 2, 0, 0, 0], "barres": [], "title": "C Major 7th" },
    'Cm7':    { "frets": [-1, 3, 5, 3, 4, 3], "barres": [{"fromString": 5, "toString": 1, "fret": 3 }], "title": "C Minor 7th" },
    'Cadd9':  { "frets": [-1, 3, 2, 0, 3, 0], "barres": [], "title": "C Add 9" },
    'Csus4':  { "frets": [-1, 3, 3, 0, 1, 1], "barres": [], "title": "C Suspended 4th" },
    'Cdim':   { "frets": [-1, -1, 1, 2, 1, 2], "barres": [], "title": "C Diminished" },
    'Caug':   { "frets": [-1, 3, 2, 1, 1, 0], "barres": [], "title": "C Augmented" },

    # --- D Chords ---
    'D':      { "frets": [-1, -1, 0, 2, 3, 2], "barres": [], "title": "D Major" },
    'Dm':     { "frets": [-1, -1, 0, 2, 3, 1], "barres": [], "title": "D Minor" },
    'D7':     { "frets": [-1, -1, 0, 2, 1, 2], "barres": [], "title": "D Dominant 7th" },
    'Dmaj7':  { "frets": [-1, -1, 0, 2, 2, 2], "barres": [], "title": "D Major 7th" },
    'Dm7':    { "frets": [-1, -1, 0, 2, 1, 1], "barres": [], "title": "D Minor 7th" },
    'Dsus4':  { "frets": [-1, -1, 0, 2, 3, 3], "barres": [], "title": "D Suspended 4th" },
    'Dsus2':  { "frets": [-1, -1, 0, 2, 3, 0], "barres": [], "title": "D Suspended 2nd" },
    'Dadd9':  { "frets": [-1, -1, 0, 2, 3, 0], "barres": [], "title": "D Add 9" },
    'D6':     { "frets": [-1, -1, 0, 2, 0, 2], "barres": [], "title": "D Major 6th" },
    'Dm6':    { "frets": [-1, -1, 0, 2, 0, 1], "barres": [], "title": "D Minor 6th" },

    # --- E Chords ---
    'E':      { "frets": [0, 2, 2, 1, 0, 0], "barres": [], "title": "E Major" },
    'Em':     { "frets": [0, 2, 2, 0, 0, 0], "barres": [], "title": "E Minor" },
    'E7':     { "frets": [0, 2, 0, 1, 0, 0], "barres": [], "title": "E Dominant 7th" },
    'Emaj7':  { "frets": [0, 2, 1, 1, 0, 0], "barres": [], "title": "E Major 7th" },
    'Em7':    { "frets": [0, 2, 2, 0, 3, 0], "barres": [], "title": "E Minor 7th" },
    'Esus4':  { "frets": [0, 2, 2, 2, 0, 0], "barres": [], "title": "E Suspended 4th" },
    'Eadd9':  { "frets": [0, 2, 2, 1, 0, 2], "barres": [], "title": "E Add 9" },
    'E6':     { "frets": [0, 2, 2, 1, 2, 0], "barres": [], "title": "E Major 6th" },
    'Em6':    { "frets": [0, 2, 2, 0, 2, 0], "barres": [], "title": "E Minor 6th" },

    # --- F Chords ---
    'F':      { "frets": [1, 3, 3, 2, 1, 1], "barres": [{"fromString": 6, "toString": 1, "fret": 1 }], "title": "F Major" },
    'Fm':     { "frets": [1, 3, 3, 1, 1, 1], "barres": [{"fromString": 6, "toString": 1, "fret": 1 }], "title": "F Minor" },
    'F7':     { "frets": [1, 3, 1, 2, 1, 1], "barres": [{"fromString": 6, "toString": 1, "fret": 1 }], "title": "F Dominant 7th" },
    'Fmaj7':  { "frets": [1, 0, 2, 2, 1, 0], "barres": [], "title": "F Major 7th (C-shape)" },
    'Fm7':    { "frets": [1, 3, 1, 1, 1, 1], "barres": [{"fromString": 6, "toString": 1, "fret": 1 }], "title": "F Minor 7th" },
    'Fadd9':  { "frets": [-1, 3, 3, 2, 1, 3], "barres": [], "title": "F Add 9" },
    
    # --- G Chords ---
    'G':      { "frets": [3, 2, 0, 0, 0, 3], "barres": [], "title": "G Major" },
    'Gm':     { "frets": [3, 5, 5, 3, 3, 3], "barres": [{"fromString": 6, "toString": 1, "fret": 3 }], "title": "G Minor" },
    'G7':     { "frets": [3, 2, 0, 0, 0, 1], "barres": [], "title": "G Dominant 7th" },
    'Gmaj7':  { "frets": [3, 2, 0, 0, 0, 2], "barres": [], "title": "G Major 7th" },
    'Gm7':    { "frets": [3, 5, 3, 3, 3, 3], "barres": [{"fromString": 6, "toString": 1, "fret": 3 }], "title": "G Minor 7th" },
    'Gsus4':  { "frets": [3, 3, 0, 0, 1, 3], "barres": [], "title": "G Suspended 4th" },
    'Gadd9':  { "frets": [3, 2, 0, 2, 0, 3], "barres": [], "title": "G Add 9" },
    'G6':     { "frets": [3, 2, 0, 0, 0, 0], "barres": [], "title": "G Major 6th" },
    'Gdim':   { "frets": [-1, -1, -1, 3, 2, 3], "barres": [], "title": "G Diminished" },
    'Gaug':   { "frets": [3, 2, 1, 0, 0, 3], "barres": [], "title": "G Augmented" },
}

SCALE_DEFINITIONS = {
    "major_scale": {
        "title": "Major Scale (Ionian)",
        "description": "The foundation of Western music, with a happy sound.",
        "intervals": [0, 2, 4, 5, 7, 9, 11]
    },
    "minor_pentatonic": {
        "title": "Minor Pentatonic",
        "description": "A versatile 5-note scale, essential for rock and blues.",
        "intervals": [0, 3, 5, 7, 10]
    },
    "aeolian": {
        "title": "Natural Minor (Aeolian)",
        "description": "The standard minor scale, creates a sad or serious mood.",
        "intervals": [0, 2, 3, 5, 7, 8, 10]
    },
    "dorian": {
        "title": "Dorian Mode",
        "description": "A minor-type scale with a brighter, jazzy or Celtic feel.",
        "intervals": [0, 2, 3, 5, 7, 9, 10]
    },
    "harmonic_minor": {
        "title": "Harmonic Minor",
        "description": "A minor scale with a raised 7th, creating a dramatic, classical, or exotic sound.",
        "intervals": [0, 2, 3, 5, 7, 8, 11]
    }
}

NOTE_MAP = {"E": 0, "F": 1, "F#": 2, "G": 3, "G#": 4, "A": 5, "A#": 6, "B": 7, "C": 8, "C#": 9, "D": 10, "D#": 11}

# --- NEW: Markov Chain Chord Progression Generator ---
def build_markov_chain(corpus):
    chain = {}
    for progression in corpus:
        for i in range(len(progression) - 1):
            current_chord = progression[i]
            next_chord = progression[i+1]
            if current_chord not in chain:
                chain[current_chord] = []
            chain[current_chord].append(next_chord)
    return chain

TRAINING_CORPUS = [
    ['C', 'G', 'Am', 'F'],          # Classic pop/rock
    ['G', 'D', 'Em', 'C'],          # Another classic
    ['Am', 'F', 'C', 'G'],          # Minor key standard
    ['D', 'A', 'Bm', 'G'],          # Common in rock ballads
    ['E', 'A', 'E', 'B7'],          # Basic blues
    ['C', 'Am', 'Dm', 'G7'],         # Doo-wop progression
    ['F', 'C', 'G', 'C'],
    ['Bm', 'G', 'D', 'A']
]
MARKOV_CHAIN = build_markov_chain(TRAINING_CORPUS)

@app.route('/api/generate-progression', methods=['GET'])
def generate_progression():
    start_chord = request.args.get('start_chord', 'C')
    length = int(request.args.get('length', 4))
    
    if start_chord not in MARKOV_CHAIN:
        start_chord = random.choice(list(MARKOV_CHAIN.keys()))

    progression = [start_chord]
    current_chord = start_chord

    for _ in range(length - 1):
        if current_chord in MARKOV_CHAIN and MARKOV_CHAIN[current_chord]:
            next_chord = random.choice(MARKOV_CHAIN[current_chord])
            progression.append(next_chord)
            current_chord = next_chord
        else:
            current_chord = random.choice(list(MARKOV_CHAIN.keys()))
            progression.append(current_chord)
            
    return jsonify(progression)

def generate_svg_chord_diagram(chord_data):
    STRING_COUNT, FRET_COUNT = 6, 5
    WIDTH, HEIGHT = 250, 300
    PAD_X, PAD_Y = 40, 50
    DIAGRAM_WIDTH, DIAGRAM_HEIGHT = WIDTH - (PAD_X * 2), HEIGHT - (PAD_Y * 2)
    STRING_SPACING = DIAGRAM_WIDTH / (STRING_COUNT - 1)
    FRET_SPACING = DIAGRAM_HEIGHT / FRET_COUNT
    NUT_HEIGHT, DOT_RADIUS = 8, FRET_SPACING / 3.5
    OPEN_STRING_RADIUS = DOT_RADIUS / 2
    COLOR_FG = "#FFFFFF"
    COLOR_BG = "#1a1a1a"

    frets, barres = chord_data.get('frets', []), chord_data.get('barres', [])
    positive_frets = [f for f in frets if f > 0]
    min_fret = min(positive_frets) if positive_frets else 1
    position = min_fret if min_fret > 1 and max(positive_frets) - min_fret < FRET_COUNT else 1

    svg = [f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" class="chord-svg">',
           f'<rect width="100%" height="100%" fill="{COLOR_BG}"/>',
           f'<g transform="translate({PAD_X}, {PAD_Y})" font-family="Arial" fill="{COLOR_FG}">']

    if position > 1:
        svg.append(f'<text x="-{PAD_X/2.5}" y="{FRET_SPACING*0.8}" font-size="{FRET_SPACING*0.8}" text-anchor="middle" class="fret-number">{position}</text>')

    for i in range(FRET_COUNT + 1):
        y = i * FRET_SPACING
        stroke_width = NUT_HEIGHT if i == 0 and position == 1 else 2
        svg.append(f'<line class="fret-line" style="--animation-order: {i+1};" x1="0" y1="{y}" x2="{DIAGRAM_WIDTH}" y2="{y}" stroke="{COLOR_FG}" stroke-width="{stroke_width}" />')

    for i in range(STRING_COUNT):
        x = i * STRING_SPACING
        svg.append(f'<line class="string-line" style="--animation-order: {i+1};" x1="{x}" y1="0" x2="{x}" y2="{DIAGRAM_HEIGHT}" stroke="{COLOR_FG}" stroke-width="1" />')

    for barre in barres:
        barre_fret = barre['fret']
        if not (position <= barre_fret < position + FRET_COUNT): continue
        fret_index = barre_fret - position + 1
        y = (fret_index * FRET_SPACING) - (FRET_SPACING / 2)
        start_string_index = STRING_COUNT - barre['fromString']
        end_string_index = STRING_COUNT - barre['toString']
        x_start, x_end = start_string_index * STRING_SPACING, end_string_index * STRING_SPACING
        svg.append(f'<rect class="barre" x="{min(x_start, x_end)}" y="{y - DOT_RADIUS}" width="{abs(x_end - x_start)}" height="{DOT_RADIUS * 2}" rx="{DOT_RADIUS}" ry="{DOT_RADIUS}" fill="{COLOR_FG}" />')

    for i, fret in enumerate(frets):
        string_x = i * STRING_SPACING
        if fret == -1:
            svg.append(f'<g class="muted-string" transform="translate({string_x}, {-FRET_SPACING/2}) scale(0.7)">'
                       f'<line x1="-{OPEN_STRING_RADIUS}" y1="-{OPEN_STRING_RADIUS}" x2="{OPEN_STRING_RADIUS}" y2="{OPEN_STRING_RADIUS}" stroke="{COLOR_FG}" stroke-width="3"/>'
                       f'<line x1="-{OPEN_STRING_RADIUS}" y1="{OPEN_STRING_RADIUS}" x2="{OPEN_STRING_RADIUS}" y2="-{OPEN_STRING_RADIUS}" stroke="{COLOR_FG}" stroke-width="3"/>'
                       '</g>')
        elif fret == 0:
            svg.append(f'<circle class="open-string" cx="{string_x}" cy="{-FRET_SPACING/2}" r="{OPEN_STRING_RADIUS}" stroke="{COLOR_FG}" stroke-width="2" fill="none" />')
        elif position <= fret < position + FRET_COUNT:
            fret_index = fret - position + 1
            dot_y = (fret_index * FRET_SPACING) - (FRET_SPACING / 2)
            svg.append(f'<circle class="finger-dot" cx="{string_x}" cy="{dot_y}" r="{DOT_RADIUS}" fill="{COLOR_FG}" />')

    svg.extend(['</g>', '</svg>'])
    return "\n".join(svg)

def generate_svg_scale_diagram(scale_data, key):
    STRING_COUNT, FRET_COUNT = 6, 12
    WIDTH, HEIGHT = 800, 200
    PAD_X, PAD_Y = 50, 30
    DIAGRAM_WIDTH, DIAGRAM_HEIGHT = WIDTH - (PAD_X * 2), HEIGHT - (PAD_Y * 2)
    STRING_SPACING = DIAGRAM_HEIGHT / (STRING_COUNT - 1)
    FRET_SPACING = DIAGRAM_WIDTH / FRET_COUNT
    DOT_RADIUS = STRING_SPACING / 3
    
    OPEN_STRING_NOTES = [4, 9, 2, 7, 11, 4] 

    root_note = NOTE_MAP.get(key, 0)
    scale_intervals = scale_data.get('intervals', [])
    scale_notes = [(root_note + i) % 12 for i in scale_intervals]

    svg = [f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" class="scale-svg">',
           f'<rect width="100%" height="100%" fill="var(--bg-color)"/>',
           f'<g transform="translate({PAD_X}, {PAD_Y})" font-family="VT323, monospace">']

    for fret_num in [3, 5, 7, 9, 12]:
        x = (fret_num * FRET_SPACING) - (FRET_SPACING / 2)
        svg.append(f'<circle cx="{x}" cy="{DIAGRAM_HEIGHT / 2}" r="{DOT_RADIUS / 2}" fill="rgba(255, 255, 255, 0.1)"/>')
        if fret_num == 12:
            svg.append(f'<circle cx="{x}" cy="{DIAGRAM_HEIGHT / 2 - STRING_SPACING * 2}" r="{DOT_RADIUS / 2}" fill="rgba(255, 255, 255, 0.1)"/>')
            svg.append(f'<circle cx="{x}" cy="{DIAGRAM_HEIGHT / 2 + STRING_SPACING * 2}" r="{DOT_RADIUS / 2}" fill="rgba(255, 255, 255, 0.1)"/>')
    
    for i in range(FRET_COUNT + 1):
        x = i * FRET_SPACING
        stroke_width = 8 if i == 0 else 2
        svg.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{DIAGRAM_HEIGHT}" stroke="rgba(255, 255, 255, 0.3)" stroke-width="{stroke_width}" />')
    for i in range(STRING_COUNT):
        y = i * STRING_SPACING
        svg.append(f'<line x1="0" y1="{y}" x2="{DIAGRAM_WIDTH}" y2="{y}" stroke="rgba(255, 255, 255, 0.5)" stroke-width="{i/2 + 1}" />')

    for string_idx, open_note in enumerate(OPEN_STRING_NOTES):
        for fret_idx in range(FRET_COUNT + 1):
            current_note = (open_note + fret_idx) % 12
            if current_note in scale_notes:
                cx = (fret_idx * FRET_SPACING) - (FRET_SPACING / 2) if fret_idx > 0 else -PAD_X/2
                cy = string_idx * STRING_SPACING
                
                is_root = (current_note == root_note)
                note_class = "root-note" if is_root else "scale-note"
                
                svg.append(f'<circle class="{note_class}" cx="{cx}" cy="{cy}" r="{DOT_RADIUS}" />')

    svg.extend(['</g>', '</svg>'])
    return "".join(svg)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chords', methods=['GET', 'POST'])
def handle_chords():
    if request.method == 'GET':
        return jsonify(CHORD_DEFINITIONS)
    if request.method == 'POST':
        new_chord = request.json
        name = new_chord.get('name')
        if not name or name in CHORD_DEFINITIONS:
            abort(400, "Invalid or duplicate chord name.")
        CHORD_DEFINITIONS[name] = new_chord
        return jsonify({"message": f"Chord '{name}' added."}), 201

@app.route('/api/chord-diagram', methods=['POST'])
def chord_diagram():
    chord_name = request.form.get('chord')
    if not chord_name: abort(400, "Chord name not provided.")
    chord_data = CHORD_DEFINITIONS.get(chord_name)
    if not chord_data: abort(404, f"Chord definition for '{chord_name}' not found.")
    svg_string = generate_svg_chord_diagram(chord_data)
    return send_file(io.BytesIO(svg_string.encode('utf-8')), mimetype='image/svg+xml')

@app.route('/api/scales', methods=['GET'])
def get_scales():
    return jsonify(SCALE_DEFINITIONS)

@app.route('/api/scale-diagram', methods=['POST'])
def scale_diagram():
    scale_name = request.form.get('scale')
    key = request.form.get('key', 'E')
    
    if not scale_name: abort(400, "Scale name not provided.")
    scale_data = SCALE_DEFINITIONS.get(scale_name)
    if not scale_data: abort(404, f"Scale definition for '{scale_name}' not found.")
        
    svg_string = generate_svg_scale_diagram(scale_data, key)
    return send_file(io.BytesIO(svg_string.encode('utf-8')), mimetype='image/svg+xml')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
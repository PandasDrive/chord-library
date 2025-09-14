import os
import io
from flask import Flask, request, jsonify, send_file, abort

app = Flask(__name__)

# This is the single source of truth for all chord shapes.
CHORD_DEFINITIONS = {
    'C':    { "frets": [-1, 3, 2, 0, 1, 0], "barres": [], "title": "C Major" },
    'Cm':   { "frets": [-1, 3, 5, 5, 4, 3], "barres": [{"fromString": 5, "toString": 1, "fret": 3 }], "title": "C Minor" },
    'C7':   { "frets": [-1, 3, 2, 3, 1, 0], "barres": [], "title": "C7" },
    'Cmaj7':{ "frets": [-1, 3, 2, 0, 0, 0], "barres": [], "title": "C Major 7th" },
    'G':    { "frets": [3, 2, 0, 0, 0, 3], "barres": [], "title": "G Major" },
    'G7':   { "frets": [3, 2, 0, 0, 0, 1], "barres": [], "title": "G7" },
    'Am':   { "frets": [-1, 0, 2, 2, 1, 0], "barres": [], "title": "A Minor" },
    'A':    { "frets": [-1, 0, 2, 2, 2, 0], "barres": [], "title": "A Major" },
    'A7':   { "frets": [-1, 0, 2, 0, 2, 0], "barres": [], "title": "A7" },
    'E':    { "frets": [0, 2, 2, 1, 0, 0], "barres": [], "title": "E Major" },
    'Em':   { "frets": [0, 2, 2, 0, 0, 0], "barres": [], "title": "E Minor" },
    'E7':   { "frets": [0, 2, 0, 1, 0, 0], "barres": [], "title": "E7" },
    'D':    { "frets": [-1, -1, 0, 2, 3, 2], "barres": [], "title": "D Major" },
    'Dm':   { "frets": [-1, -1, 0, 2, 3, 1], "barres": [], "title": "D Minor" },
    'D7':   { "frets": [-1, -1, 0, 2, 1, 2], "barres": [], "title": "D7" },
    'F':    { "frets": [1, 3, 3, 2, 1, 1], "barres": [{"fromString": 6, "toString": 1, "fret": 1 }], "title": "F Major" },
    'B7':   { "frets": [-1, 2, 1, 2, 0, 2], "barres": [], "title": "B7" },
}

# --- NEW: Updated SCALE_DEFINITIONS with 5 boxes and root notes ---
SCALE_DEFINITIONS = {
    "minor_pentatonic": {
        "title": "Minor Pentatonic",
        "description": "A versatile 5-note scale, essential for rock and blues.",
        "pattern": {
            "box1": { "frets": [(6,0), (6,3), (5,0), (5,2), (4,0), (4,2), (3,0), (3,2), (2,0), (2,3), (1,0), (1,3)], "roots": [(6,0), (4,2), (1,0)] },
            "box2": { "frets": [(6,3), (6,5), (5,2), (5,5), (4,2), (4,5), (3,2), (3,4), (2,3), (2,5), (1,3), (1,5)], "roots": [(5,5), (3,2), (1,5)] },
            "box3": { "frets": [(6,5), (6,8), (5,5), (5,7), (4,5), (4,7), (3,4), (3,7), (2,5), (2,8), (1,5), (1,8)], "roots": [(6,8), (4,5), (2,8), (1,5)] },
            "box4": { "frets": [(6,8), (6,10), (5,7), (5,10), (4,7), (4,9), (3,7), (3,9), (2,8), (2,10), (1,8), (1,10)],"roots": [(6,8), (4,7), (2,10)] },
            "box5": { "frets": [(6,10), (6,12), (5,10), (5,12), (4,9), (4,12), (3,9), (3,12), (2,10), (2,12), (1,10), (1,12)],"roots": [(6,12), (5,10), (3,12), (1,10)] }
        }
    },
    "major_scale": {
        "title": "Major Scale (Ionian)",
        "description": "The foundation of Western music, with a happy sound.",
        "pattern": {
            "box1": {"root_string": 6, "frets": [(6,0), (6,2), (6,4), (5,0), (5,2), (5,4), (4,1), (4,2), (4,4), (3,1), (3,2), (3,4), (2,2), (2,4), (2,5), (1,2), (1,4), (1,5)], "roots": [(6,0), (5,2), (4,4)]}
        }
    }
}


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

    svg = [f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="100%" height="100%" fill="{COLOR_BG}"/>',
           f'<g transform="translate({PAD_X}, {PAD_Y})" font-family="Arial" fill="{COLOR_FG}">']

    if position > 1:
        svg.append(f'<text x="-{PAD_X/2.5}" y="{FRET_SPACING*0.8}" font-size="{FRET_SPACING*0.8}" text-anchor="middle">{position}</text>')

    for i in range(FRET_COUNT + 1):
        y = i * FRET_SPACING
        stroke_width = NUT_HEIGHT if i == 0 and position == 1 else 2
        svg.append(f'<line x1="0" y1="{y}" x2="{DIAGRAM_WIDTH}" y2="{y}" stroke="{COLOR_FG}" stroke-width="{stroke_width}" />')

    for i in range(STRING_COUNT):
        x = i * STRING_SPACING
        svg.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{DIAGRAM_HEIGHT}" stroke="{COLOR_FG}" stroke-width="1" />')

    for barre in barres:
        barre_fret = barre['fret']
        if not (position <= barre_fret < position + FRET_COUNT): continue
        fret_index = barre_fret - position + 1
        y = (fret_index * FRET_SPACING) - (FRET_SPACING / 2)
        start_string_index = STRING_COUNT - barre['fromString']
        end_string_index = STRING_COUNT - barre['toString']
        x_start, x_end = start_string_index * STRING_SPACING, end_string_index * STRING_SPACING
        svg.append(f'<rect x="{min(x_start, x_end)}" y="{y - DOT_RADIUS}" width="{abs(x_end - x_start)}" height="{DOT_RADIUS * 2}" rx="{DOT_RADIUS}" ry="{DOT_RADIUS}" fill="{COLOR_FG}" />')

    for i, fret in enumerate(frets):
        string_x = i * STRING_SPACING
        if fret == -1:
            svg.append(f'<g transform="translate({string_x}, {-FRET_SPACING/2}) scale(0.7)">'
                       f'<line x1="-{OPEN_STRING_RADIUS}" y1="-{OPEN_STRING_RADIUS}" x2="{OPEN_STRING_RADIUS}" y2="{OPEN_STRING_RADIUS}" stroke="{COLOR_FG}" stroke-width="3"/>'
                       f'<line x1="-{OPEN_STRING_RADIUS}" y1="{OPEN_STRING_RADIUS}" x2="{OPEN_STRING_RADIUS}" y2="-{OPEN_STRING_RADIUS}" stroke="{COLOR_FG}" stroke-width="3"/>'
                       '</g>')
        elif fret == 0:
            svg.append(f'<circle cx="{string_x}" cy="{-FRET_SPACING/2}" r="{OPEN_STRING_RADIUS}" stroke="{COLOR_FG}" stroke-width="2" fill="none" />')
        elif position <= fret < position + FRET_COUNT:
            fret_index = fret - position + 1
            dot_y = (fret_index * FRET_SPACING) - (FRET_SPACING / 2)
            svg.append(f'<circle cx="{string_x}" cy="{dot_y}" r="{DOT_RADIUS}" fill="{COLOR_FG}" />')

    svg.extend(['</g>', '</svg>'])
    return "\n".join(svg)

# --- NEW: Updated SVG generation for scales to handle boxes and root notes ---
def generate_svg_scale_diagram(scale_data, key, box):
    STRING_COUNT, FRET_COUNT = 6, 5
    WIDTH, HEIGHT = 250, 300
    PAD_X, PAD_Y = 40, 50
    DIAGRAM_WIDTH, DIAGRAM_HEIGHT = WIDTH - (PAD_X * 2), HEIGHT - (PAD_Y * 2)
    STRING_SPACING = DIAGRAM_WIDTH / (STRING_COUNT - 1)
    FRET_SPACING = DIAGRAM_HEIGHT / FRET_COUNT
    DOT_RADIUS = FRET_SPACING / 4.5
    COLOR_FG, COLOR_ROOT, COLOR_BG = "#FFFFFF", "#007bff", "#1a1a1a"

    pattern = scale_data.get('pattern', {}).get(box)
    if not pattern:
        abort(404, f"Box '{box}' not found for this scale.")

    notes, roots = pattern.get('frets', []), pattern.get('roots', [])
    
    all_frets = [fret for string, fret in notes if fret > 0]
    position = min(all_frets) if all_frets else 1
    
    if max(all_frets) - position >= FRET_COUNT:
         FRET_COUNT = max(all_frets) - position + 1
         DIAGRAM_HEIGHT = FRET_SPACING * FRET_COUNT
         HEIGHT = DIAGRAM_HEIGHT + (PAD_Y * 2)

    svg = [f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="100%" height="100%" fill="{COLOR_BG}"/>',
           f'<g transform="translate({PAD_X}, {PAD_Y})" font-family="Arial" fill="{COLOR_FG}">']
    
    if position > 1:
        svg.append(f'<text x="-{PAD_X/2.5}" y="{FRET_SPACING*0.8}" font-size="{FRET_SPACING*0.8}" text-anchor="middle">{position}</text>')

    for i in range(FRET_COUNT + 1):
        y = i * FRET_SPACING
        svg.append(f'<line x1="0" y1="{y}" x2="{DIAGRAM_WIDTH}" y2="{y}" stroke="{COLOR_FG}" stroke-width="2" />')

    for i in range(STRING_COUNT):
        x = i * STRING_SPACING
        svg.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{DIAGRAM_HEIGHT}" stroke="{COLOR_FG}" stroke-width="1" />')

    for string, fret in notes:
        if fret == 0 or (fret >= position and fret < position + FRET_COUNT + 1):
            string_x = (STRING_COUNT - string) * STRING_SPACING
            fret_index = fret - position + 1 if fret >= position else 0
            dot_y = (fret_index * FRET_SPACING) - (FRET_SPACING / 2) if fret > 0 else -FRET_SPACING/2
            is_root = (string, fret) in roots
            fill_color = COLOR_ROOT if is_root else COLOR_FG
            svg.append(f'<circle cx="{string_x}" cy="{dot_y}" r="{DOT_RADIUS}" fill="{fill_color}" />')

    svg.extend(['</g>', '</svg>'])
    return "".join(svg)


@app.route('/')
def index():
    return send_file('index.html')

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
    if not chord_name:
        abort(400, "Chord name not provided.")

    chord_data = CHORD_DEFINITIONS.get(chord_name)
    if not chord_data:
        abort(404, f"Chord definition for '{chord_name}' not found.")

    svg_string = generate_svg_chord_diagram(chord_data)
    return send_file(io.BytesIO(svg_string.encode('utf-8')), mimetype='image/svg+xml')

# --- NEW: Route for getting scale definitions ---
@app.route('/api/scales', methods=['GET'])
def get_scales():
    return jsonify(SCALE_DEFINITIONS)

# --- NEW: Route for generating scale diagrams ---
@app.route('/api/scale-diagram', methods=['POST'])
def scale_diagram():
    scale_name = request.form.get('scale')
    key = request.form.get('key', 'E')
    box = request.form.get('box', 'box1')
    
    if not scale_name:
        abort(400, "Scale name not provided.")
        
    scale_data = SCALE_DEFINITIONS.get(scale_name)
    if not scale_data:
        abort(404, f"Scale definition for '{scale_name}' not found.")
        
    svg_string = generate_svg_scale_diagram(scale_data, key, box)
    return send_file(io.BytesIO(svg_string.encode('utf-8')), mimetype='image/svg+xml')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
from flask import Flask, request, send_file, abort
import io

app = Flask(__name__)

# Chord definitions moved from the frontend to the backend.
# This makes the backend the single source of truth for chord shapes.
CHORD_DEFINITIONS = {
    'C':    { "frets": [-1, 3, 2, 0, 1, 0], "barres": [] },
    'Cm':   { "frets": [-1, 3, 5, 5, 4, 3], "barres": [{"fromString": 5, "toString": 1, "fret": 3 }] },
    'C7':   { "frets": [-1, 3, 2, 3, 1, 0], "barres": [] },
    'Cmaj7':{ "frets": [-1, 3, 2, 0, 0, 0], "barres": [] },
    'G':    { "frets": [3, 2, 0, 0, 0, 3], "barres": [] },
    'G7':   { "frets": [3, 2, 0, 0, 0, 1], "barres": [] },
    'Gmaj7':{ "frets": [3, 2, 0, 0, 0, 2], "barres": [] },
    'Am':   { "frets": [-1, 0, 2, 2, 1, 0], "barres": [] },
    'A':    { "frets": [-1, 0, 2, 2, 2, 0], "barres": [] },
    'A7':   { "frets": [-1, 0, 2, 0, 2, 0], "barres": [] },
    'Amaj7':{ "frets": [-1, 0, 2, 1, 2, 0], "barres": [] },
    'E':    { "frets": [0, 2, 2, 1, 0, 0], "barres": [] },
    'Em':   { "frets": [0, 2, 2, 0, 0, 0], "barres": [] },
    'E7':   { "frets": [0, 2, 0, 1, 0, 0], "barres": [] },
    'Emaj7':{ "frets": [0, 2, 1, 1, 0, 0], "barres": [] },
    'D':    { "frets": [-1, -1, 0, 2, 3, 2], "barres": [] },
    'Dm':   { "frets": [-1, -1, 0, 2, 3, 1], "barres": [] },
    'D7':   { "frets": [-1, -1, 0, 2, 1, 2], "barres": [] },
    'Dmaj7':{ "frets": [-1, -1, 0, 2, 2, 2], "barres": [] },
    'F':    { "frets": [1, 3, 3, 2, 1, 1], "barres": [{"fromString": 6, "toString": 1, "fret": 1 }] },
    'Fmaj7':{ "frets": [1, 3, 2, 2, 1, 1], "barres": [{"fromString": 6, "toString": 1, "fret": 1 }] },
    'B':    { "frets": [-1, 2, 4, 4, 4, 2], "barres": [{"fromString": 5, "toString": 1, "fret": 2 }] },
    'Bm':   { "frets": [-1, 2, 4, 4, 3, 2], "barres": [{"fromString": 5, "toString": 1, "fret": 2 }] },
    'B7':   { "frets": [-1, 2, 1, 2, 0, 2], "barres": [] },
}

def generate_svg_chord_diagram(chord_data):
    """Generates an SVG chord diagram from chord data."""
    # --- Constants ---
    STRING_COUNT, FRET_COUNT = 6, 5
    WIDTH, HEIGHT = 250, 300
    PAD_X, PAD_Y = 40, 50
    DIAGRAM_WIDTH, DIAGRAM_HEIGHT = WIDTH - (PAD_X * 2), HEIGHT - (PAD_Y * 2)
    STRING_SPACING = DIAGRAM_WIDTH / (STRING_COUNT - 1)
    FRET_SPACING = DIAGRAM_HEIGHT / FRET_COUNT
    NUT_HEIGHT, DOT_RADIUS = 8, FRET_SPACING / 3.5
    OPEN_STRING_RADIUS = DOT_RADIUS / 2
    COLOR_FG = "#000000"

    # --- Data processing ---
    frets, barres = chord_data.get('frets', []), chord_data.get('barres', [])
    positive_frets = [f for f in frets if f > 0]
    min_fret = min(positive_frets) if positive_frets else 1
    position = min_fret if min_fret > 1 and max(positive_frets) - min_fret < FRET_COUNT else 1

    # --- SVG Generation ---
    svg = [f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">',
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
        start_string = STRING_COUNT - barre['fromString']
        end_string = STRING_COUNT - barre['toString']
        x_start, x_end = start_string * STRING_SPACING, end_string * STRING_SPACING
        svg.append(f'<rect x="{x_start}" y="{y - DOT_RADIUS}" width="{x_end - x_start}" height="{DOT_RADIUS * 2}" rx="{DOT_RADIUS}" ry="{DOT_RADIUS}" fill="{COLOR_FG}" />')

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

@app.route('/api/chord-diagram', methods=['POST'])
def chord_diagram():
    """
    Generates an SVG chord diagram based on the provided chord name.
    """
    try:
        chord_name = request.form.get('chord')
        if not chord_name:
            abort(400, "Chord name not provided.")

        chord_data = CHORD_DEFINITIONS.get(chord_name)
        if not chord_data:
            abort(404, f"Chord definition for '{chord_name}' not found.")

        # Generate the SVG string
        svg_string = generate_svg_chord_diagram(chord_name, chord_data)

        # Send the SVG as a file in the response
        return send_file(
            io.BytesIO(svg_string.encode('utf-8')),
            mimetype='image/svg+xml'
        )

    except Exception as e:
        # Log the full error for debugging
        app.logger.error(f"Error generating chord diagram: {e}")
        # Return a generic error to the client
        return "Error generating chord diagram.", 500

if __name__ == '__main__':
    app.run(debug=True)
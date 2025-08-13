from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3
import os

# Add CORS support
try:
    from flask_cors import CORS
except ImportError:
    CORS = None

app = Flask(__name__, static_folder='static', template_folder='templates')
if CORS:
    CORS(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('pit_campus.db')
    cursor = conn.cursor()
    
    # Create locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            keywords TEXT NOT NULL,
            description TEXT NOT NULL,
            image_path TEXT NOT NULL,
            facilities TEXT NOT NULL,
            timing TEXT NOT NULL,
            coordinates TEXT
        )
    ''')
    
    # Insert sample data for Parul Institute of Technology
    locations_data = [
        (
            'Main Entrance',
            'main gate, entrance, entry, gate, main entrance',
            'The main entrance to Parul Institute of Technology, featuring modern infrastructure and security facilities. The gateway to excellence in technical education.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/main_entrance.jpg',
            'Security Office, Visitor Reception, Parking Area, Information Desk',
            '24/7 Access',
            '22.2587° N, 73.2119° E'
        ),
        (
            'Technical Library',
            'library, books, study, reading, technical library, e-library',
            'Comprehensive technical library with extensive collection of engineering books, journals, and digital resources. Perfect environment for research and study.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/library.jpg',
            'Technical Books Collection, Digital Library, Research Section, Study Rooms, Internet Access',
            'Mon-Sun: 8:00 AM - 10:00 PM',
            '22.2590° N, 73.2125° E'
        ),
        (
            'Computer Engineering Lab',
            'computer lab, lab, programming, computers, ce lab, software lab',
            'State-of-the-art computer engineering laboratory equipped with latest hardware and software for programming, development, and research activities.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/computer_lab.jpg',
            '50 High-end Workstations, Latest Software Tools, Project Development Area, Network Lab',
            'Mon-Fri: 9:00 AM - 6:00 PM, Sat: 9:00 AM - 2:00 PM',
            '22.2592° N, 73.2130° E'
        ),
        (
            'Electronics & Communication Lab',
            'ec lab, electronics lab, communication lab, circuits lab, embedded lab',
            'Advanced electronics and communication laboratory with modern equipment for circuit design, embedded systems, and communication experiments.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/ec_lab.jpg',
            'Circuit Design Workstations, Oscilloscopes, Signal Generators, Embedded Systems Kits, PCB Design Tools',
            'Mon-Fri: 9:00 AM - 6:00 PM, Sat: 9:00 AM - 2:00 PM',
            '22.2594° N, 73.2128° E'
        ),
        (
            'Mechanical Workshop',
            'mechanical lab, workshop, machine shop, manufacturing lab, mech lab',
            'Well-equipped mechanical workshop with various machines and tools for manufacturing, machining, and hands-on learning experiences.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/mech_workshop.jpg',
            'CNC Machines, Lathe Machines, Milling Machines, Welding Setup, CAD/CAM Lab',
            'Mon-Fri: 9:00 AM - 5:00 PM, Sat: 9:00 AM - 1:00 PM',
            '22.2596° N, 73.2132° E'
        ),
        (
            'Student Hostels',
            'hostel, accommodation, rooms, dormitory, residence, boys hostel, girls hostel',
            'Comfortable accommodation facilities for students with modern amenities. Separate hostels for boys and girls with 24/7 security and mess facilities.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/hostels.jpg',
            'AC/Non-AC Rooms, Wi-Fi, Mess Hall, 24/7 Security, Laundry, Study Room, Recreation Area',
            '24/7 Access for Residents',
            '22.2585° N, 73.2140° E'
        ),
        (
            'Institute Cafeteria',
            'cafeteria, food, dining, canteen, mess, restaurant, food court',
            'Spacious cafeteria serving variety of cuisines at affordable prices. Clean, hygienic food preparation with comfortable seating arrangements.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/cafeteria.jpg',
            'Multi-cuisine Food, AC Dining Area, Snacks Counter, Beverages, Outdoor Seating',
            'Mon-Sun: 7:00 AM - 10:00 PM',
            '22.2588° N, 73.2122° E'
        ),
        (
            'Sports & Recreation Center',
            'sports, gym, playground, basketball, cricket, badminton, fitness center, sports center, recreation center',
            'Modern sports complex with indoor and outdoor facilities for various sports and fitness activities. Promotes physical wellness among students.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/sports_center.jpg',
            'Basketball Court, Badminton Court, Table Tennis, Gymnasium, Cricket Ground, Fitness Equipment',
            'Mon-Sun: 6:00 AM - 9:00 PM',
            '22.2595° N, 73.2135° E'
        ),
        (
            'Auditorium',
            'auditorium, seminar hall, conference hall, events, presentations',
            'Modern auditorium with advanced audio-visual facilities for seminars, conferences, cultural events, and guest lectures.',
            'https://raw.githubusercontent.com/aryanjha205/ome/main/static/images/auditorium.jpg',
            'Seating for 500, Advanced AV System, Air Conditioning, Stage with Projectors, Sound System',
            'Event-based Access, Mon-Fri: 9:00 AM - 6:00 PM',
            '22.2591° N, 73.2127° E'
        ),
        (
            'Administrative Block',
            'admin, office, admission, accounts, principal office, administration, admin block',
            'Central administrative building housing all administrative offices including admissions, accounts, principal office, and student services.',
            'https://github.com/aryanjha205/ome/blob/153ed40f40567b922370d41151d38d687ce459de/static/images/admin_block.jpg',
            'Admission Office, Accounts Department, Principal Office, Student Services, Examination Cell',
            'Mon-Fri: 9:00 AM - 5:00 PM, Sat: 9:00 AM - 1:00 PM',
            '22.2589° N, 73.2124° E'
        )
    ]
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM locations')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO locations (name, keywords, description, image_path, facilities, timing, coordinates)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', locations_data)
    
    conn.commit()
    conn.close()

def search_location(query):
    conn = sqlite3.connect('pit_campus.db')
    cursor = conn.cursor()
    norm_query = query.lower().strip()
    # Try exact and partial matches in name and keywords
    cursor.execute('SELECT * FROM locations')
    results = cursor.fetchall()
    conn.close()
    for result in results:
        name = result[1].lower()
        keywords = result[2].lower()
        if norm_query in name or norm_query in keywords:
            return {
                'id': result[0],
                'name': result[1],
                'description': result[3],
                'image_path': result[4],
                'facilities': result[5].split(', '),
                'timing': result[6],
                'coordinates': result[7]
            }
    # fallback: try if any keyword contains the query as a word
    for result in results:
        keywords = result[2].lower().split(', ')
        if any(norm_query in k for k in keywords):
            return {
                'id': result[0],
                'name': result[1],
                'description': result[3],
                'image_path': result[4],
                'facilities': result[5].split(', '),
                'timing': result[6],
                'coordinates': result[7]
            }
    return None

@app.route('/')
def index():
    # Serve index.html from the root directory
    return send_from_directory('.', 'index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    location = search_location(query)
    
    if location:
        return jsonify({
            'success': True,
            'location': location,
            'message': f"Here's the {location['name']}! {location['description']}"
        })
    else:
        return jsonify({
            'success': False,
            'message': "I couldn't find that location. Try asking about: Main Entrance, Library, Computer Lab, EC Lab, Mechanical Workshop, Hostels, Cafeteria, Sports Center, Auditorium, or Admin Block."
        })

@app.route('/api/locations')
def api_locations():
    conn = sqlite3.connect('pit_campus.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT name, description FROM locations')
    results = cursor.fetchall()
    conn.close()
    
    locations = [{'name': row[0], 'description': row[1]} for row in results]
    return jsonify(locations)

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    # Serve images from static/images
    return send_from_directory('static/images', filename)

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Initialize database
    init_db()
    
    print("🏛️ Parul Institute of Technology Virtual Campus Tour Bot")
    print("📍 Database initialized with PIT campus locations")
    print("🌐 Starting Flask server...")
    print("📱 Access the tour at: http://localhost:5000")
    

    app.run(debug=True, host='0.0.0.0', port=5000)



from flask import Flask, jsonify, request
import sqlite3

app = Flask(_name_)

# Database initialization
conn = sqlite3.connect('flight_booking.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS flights 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, flight_number TEXT, departure_time TEXT, 
             available_seats INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS bookings 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, flight_id INTEGER,
             FOREIGN KEY(user_id) REFERENCES users(id),
             FOREIGN KEY(flight_id) REFERENCES flights(id))''')

conn.commit()

# Helper functions
def get_user_by_username(username):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    return c.fetchone()

def get_flight_by_id(flight_id):
    c.execute("SELECT * FROM flights WHERE id=?", (flight_id,))
    return c.fetchone()

def get_bookings_by_user_id(user_id):
    c.execute("SELECT * FROM bookings WHERE user_id=?", (user_id,))
    return c.fetchall()

# User routes
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if get_user_by_username(username):
        return jsonify({'message': 'User already exists'}), 400

    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = get_user_by_username(username)
    if user and user[2] == password:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/search', methods=['GET'])
def search_flights():
    # Your implementation to search flights based on date and time
    # This is just a placeholder
    return jsonify({'message': 'Searching for flights...'}), 200

@app.route('/book', methods=['POST'])
def book_flight():
    data = request.get_json()
    user_id = data['user_id']
    flight_id = data['flight_id']

    flight = get_flight_by_id(flight_id)
    if not flight:
        return jsonify({'message': 'Flight not found'}), 404

    if flight[3] == 0:
        return jsonify({'message': 'No available seats on this flight'}), 400

    # Decrease available seats and create booking
    c.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE id=?", (flight_id,))
    c.execute("INSERT INTO bookings (user_id, flight_id) VALUES (?, ?)", (user_id, flight_id))
    conn.commit()

    return jsonify({'message': 'Flight booked successfully'}), 200

@app.route('/mybookings/<int:user_id>', methods=['GET'])
def get_user_bookings(user_id):
    bookings = get_bookings_by_user_id(user_id)
    # Format bookings data as needed
    return jsonify({'bookings': bookings}), 200

# Admin routes
@app.route('/admin/addflight', methods=['POST'])
def add_flight():
    # Admin authentication can be added here
    data = request.get_json()
    flight_number = data['flight_number']
    departure_time = data['departure_time']
    available_seats = data['available_seats']

    c.execute("INSERT INTO flights (flight_number, departure_time, available_seats) VALUES (?, ?, ?)", 
              (flight_number, departure_time, available_seats))
    conn.commit()
    return jsonify({'message': 'Flight added successfully'}), 201

@app.route('/admin/removeflight/<int:flight_id>', methods=['DELETE'])
def remove_flight(flight_id):
    # Admin authentication can be added here
    c.execute("DELETE FROM flights WHERE id=?", (flight_id,))
    conn.commit()
    return jsonify({'message': 'Flight removed successfully'}), 200

@app.route('/admin/viewbookings/<int:flight_id>', methods=['GET'])
def get_flight_bookings(flight_id):
    # Admin authentication can be added here
    c.execute("SELECT * FROM bookings WHERE flight_id=?", (flight_id,))
    bookings = c.fetchall()
    return jsonify({'bookings': bookings}), 200

if _name_ == '_main_':
    app.run(debug=True)

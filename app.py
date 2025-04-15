#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
from functools import wraps
import datetime

#Initialize the app from Flask
app = Flask(__name__)
app.secret_key = 'my-secret_key'  # Replace with a strong secret key

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if session['user_type'] == 'customer':
        return render_template('customer_dashboard.html')
    else:
        return render_template('staff_dashboard.html')

@app.route('/login_auth', methods=['GET','POST'])
def login_auth():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']

    cursor = conn.cursor()

    if user_type == 'customer':
        query = 'SELECT * FROM customer WHERE email = %s AND password = %s'
        cursor.execute(query, (username, password))
    else:
        query = 'SELECT * FROM airline_staff WHERE username = %s AND password = %s'
        cursor.execute(query, (username, password))

    data = cursor.fetchone()
    cursor.close()
    error = None

    if data:
        session['username'] = username
        session['user_type'] = user_type
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid login credentials')
        return redirect(url_for('login'))
    
@app.route('/register_auth', methods=['GET', 'POST'])
def register_auth():
    user_type = request.form['user_type']

    if user_type == 'customer':
        # Get customer registration data
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        building_number = request.form['building_number']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        phone_number = request.form['phone_number']
        passport_number = request.form['passport_number']
        passport_expiration = request.form['passport_expiration']
        passport_country = request.form['passport_country']
        date_of_birth = request.form['date_of_birth']

        cursor = conn.cursor()

        # Check if customer already exists
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()

        if data:
            cursor.close()
            flash('This email is already registered')
            return redirect(url_for('register'))

        # Insert new customer
        ins = 'INSERT INTO customer VALUES(%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, name, password, building_number, street, city,
                             state, phone_number, passport_number, passport_expiration,
                             passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        flash('Registration successful! Please login')
        return redirect(url_for('login'))

    else:  # Airline Staff registration
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        airline_name = request.form['airline_name']
        phone_numbers = request.form.getlist('phone_numbers[]')
        emails = request.form.getlist('emails[]')

        cursor = conn.cursor()

        # Check if staff already exists
        query = 'SELECT * FROM airline_staff WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()

        if data:
            cursor.close()
            flash('This username is already taken')
            return redirect(url_for('register'))

        # Insert new staff member
        ins = 'INSERT INTO airline_staff VALUES(%s, md5(%s), %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, first_name, last_name,
                             date_of_birth, airline_name))
        
        # Insert phone numbers
        for phone in phone_numbers:
            if phone:  # Only insert if phone number is not empty
                phone_ins = 'INSERT INTO staff_phone VALUES(%s, %s)'
                cursor.execute(phone_ins, (username, phone))
        
        # Insert email addresses
        for email in emails:
            if email:  # Only insert if email is not empty
                email_ins = 'INSERT INTO staff_email VALUES(%s, %s)'
                cursor.execute(email_ins, (username, email))
        
        conn.commit()
        cursor.close()
        flash('Staff registration successful! Please login')
        return redirect(url_for('login'))

@app.route('/search_flights', methods=['POST'])
def search_flights():
    source = request.form['source']
    destination = request.form['destination']
    departure_date = request.form['departure_date']
    trip_type = request.form['trip_type']
    return_date = request.form.get('return_date')

    cursor = conn.cursor()
    
    # Search for outbound flights
    outbound_query = '''
    SELECT flight_number, airline_name, departure_datetime, arrival_datetime,
           departure_airport_code, arrival_airport_code, base_price, status, airplane_ID 
    FROM flight
    WHERE departure_airport_code = %s 
    AND arrival_airport_code = %s 
    AND DATE(departure_datetime) = %s
    '''
    cursor.execute(outbound_query, (source, destination, departure_date))
    outbound_flights = cursor.fetchall()

    # Convert datetime strings to datetime objects if needed
    for flight in outbound_flights:
        try:
            # Try to use strftime - if it works, it's already a datetime
            flight['departure_datetime'].strftime('%Y-%m-%d %H:%M:%S')
        except (AttributeError, TypeError):
            # If it fails, convert from string to datetime
            flight['departure_datetime'] = datetime.datetime.strptime(str(flight['departure_datetime']), '%Y-%m-%d %H:%M:%S')
            
        try:
            flight['arrival_datetime'].strftime('%Y-%m-%d %H:%M:%S')
        except (AttributeError, TypeError):
            flight['arrival_datetime'] = datetime.datetime.strptime(str(flight['arrival_datetime']), '%Y-%m-%d %H:%M:%S')

    # Search for return flights if round trip
    return_flights = []
    if trip_type == 'round_trip' and return_date:
        return_query = '''
        SELECT flight_number, airline_name, departure_datetime, arrival_datetime,
               departure_airport_code, arrival_airport_code, base_price, status, airplane_ID 
        FROM flight
        WHERE departure_airport_code = %s 
        AND arrival_airport_code = %s 
        AND DATE(arrival_datetime) = %s
        AND DATE(departure_datetime) >= DATE(%s)
        ORDER BY departure_datetime ASC
        '''
        cursor.execute(return_query, (destination, source, return_date, departure_date))
        return_flights = cursor.fetchall()
        
        # Convert datetime strings to datetime objects if needed
        for flight in return_flights:
            try:
                flight['departure_datetime'].strftime('%Y-%m-%d %H:%M:%S')
            except (AttributeError, TypeError):
                flight['departure_datetime'] = datetime.datetime.strptime(str(flight['departure_datetime']), '%Y-%m-%d %H:%M:%S')
                
            try:
                flight['arrival_datetime'].strftime('%Y-%m-%d %H:%M:%S')
            except (AttributeError, TypeError):
                flight['arrival_datetime'] = datetime.datetime.strptime(str(flight['arrival_datetime']), '%Y-%m-%d %H:%M:%S')

    cursor.close()

    return render_template('search_results.html', 
                         outbound_flights=outbound_flights,
                         return_flights=return_flights,
                         trip_type=trip_type)

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
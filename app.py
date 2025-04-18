#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
import datetime

#Initialize the app from Flask
app = Flask(__name__)
app.secret_key = 'my-secret_key'

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

@app.route('/register/customer')
def register_customer():
    return render_template('register_customer.html')

@app.route('/register/staff')
def register_staff():
    return render_template('register_staff.html')

@app.route('/register/customer/auth', methods=['POST'])
def register_customer_auth():
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

    try:
        # Check if customer already exists
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (email,))
        data = cursor.fetchone()

        if data:
            flash('This email is already registered', 'error')
            return redirect(url_for('register_customer'))

        # Insert new customer
        ins = 'INSERT INTO customer VALUES(%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, name, password, building_number, street, city,
                             state, phone_number, passport_number, passport_expiration,
                             passport_country, date_of_birth))
        conn.commit()
        flash('Registration successful! Please login', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        flash('An error occurred during registration', 'error')
        return redirect(url_for('register_customer'))
    finally:
        cursor.close()

@app.route('/register/staff/auth', methods=['POST'])
def register_staff_auth():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    airline_name = request.form['airline_name']
    phone_number = request.form['phone_numbers']
    email = request.form['emails']

    cursor = conn.cursor()

    try:
        # First check if the airline exists
        airline_query = 'SELECT * FROM airline WHERE name = %s'
        cursor.execute(airline_query, (airline_name,))
        airline_data = cursor.fetchone()
        
        if not airline_data:
            flash('This airline does not exist in our system', 'error')
            return redirect(url_for('register_staff'))

        # Check if staff already exists
        query = 'SELECT * FROM airline_staff WHERE username = %s'
        cursor.execute(query, (username,))
        data = cursor.fetchone()

        if data:
            flash('This username is already taken', 'error')
            return redirect(url_for('register_staff'))

        # Insert new staff member
        ins = 'INSERT INTO airline_staff VALUES(%s, md5(%s), %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, first_name, last_name,
                             date_of_birth, airline_name))
        
        # Insert phone number
        if phone_number:
            phone_ins = 'INSERT INTO staff_phone VALUES(%s, %s)'
            cursor.execute(phone_ins, (username, phone_number))
        
        # Insert email
        if email:
            email_ins = 'INSERT INTO airline_email VALUES(%s, %s)'
            cursor.execute(email_ins, (username, email))
        
        conn.commit()
        flash('Staff registration successful! Please login', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        flash('An error occurred during registration', 'error')
        return redirect(url_for('register_staff'))
    finally:
        cursor.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    if session['user_type'] == 'customer':
        return render_template('customer_dashboard.html')
    else:
        return render_template('staff_dashboard.html')

@app.route('/login_auth', methods=['GET','POST'])
def login_auth():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    user_type = request.form['user_type']

    cursor = conn.cursor()

    try:
        if user_type == 'customer':
            # Check if the email exists first
            check_query = 'SELECT * FROM customer WHERE email = %s'
            cursor.execute(check_query, (username,))
            user_exists = cursor.fetchone()
            
            if not user_exists:
                flash('No customer account found with this email', 'error')
                return redirect(url_for('login'))
            
            # Try password match with MD5 hashing
            query = 'SELECT * FROM customer WHERE email = %s AND password = md5(%s)'
            cursor.execute(query, (username, password))
            data = cursor.fetchone()
            
            if not data:
                flash('Incorrect password', 'error')
                return redirect(url_for('login'))
        else:
            # Check if the username exists first
            check_query = 'SELECT * FROM airline_staff WHERE username = %s'
            cursor.execute(check_query, (username,))
            user_exists = cursor.fetchone()
            
            if not user_exists:
                flash('No staff account found with this username', 'error')
                return redirect(url_for('login'))
            
            # Try password match with MD5 hashing
            query = 'SELECT * FROM airline_staff WHERE username = %s AND password = md5(%s)'
            cursor.execute(query, (username, password))
            data = cursor.fetchone()
            
            if not data:
                flash('Incorrect password', 'error')
                return redirect(url_for('login'))

        # If we get here, login was successful
        session['username'] = username
        session['user_type'] = user_type
        if user_type == 'customer':
            session['name'] = data['name']
        else:
            session['first_name'] = data['first_name']
            session['last_name'] = data['last_name']
            session['airline_name'] = data['airline_name']
            
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
            
    except Exception as e:
        flash('An error occurred during login. Please try again.', 'error')
        return redirect(url_for('login'))
    finally:
        cursor.close()

@app.route('/search_flights', methods=['POST'])
def search_flights():
    source = request.form['source']
    destination = request.form['destination']
    departure_date = request.form['departure_date']
    trip_type = request.form['trip_type']
    return_date = request.form.get('return_date')

    cursor = conn.cursor()
    
    # Get current datetime for future flight validation
    current_datetime = datetime.datetime.now()
    
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
            flight['departure_datetime'].strftime('%Y-%m-%d %H:%M:%S')
        except (AttributeError, TypeError):
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

@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('You must be logged in as airline staff to access this page')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        airline_name = session.get('airline_name')
        airplane_id = request.form['airplane_id']
        seats = request.form['seats']
        
        cursor = conn.cursor()
        try:
            # Check if airplane already exists
            query = 'SELECT * FROM airplane WHERE airline_name = %s AND airplane_id = %s'
            cursor.execute(query, (airline_name, airplane_id))
            if cursor.fetchone():
                flash('An airplane with this ID already exists')
                return redirect(url_for('add_airplane'))
                
            # Add new airplane
            query = 'INSERT INTO airplane VALUES(%s, %s, %s)'
            cursor.execute(query, (airline_name, airplane_id, seats))
            conn.commit()
            flash('Airplane added successfully')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash('Error adding airplane')
            return redirect(url_for('add_airplane'))
        finally:
            cursor.close()
            
    return render_template('add_airplane.html')

@app.route('/staff/view_flights', methods=['GET', 'POST'])
def staff_view_flights():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please login as airline staff', 'error')
        return redirect(url_for('login'))

    cursor = conn.cursor()
    airline_name = session['airline_name']
    
    # Default: next 30 days
    start_date = datetime.datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    source_airport = ''
    destination_airport = ''
    
    # Handle filters if POST request
    if request.method == 'POST':
        start_date = request.form.get('start_date', start_date)
        end_date = request.form.get('end_date', end_date)
        source_airport = request.form.get('source_airport', '')
        destination_airport = request.form.get('destination_airport', '')
    
    # Base query
    query = '''
        SELECT flight_number, departure_datetime, arrival_datetime, 
               departure_airport_code, arrival_airport_code, status, 
               airplane_ID, base_price
        FROM flight 
        WHERE airline_name = %s 
        AND DATE(departure_datetime) BETWEEN %s AND %s
    '''
    params = [airline_name, start_date, end_date]
    
    # Add filters if provided
    if source_airport:
        query += ' AND departure_airport_code = %s'
        params.append(source_airport)
    if destination_airport:
        query += ' AND arrival_airport_code = %s'
        params.append(destination_airport)
    
    # Order by departure date
    query += ' ORDER BY departure_datetime ASC'
    
    cursor.execute(query, tuple(params))
    flights = cursor.fetchall()
    
    # Get all airports for the filter dropdowns
    cursor.execute('SELECT DISTINCT code, city FROM airport')
    airports = cursor.fetchall()
    
    cursor.close()
    return render_template('staff_view_flights.html', 
                         flights=flights, 
                         airports=airports,
                         start_date=start_date,
                         end_date=end_date,
                         source_airport=source_airport,
                         destination_airport=destination_airport)

@app.route('/staff/flight_customers/<flight_number>')
def staff_flight_customers(flight_number):
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please login as airline staff', 'error')
        return redirect(url_for('login'))

    cursor = conn.cursor()
    airline_name = session['airline_name']
    
    # Verify the flight belongs to the staff's airline
    cursor.execute('SELECT * FROM flight WHERE airline_name = %s AND flight_number = %s', 
                  (airline_name, flight_number))
    flight = cursor.fetchone()
    
    if not flight:
        flash('Flight not found or unauthorized', 'error')
        return redirect(url_for('staff_view_flights'))
    
    # Get customers on this flight
    query = '''
        SELECT c.name, c.email, t.ticket_ID, t.sold_price
        FROM ticket t
        JOIN customer c ON t.email = c.email
        WHERE t.flight_number = %s AND t.airline_name = %s
    '''
    cursor.execute(query, (flight_number, airline_name))
    customers = cursor.fetchall()
    
    cursor.close()
    return render_template('staff_flight_customers.html', 
                         flight=flight, 
                         customers=customers)

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
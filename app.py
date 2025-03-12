from flask import Flask, jsonify, request, render_template, redirect, url_for
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    #Establish and return a MySQL database connection.
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route("/users", methods=['GET'])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Unable to connect to the database."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        return jsonify(users)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# GET route to display the new user form
@app.route("/", methods=['GET'])
def new_user_form():
    return render_template("user.html")

# POST route to handle form submission and insert user data
@app.route("/add_user", methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return "Username and password are required", 400
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    conn = get_db_connection()
    if not conn:
        return "Unable to connect to the database", 500
    try:
        cursor = conn.cursor()
        query = "INSERT INTO user (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))
        conn.commit()
        return redirect(url_for('new_user_form'))
    except mysql.connector.Error as err:
        conn.rollback()
        return f"Error: {err}", 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
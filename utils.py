import mysql.connector
from mysql.connector import Error
import hashlib
import streamlit as st

def create_connection():
    # Replace with your database details
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="i know it",
        database="NutritionTracker"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def fetch_user_data():
    if 'user_email' not in st.session_state:
        st.error("No user is logged in.")
        return None

    email = st.session_state['user_email']
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE UserEmail = %s", (email,))
        user_data = cursor.fetchone()
        return user_data
    except Error as e:
        st.error(f"Error fetching user data: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
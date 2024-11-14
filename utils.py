import mysql.connector
from mysql.connector import Error
import hashlib
import streamlit as st

def create_connection():
    # Replace with your database details
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2910",
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
            
            
def fetch_name(email, table_name, email_column):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Use the provided table name and email column to dynamically build the query
        query = f"SELECT FirstName, LastName FROM {table_name} WHERE {email_column} = %s"
        cursor.execute(query, (email,))
        
        result = cursor.fetchone()
        if result:
            st.session_state["first_name"] = result["FirstName"]
            st.session_state["last_name"] = result["LastName"]
    except Error as e:
        st.error(f"Error fetching name: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
def display_greeting():
    first_name = st.session_state.get("first_name")
    last_name = st.session_state.get("last_name")
    if first_name and last_name:
        st.header(f"Hello {first_name} {last_name}!")
    else:
        st.header("Hello!")
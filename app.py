from common_imports import *
from user_dashboard import user_dashboard
from nutritionist_dashboard import nutritionist_dashboard
from utils import create_connection, hash_password


# Reset session state for form fields 
def reset_form_fields():
    for key in ["email", "password", "first_name", "last_name", "username", "dob", "gender", "height", "weight"]:
        if key in st.session_state:
            del st.session_state[key]

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'login'

# Registration function
def register_user(role, email, password, first_name, last_name, **kwargs):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        if role == "User":
            cursor.execute("SELECT * FROM Users WHERE UserEmail = %s", (email,))
      
        if cursor.fetchone():
            st.error("An account with this email already exists!")
            return False
        
        # Insert new user or nutritionist
        if role == "User":
            cursor.execute("""
                INSERT INTO Users (Username, Password, UserEmail, FirstName, LastName, DOB, Gender, Height, Weight)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (kwargs['username'], hash_password(password), email, first_name, last_name, kwargs['dob'], kwargs['gender'], kwargs['height'], kwargs['weight']))
      
        conn.commit()
        st.success(f"{role} registered successfully! Please log in.")
        st.session_state['current_page'] = 'login'
        return True
    except Error as e:
        st.error(f"Error: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Login function 
def login_user(role, email, password):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check credentials based on the role
        if role == "User":
            cursor.execute("SELECT * FROM Users WHERE UserEmail = %s AND Password = %s", (email, hash_password(password)))
        elif role == "Nutritionist":
            cursor.execute("SELECT * FROM Nutritionists WHERE NutritionistEmail = %s AND Password = %s", (email, hash_password(password)))
        
        user = cursor.fetchone()
        
        if user:
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = role
            st.session_state['user_email'] = email
            st.session_state['user_data'] = user
            
            # Store the nutritionist email separately in session state (for nutritionists)
            if role == "Nutritionist":
                st.session_state["nutritionist_email"] = email
            
            # Redirect to the dashboard page
            st.session_state['current_page'] = 'dashboard'
            st.rerun()
        else:
            st.error("Invalid email or password.")
            return None
        
    except Error as e:
        st.error(f"Error: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def show_login_page():
    st.title("Nutrition Tracker Login")
    role = st.selectbox("Login as", ["User", "Nutritionist"], key="role")
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if not email or not password:
                st.error("All fields are required!")
            else:
                user = login_user(role, email, password)
                if not user:
                    st.error("Invalid email or password.")
    with col2:
        if st.button("Go to Register"):
            st.session_state['current_page'] = 'register'
            st.rerun()

def show_register_page():
    st.title("Nutrition Tracker Registration")
    
    role = st.selectbox("I am a", ["User"], key="role")
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    first_name = st.text_input("First Name", key="first_name")
    last_name = st.text_input("Last Name", key="last_name")

    if role == "User":
        username = st.text_input("Username", key="username")
        dob = st.date_input("Date of Birth", value=None, min_value=dt.date(1900, 1, 1), max_value=dt.datetime.today(), key="dob")
        gender = st.selectbox("Gender", ["M", "F", "Other"], key="gender")
        height = st.number_input("Height (in cm)", min_value=0.0, key="height")
        weight = st.number_input("Weight (in kg)", min_value=0.0, key="weight")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register"):
            if not all([email, password, first_name, last_name, username, dob, gender, height, weight]):
                st.error("All fields are required!")
            else:
                if register_user("User", email, password, first_name, last_name, 
                               username=username, dob=dob, gender=gender, 
                               height=height, weight=weight):
                    reset_form_fields()
    
    with col2:
        if st.button("Back to Login"):
            st.session_state['current_page'] = 'login'
            reset_form_fields()
            st.rerun()

def main():
    initialize_session_state()
    
    # Add logout button in sidebar if logged in
    if st.session_state['logged_in']:
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            initialize_session_state()
            st.rerun()
    
    # Route to appropriate page based on session state
    if not st.session_state['logged_in']:
        if st.session_state['current_page'] == 'register':
            show_register_page()
        else:
            show_login_page()
    else:
        if st.session_state['user_role'] == "User":
            user_dashboard()
        elif st.session_state['user_role'] == 'Nutritionist':
            nutritionist_dashboard()
        else:
            st.title("something went wrong")
            

if __name__ == "__main__":
    main()
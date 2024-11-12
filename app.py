# from common_imports import *
# from user_dashboard import user_dashboard
# from utils import create_connection, hash_password

# # Reset session state for form fields
# def reset_form_fields():
#     for key in ["email", "password", "first_name", "last_name", "username", "dob", "gender", "height", "weight"]:
#         st.session_state[key] = ""

# # Registration function
# def register_user(role, email, password, first_name, last_name, **kwargs):
#     try:
#         conn = create_connection()
#         cursor = conn.cursor()
        
#         # Check if email already exists
#         if role == "User":
#             cursor.execute("SELECT * FROM Users WHERE UserEmail = %s", (email,))
#         else:
#             cursor.execute("SELECT * FROM Nutritionists WHERE NutritionistEmail = %s", (email,))
        
#         if cursor.fetchone():
#             st.error("An account with this email already exists!")
#             return False
        
#         # Insert new user or nutritionist
#         if role == "User":
#             cursor.execute("""
#                 INSERT INTO Users (Username, Password, UserEmail, FirstName, LastName, DOB, Gender, Height, Weight)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
#             """, (kwargs['username'], hash_password(password), email, first_name, last_name, kwargs['dob'], kwargs['gender'], kwargs['height'], kwargs['weight']))
        
#         else:  # Nutritionist
#             cursor.execute("""
#                 INSERT INTO Nutritionists (FirstName, LastName, NutritionistEmail, Password)
#                 VALUES (%s, %s, %s, %s)
#             """, (first_name, last_name, email, hash_password(password)))
        
#         conn.commit()
#         st.success(f"{role} registered successfully! Please log in.")
#         return True
#     except Error as e:
#         st.error(f"Error: {e}")
#         return False
#     finally:
#         if conn.is_connected():
#             cursor.close()
#             conn.close()

# # Login function
# def login_user(role, email, password):
#     try:
#         conn = create_connection()
#         cursor = conn.cursor(dictionary=True)
        
#         if role == "User":
#             cursor.execute("SELECT * FROM Users WHERE UserEmail = %s AND Password = %s", (email, hash_password(password)))
#         else:
#             cursor.execute("SELECT * FROM Nutritionists WHERE NutritionistEmail = %s AND Password = %s", (email, hash_password(password)))
        
#         user = cursor.fetchone()
#         return user
#     except Error as e:
#         st.error(f"Error: {e}")
#         return None
#     finally:
#         if conn.is_connected():
#             cursor.close()
#             conn.close()


# # App Layout
# st.title("Nutrition Tracker Login and Registration")

# menu = ["Login", "Register"]
# choice = st.sidebar.selectbox("Menu", menu, on_change=reset_form_fields)

# if choice == "Register":
#     st.subheader("Create a New Account")

#     role = st.selectbox("I am a", ["User", "Nutritionist"], key="role")
#     email = st.text_input("Email", key="email")
#     password = st.text_input("Password", type="password", key="password")
#     first_name = st.text_input("First Name", key="first_name")
#     last_name = st.text_input("Last Name", key="last_name")

#     if role == "User":
#         username = st.text_input("Username", key="username")
#         dob = st.date_input("Date of Birth", value=None, min_value=dt.date(1900, 1, 1), max_value=dt.datetime.today(), key="dob")
#         gender = st.selectbox("Gender", ["M", "F", "Other"], key="gender")
#         height = st.number_input("Height (in cm)", min_value=0.0, key="height")
#         weight = st.number_input("Weight (in kg)", min_value=0.0, key="weight")

#     if st.button("Register"):
#         if role == "User":
#             register_user("User", email, password, first_name, last_name, username=username, dob=dob, gender=gender, height=height, weight=weight)
#         else:
#             register_user("Nutritionist", email, password, first_name, last_name)

# elif choice == "Login":
#     # st.subheader("Login to Your Account")
#     # role = st.selectbox("Login as", ["User", "Nutritionist"], key="role")
#     # email = st.text_input("Email", key="email")
#     # password = st.text_input("Password", type="password", key="password")
    
    
#     role = st.selectbox("Login as", ["User", "Nutritionist"], key="role")
#     email = st.text_input("Email", key="email")
#     password = st.text_input("Password", type="password", key="password")
    
#     if st.button("Login"):
#         user = login_user(role, email, password)
        
#         if user:
#             st.session_state['logged_in'] = True
#             st.session_state['user_role'] = role
#             st.session_state['user_email'] = email
#             st.success(f"Welcome {user['FirstName']} {user['LastName']}!")
#         else:
#             st.error("Invalid email or password.")

# # Display the user dashboard if logged in
# if st.session_state.get('logged_in'):
#     if st.session_state['user_role'] == "User":
#         user_dashboard()

from common_imports import *
from user_dashboard import user_dashboard
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
        else:
            cursor.execute("SELECT * FROM Nutritionists WHERE NutritionistEmail = %s", (email,))
        
        if cursor.fetchone():
            st.error("An account with this email already exists!")
            return False
        
        # Insert new user or nutritionist
        if role == "User":
            cursor.execute("""
                INSERT INTO Users (Username, Password, UserEmail, FirstName, LastName, DOB, Gender, Height, Weight)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (kwargs['username'], hash_password(password), email, first_name, last_name, kwargs['dob'], kwargs['gender'], kwargs['height'], kwargs['weight']))
        else:
            cursor.execute("""
                INSERT INTO Nutritionists (FirstName, LastName, NutritionistEmail, Password)
                VALUES (%s, %s, %s, %s)
            """, (first_name, last_name, email, hash_password(password)))
        
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
        
        if role == "User":
            cursor.execute("SELECT * FROM Users WHERE UserEmail = %s AND Password = %s", (email, hash_password(password)))
        else:
            cursor.execute("SELECT * FROM Nutritionists WHERE NutritionistEmail = %s AND Password = %s", (email, hash_password(password)))
        
        user = cursor.fetchone()
        if user:
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = role
            st.session_state['user_email'] = email
            st.session_state['user_data'] = user
            st.session_state['current_page'] = 'dashboard'
            st.rerun()
        return user
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
            user = login_user(role, email, password)
            if not user:
                st.error("Invalid email or password.")
    with col2:
        if st.button("Go to Register"):
            st.session_state['current_page'] = 'register'
            st.rerun()

def show_register_page():
    st.title("Nutrition Tracker Registration")
    
    role = st.selectbox("I am a", ["User", "Nutritionist"], key="role")
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
            if role == "User":
                if register_user("User", email, password, first_name, last_name, 
                               username=username, dob=dob, gender=gender, 
                               height=height, weight=weight):
                    reset_form_fields()
            else:
                if register_user("Nutritionist", email, password, first_name, last_name):
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
        else:
            st.title("Nutritionist Dashboard")
            st.write("Nutritionist dashboard functionality coming soon...")

if __name__ == "__main__":
    main()
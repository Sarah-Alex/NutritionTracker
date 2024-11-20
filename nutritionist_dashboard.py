import streamlit as st
import datetime as dt
from mysql.connector import Error
from common_imports import *
from utils import create_connection, fetch_name, display_greeting

def fetch_assigned_users():
    try:
        nutritionist_email = st.session_state.get('user_email')
        if not nutritionist_email:
            st.error("You are not logged in. Please log in to view users.")
            return []
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT Users.UserEmail, Users.FirstName, Users.LastName 
            FROM Users 
            JOIN NutritionistUserMapping ON Users.UserEmail = NutritionistUserMapping.UserEmail
            WHERE NutritionistUserMapping.NutritionistEmail = %s
        """, (nutritionist_email,))
        users = cursor.fetchall()
        return users
    except Error as e:
        st.error(f"Error fetching users: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def fetch_user_food_logs(user_email, meal_type=None, food_item=None, start_date=None, end_date=None):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT Food_Items.ItemName, User_Eats.Date, User_Eats.Quantity, Food_Items.Calories, User_Eats.MealType 
        FROM User_Eats 
        JOIN Food_Items ON User_Eats.ItemID = Food_Items.ItemID 
        WHERE User_Eats.UserEmail = %s
    """
    params = [user_email]
    
    if meal_type:
        query += " AND User_Eats.MealType = %s"
        params.append(meal_type)
    if food_item:
        query += " AND Food_Items.ItemName LIKE %s"
        params.append(f"%{food_item}%")
    if start_date:
        query += " AND User_Eats.Date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND User_Eats.Date <= %s"
        params.append(end_date)
    
    cursor.execute(query, tuple(params))
    food_logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return food_logs

def fetch_user_exercise_logs(user_email, exercise_name=None, start_date=None, end_date=None):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT Exercises.ExerciseName, Workouts.Date, Workouts.Duration, Exercises.CaloriesBurnt 
        FROM Workouts 
        JOIN Exercises ON Workouts.ExerciseID = Exercises.ExerciseID 
        WHERE Workouts.UserEmail = %s
    """
    params = [user_email]
    
    if exercise_name:
        query += " AND Exercises.ExerciseName LIKE %s"
        params.append(f"%{exercise_name}%")
    if start_date:
        query += " AND Workouts.Date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND Workouts.Date <= %s"
        params.append(end_date)
    
    cursor.execute(query, tuple(params))
    exercise_logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return exercise_logs

def save_nutritionist_report(user_email, recommendation):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Reports (UserEmail, Recommendation, Date)
            VALUES (%s, %s, %s)
        """, (user_email, recommendation, dt.date.today()))
        conn.commit()
        st.success("Report saved successfully!")
    except Error as e:
        st.error(f"Error saving report: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def suggest_supplement(user_email, supplement_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO User_Supplements (UserEmail, SupplementID, StartDate)
            VALUES (%s, %s, %s)
        """, (user_email, supplement_id, dt.date.today()))
        conn.commit()
        st.success("Supplement suggestion saved successfully!")
    except Error as e:
        st.error(f"Error suggesting supplement: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def fetch_supplements():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Supplements")
    supplements = cursor.fetchall()
    cursor.close()
    connection.close()
    return supplements

def display_food_history(user_email):
    st.subheader("View User's Food Intake History")
    meal_type = st.selectbox("Select Meal Type", ['All', 'Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner'], index=0)
    food_item = st.text_input("Search by Food Item", "")
    start_date = st.date_input("Start Date", dt.date(2000, 1, 1))
    end_date = st.date_input("End Date", dt.date.today())

    meal_type = None if meal_type == 'All' else meal_type
    food_logs = fetch_user_food_logs(user_email, meal_type, food_item, start_date, end_date)
    
    if food_logs:
        for log in food_logs:
            st.write(f"{log['Date']}: {log['MealType']} - {log['ItemName']} ({log['Quantity']}g, {log['Calories']} kcal)")
    else:
        st.info("No food intake records found.")

def display_exercise_history(user_email):
    st.subheader("View User's Exercise History")
    exercise_name = st.text_input("Search by Exercise Name", "")
    start_date = st.date_input("Start Date", dt.date(2000, 1, 1))
    end_date = st.date_input("End Date", dt.date.today())

    exercise_logs = fetch_user_exercise_logs(user_email, exercise_name, start_date, end_date)
    
    if exercise_logs:
        for log in exercise_logs:
            st.write(f"{log['Date']}: {log['ExerciseName']} - {log['Duration']} minutes, {log['CaloriesBurnt']} kcal burned")
    else:
        st.info("No exercise records found.")

def display_assigned_users():
    st.title("View Users Under Your Supervision")
    users = fetch_assigned_users()
    if not users:
        st.write("You have no assigned users")
    else:
        selected_user_email = st.selectbox("Select a User", [f"{user['FirstName']} {user['LastName']} ({user['UserEmail']})" for user in users])

        if selected_user_email:
            selected_user_email = selected_user_email.split('(')[-1][:-1]
            st.subheader("Choose Action for the Selected User")
            action = st.radio("What would you like to do?", ["View Food Intake History", "View Exercise History", "Leave a Report"])

            if action == "View Food Intake History":
                display_food_history(selected_user_email)
            elif action == "View Exercise History":
                display_exercise_history(selected_user_email)
            elif action == "Leave a Report":
                st.subheader("Leave a Report")
                recommendation = st.text_area("Enter your recommendation for the user")
                if st.button("Submit Recommendation"):
                    save_nutritionist_report(selected_user_email, recommendation)

def suggest_supplements():
    st.title("Suggest Supplements")
    
    users = fetch_assigned_users()
    user_emails = [user['UserEmail'] for user in users]
    selected_user = st.selectbox("Select a User", user_emails)
    
    supplements = fetch_supplements()
    supplement_options = {f"{supplement['SupplementName']} - {supplement['Description']}": supplement['SupplementID'] 
                          for supplement in supplements}
    
    selected_supplement = st.selectbox("Select a Supplement", list(supplement_options.keys()))
    
    if st.button("Suggest Supplement"):
        supplement_id = supplement_options[selected_supplement]
        suggest_supplement(selected_user, supplement_id)

def nutritionist_dashboard():
    if "first_name" not in st.session_state or "last_name" not in st.session_state:
        nutritionist_email = st.session_state.get("nutritionist_email")
        if nutritionist_email:
            fetch_name(nutritionist_email, "Nutritionists", "NutritionistEmail")
        else:
            st.error("Nutritionist email is not set in session state.")
    
    display_greeting()
    
    st.sidebar.title("Nutritionist Dashboard")
    page = st.sidebar.radio("Navigation", ["View Assigned Users", "Suggest Supplements"])
    
    if page == "View Assigned Users":
        display_assigned_users()
    elif page == "Suggest Supplements":
        suggest_supplements()

if __name__ == "__main__":
    nutritionist_dashboard()
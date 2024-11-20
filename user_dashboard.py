# import streamlit as st
import datetime as dt
import pandas as pd
import plotly.express as px
from mysql.connector import Error
from common_imports import *
from utils import create_connection, fetch_name, display_greeting

# Fetch food items from the database
def fetch_food_items():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Food_Items")
        food_items = cursor.fetchall()
        return food_items
    except Error as e:
        st.error(f"Error fetching food items: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fetch exercises from the database
def fetch_exercises():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Exercises")
        exercises = cursor.fetchall()
        return exercises
    except Error as e:
        st.error(f"Error fetching exercises: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Save user's food log to User_Eats table
def save_food_log(meal_type, food_item_id, quantity, calories, date):
    try:
        user_email = st.session_state.get('user_email')
        if not user_email:
            st.error("You are not logged in. Please log in to log meals.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO User_Eats (UserEmail, ItemID, Date, Quantity, MealType)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_email, food_item_id, date, quantity, meal_type))
        conn.commit()
        st.success(f"{meal_type} log saved successfully!")
    except Error as e:
        st.error(f"Error saving food log: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Save workout log to Workouts table
def save_workout_log(exercise_id, duration, date):
    try:
        user_email = st.session_state.get('user_email')
        if not user_email:
            st.error("You are not logged in. Please log in to log workouts.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Workouts (UserEmail, ExerciseID, Date, Duration)
            VALUES (%s, %s, %s, %s)
        """, (user_email, exercise_id, date, duration))
        conn.commit()
        st.success("Workout log saved successfully!")
    except Error as e:
        st.error(f"Error saving workout log: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fetch meal logs with optional filtering by date range
def fetch_meal_logs(start_date=None, end_date=None):
    try:
        user_email = st.session_state.get("user_email")
        if not user_email:
            st.error("You are not logged in. Please log in to view your meal logs.")
            return []

        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT User_Eats.Date, User_Eats.MealType, Food_Items.ItemName, User_Eats.Quantity, Food_Items.Calories
            FROM User_Eats 
            JOIN Food_Items ON User_Eats.ItemID = Food_Items.ItemID
            WHERE User_Eats.UserEmail = %s
        """
        params = [user_email]
        
        if start_date and end_date:
            query += " AND User_Eats.Date BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        cursor.execute(query, params)
        meal_logs = cursor.fetchall()
        return meal_logs
    except Error as e:
        st.error(f"Error fetching meal logs: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fetch exercise logs with optional filtering by date range
def fetch_exercise_logs(start_date=None, end_date=None):
    try:
        user_email = st.session_state.get("user_email")
        if not user_email:
            st.error("You are not logged in. Please log in to view your exercise logs.")
            return []

        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT Workouts.Date, Exercises.ExerciseName, Workouts.Duration, 
                   (Exercises.CaloriesBurnt * Workouts.Duration) AS CaloriesBurned
            FROM Workouts
            JOIN Exercises ON Workouts.ExerciseID = Exercises.ExerciseID
            WHERE Workouts.UserEmail = %s
        """
        params = [user_email]
        
        if start_date and end_date:
            query += " AND Workouts.Date BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        cursor.execute(query, params)
        exercise_logs = cursor.fetchall()
        return exercise_logs
    except Error as e:
        st.error(f"Error fetching exercise logs: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fetch reports for the logged-in user
def fetch_reports():
    try:
        user_email = st.session_state.get("user_email")
        if not user_email:
            st.error("You are not logged in. Please log in to view reports.")
            return []

        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT Recommendation, Date
            FROM Reports
            WHERE UserEmail = %s
            ORDER BY Date DESC
        """, (user_email,))
        reports = cursor.fetchall()
        return reports
    except Error as e:
        st.error(f"Error fetching reports: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fetch user supplements
def fetch_supplements():
    try:
        user_email = st.session_state.get("user_email")
        if not user_email:
            st.error("You are not logged in. Please log in to view your supplements.")
            return []
        
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.SupplementName, s.Description, u.StartDate 
            FROM Supplements as s, user_supplements as u 
            WHERE u.SupplementID = s.SupplementID and u.UserEmail = %s
            ORDER BY u.StartDate DESC;
        """, (user_email,))
        
        supplements = cursor.fetchall()
        return supplements
    except Error as e:
        st.error(f"Error fetching supplements: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fetch user's assigned nutritionist
def fetch_user_nutritionist():
    try:
        user_email = st.session_state.get('user_email')
        if not user_email:
            st.error("You are not logged in.")
            return

        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT n.FirstName, n.LastName, n.NutritionistEmail 
            FROM Nutritionists n 
            JOIN NutritionistUserMapping m ON n.NutritionistEmail = m.NutritionistEmail
            WHERE m.UserEmail = %s
        """, (user_email,))
        nutritionist = cursor.fetchone()
        return nutritionist
    except Error as e:
        st.error(f"Error fetching nutritionist details: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def display_dashboard_summary():
    st.title("Dashboard Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Today's Nutrition")
        today_meals = fetch_meal_logs(start_date=dt.date.today(), end_date=dt.date.today())
        total_calories = sum(meal['Calories'] * meal['Quantity'] / 100 for meal in today_meals)
        st.metric("Total Calories Consumed", f"{total_calories:.0f} kcal")
        
    
    with col2:
        st.subheader("Today's Exercise")
        today_exercises = fetch_exercise_logs(start_date=dt.date.today(), end_date=dt.date.today())
        total_calories_burned = sum(exercise['CaloriesBurned'] for exercise in today_exercises)
        st.metric("Total Calories Burned", f"{total_calories_burned:.0f} kcal")
        
        # Bar chart for exercise duration
        if today_exercises:
            exercise_df = pd.DataFrame(today_exercises)
            fig = px.bar(exercise_df, x='ExerciseName', y='Duration', title="Exercise Duration")
            st.plotly_chart(fig)
        else:
            st.info("No exercises logged today.")

def display_log_meals():
    st.title("Log Your Meals")
    meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"])
    food_items = fetch_food_items()
    
    selected_foods = st.multiselect("Select Food Items", [item['ItemName'] for item in food_items])
    
    log_entries = []
    for food in selected_foods:
        food_item = next(item for item in food_items if item['ItemName'] == food)
        quantity = st.number_input(f"Quantity of {food} (g)", min_value=1, value=100)
        calories = food_item['Calories'] * quantity / 100
        log_entries.append((meal_type, food_item['ItemID'], quantity, calories))
    
    if st.button("Save Meal Log"):
        for entry in log_entries:
            save_food_log(*entry, dt.date.today())
        st.success("Meal log saved successfully!")

def display_log_exercises():
    st.title("Log Your Exercises")
    exercises = fetch_exercises()
    
    selected_exercise = st.selectbox("Select Exercise", [ex['ExerciseName'] for ex in exercises])
    duration = st.number_input("Duration (minutes)", min_value=1, value=30)
    
    if st.button("Save Exercise Log"):
        exercise_id = next(ex['ExerciseID'] for ex in exercises if ex['ExerciseName'] == selected_exercise)
        save_workout_log(exercise_id, duration, dt.date.today())
        st.success("Exercise log saved successfully!")

def view_meal_logs():
    st.title("View Your Meal Logs")
    date_range = st.date_input("Select Date Range", [dt.date.today() - dt.timedelta(days=7), dt.date.today()])
    meal_logs = fetch_meal_logs(start_date=date_range[0], end_date=date_range[1])
    
    if meal_logs:
        df = pd.DataFrame(meal_logs)
        df['Date'] = pd.to_datetime(df['Date'])
        
        st.dataframe(df)
        
        # Calories per day chart
        daily_calories = df.groupby('Date')['Calories'].sum().reset_index()
        fig = px.line(daily_calories, x='Date', y='Calories', title="Daily Calorie Intake")
        st.plotly_chart(fig)
    else:
        st.info("No meal logs found for the selected date range.")

def view_exercise_logs():
    st.title("View Your Exercise Logs")
    date_range = st.date_input("Select Date Range", [dt.date.today() - dt.timedelta(days=7), dt.date.today()])
    exercise_logs = fetch_exercise_logs(start_date=date_range[0], end_date=date_range[1])
    
    if exercise_logs:
        df = pd.DataFrame(exercise_logs)
        df['Date'] = pd.to_datetime(df['Date'])
        
        st.dataframe(df)
        
        # Calories burned per day chart
        daily_calories_burned = df.groupby('Date')['CaloriesBurned'].sum().reset_index()
        fig = px.line(daily_calories_burned, x='Date', y='CaloriesBurned', title="Daily Calories Burned")
        st.plotly_chart(fig)
    else:
        st.info("No exercise logs found for the selected date range.")

def display_nutritionist_details():
    st.title("Nutritionist Details")
    nutritionist = fetch_user_nutritionist()
    
    if nutritionist:
        st.write(f"Your nutritionist: {nutritionist['FirstName']} {nutritionist['LastName']}")
        st.write(f"Contact: {nutritionist['NutritionistEmail']}")
    else:
        st.info("No nutritionist assigned. Please contact support for assistance.")

def view_reports():
    st.title("Your Reports")
    reports = fetch_reports()
    if reports:
        for report in reports:
            st.write(f"Date: {report['Date']}")
            st.write(f"Recommendation: {report['Recommendation']}")
            st.write("---")
    else:
        st.info("No reports available.")

def view_supplements():
    st.title("Your Supplements")
    supplements = fetch_supplements()
    
    if supplements:
        for supplement in supplements:
            st.write(f"Supplement Name: {supplement['SupplementName']}")
            st.write(f"Description: {supplement['Description']}")
            st.write(f"Start Date: {supplement['StartDate']}")
            st.write("---")
    else:
        st.info("No supplements suggested.")

def user_dashboard():
    if "first_name" not in st.session_state or "last_name" not in st.session_state:
        user_email = st.session_state.get("user_email")
        if user_email:
            fetch_name(user_email, "Users", "UserEmail")
    display_greeting()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Log Meals", "Log Exercises", "View Meal Logs", "View Exercise Logs", "Nutritionist Details", "View Reports", "View Supplements"])
    
    if page == "Dashboard":
        display_dashboard_summary()
    elif page == "Log Meals":
        display_log_meals()
    elif page == "Log Exercises":
        display_log_exercises()
    elif page == "View Meal Logs":
        view_meal_logs()
    elif page == "View Exercise Logs":
        view_exercise_logs()
    elif page == "Nutritionist Details":
        display_nutritionist_details()
    elif page == "View Reports":
        view_reports()
    elif page == "View Supplements":
        view_supplements()

if __name__ == '__main__':
    user_dashboard()
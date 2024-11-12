from common_imports import *
from utils import create_connection

# Fetch food items
def fetch_food_items():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM food_items")
        food_items = cursor.fetchall()
        return food_items
    except Error as e:
        st.error(f"Error fetching food items: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fetch exercises
def fetch_exercises():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM exercises")
        exercises = cursor.fetchall()
        return exercises
    except Error as e:
        st.error(f"Error fetching exercises: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Save user's food log
def save_food_log(meal, food_item_id, quantity, calories, date):
    try:
        user_email = st.session_state.get('user_email')
        if not user_email:
            st.error("You are not logged in. Please log in to log meals.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_eats (userEmail, meal, foodItemID, quantity, calories, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_email, meal, food_item_id, quantity, calories, date))
        conn.commit()
        st.success(f"{meal} log saved successfully!")
    except Error as e:
        st.error(f"Error saving food log: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Save workout log
def save_workout_log(exercise_id, duration, date):
    try:
        user_email = st.session_state.get('user_email')
        if not user_email:
            st.error("You are not logged in. Please log in to log workouts.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workouts (userEmail, exerciseID, date, duration)
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

# Fetch past workout logs
def fetch_workout_logs():
    try:
        user_email = st.session_state.get('user_email')
        if not user_email:
            st.error("You are not logged in. Please log in to view workout logs.")
            return []

        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM workouts WHERE userEmail = %s ORDER BY date DESC", (user_email,))
        logs = cursor.fetchall()
        return logs
    except Error as e:
        st.error(f"Error fetching workout logs: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Dashboard layout
def user_dashboard():
    if 'user_email' not in st.session_state:
        st.write("Log in to access your dashboard.")
        return
    
    st.title("User Dashboard")
    st.write(f"Welcome, {st.session_state['user_email']}!")
    
    # Section: Meal Logging
    st.subheader("Log Today's Meals")
    food_items = fetch_food_items()
    # Updated to match your database column names
    food_options = {item['ItemName']: (item['ItemID'], item['Calories']) for item in food_items}

    total_calories = 0
    for meal in ["Breakfast", "Lunch", "Dinner"]:
        st.write(f"### {meal}")
        selected_food = st.selectbox(f"Select food for {meal}", list(food_options.keys()), key=f"{meal}_food")
        quantity = st.number_input(f"Quantity (g) of {selected_food}", min_value=1, key=f"{meal}_quantity")
        
        food_id, calories_per_gram = food_options[selected_food]
        calories = quantity * calories_per_gram
        total_calories += calories
        
        if st.button(f"Log {meal}", key=f"{meal}_log"):
            save_food_log(meal, food_id, quantity, calories, dt.date.today())

    st.write(f"**Total Calories for the Day**: {total_calories} kcal")

    # Section: Exercise Selection and Workout Logging
    st.subheader("Curate Your Workout")
    exercises = fetch_exercises()
    
    # Display available exercises
    for exercise in exercises:
        st.write(f"{exercise['exerciseName']} - {exercise['description']}")

    selected_exercise = st.selectbox("Select an exercise", [exercise['exerciseName'] for exercise in exercises], key="exercise_select")
    exercise_id = next((ex['exerciseID'] for ex in exercises if ex['exerciseName'] == selected_exercise), None)
    duration = st.number_input("Duration (minutes)", min_value=1, key="duration")

    if st.button("Save Workout"):
        save_workout_log(exercise_id, duration, dt.date.today())

    # Section: View Past Workouts
    st.subheader("View Past Workouts")
    if st.button("Show Workout Logs"):
        workout_logs = fetch_workout_logs()
        if workout_logs:
            for log in workout_logs:
                exercise_name = next((ex['exerciseName'] for ex in exercises if ex['exerciseID'] == log['exerciseID']), "Unknown")
                st.write(f"**Date**: {log['date']}, **Exercise**: {exercise_name}, **Duration**: {log['duration']} minutes")
        else:
            st.info("No workout logs found.")

def main():
    user_dashboard()

if __name__ == "__main__":
    main()
    
    



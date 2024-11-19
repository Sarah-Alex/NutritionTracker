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

# Fetch meal logs with optional filtering by meal type
def fetch_meal_logs(meal_type=None):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM User_Eats JOIN Food_Items ON User_Eats.ItemID = Food_Items.ItemID"
    if meal_type:
        query += " WHERE MealType = %s"
        cursor.execute(query, (meal_type,))
    else:
        cursor.execute(query)
    meal_logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return meal_logs

# Fetch exercise logs with optional filtering by date
def fetch_exercise_logs(date=None):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM Workouts JOIN Exercises ON Workouts.ExerciseID = Exercises.ExerciseID"
    if date:
        query += " WHERE Date = %s"
        cursor.execute(query, (date,))
    else:
        cursor.execute(query)
    exercise_logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return exercise_logs


def fetch_nutritionists():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Nutritionists")
        nutritionists = cursor.fetchall()
        return nutritionists
    except Error as e:
        st.error(f"Error fetching nutritionists: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
# def fetch_nutritionists():
#     try:
#         conn = create_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM Nutritionists")
#         nutritionists = cursor.fetchall()
#         return nutritionists
#     except Error as e:
#         st.error(f"Error fetching nutritionists: {e}")
#     finally:
#         if conn.is_connected():
#             cursor.close()
#             conn.close()


# Clear main content when a new option is selected
def clear_main_content():
    for key in st.session_state.keys():
        if key.startswith("main_content"):
            del st.session_state[key]


# Function to log meals with multiple items per meal
def display_log_meals():
    st.title("Log Your Meals")
    meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"], key="main_content_meal_type")
    food_items = fetch_food_items()
    food_options = {item['ItemName']: (item['ItemID'], item['Calories']) for item in food_items}

    if "main_content_food_logs" not in st.session_state:
        st.session_state["main_content_food_logs"] = []

    def add_food_item():
        selected_food = st.session_state[f"main_content_food_{len(st.session_state['main_content_food_logs'])}_name"]
        quantity = st.session_state[f"main_content_food_{len(st.session_state['main_content_food_logs'])}_quantity"]
        food_id, calories_per_gram = food_options[selected_food]
        calories = quantity * calories_per_gram
        st.session_state["main_content_food_logs"].append((meal_type, food_id, quantity, calories))

    for i, (meal_type, food_id, quantity, calories) in enumerate(st.session_state["main_content_food_logs"]):
        food_name = next(item for item in food_options if food_options[item][0] == food_id)
        st.write(f"Item {i + 1}: {quantity}g of {food_name} - {calories} kcal")

    selected_food = st.selectbox("Select Food Item", list(food_options.keys()), key=f"main_content_food_{len(st.session_state['main_content_food_logs'])}_name")
    quantity = st.number_input("Quantity (g)", min_value=1, key=f"main_content_food_{len(st.session_state['main_content_food_logs'])}_quantity")
    st.button("Add Food Item", on_click=add_food_item, help="Add new food item to this meal")

    if st.button("Save Meal Log"):
        for meal_type, food_id, quantity, calories in st.session_state["main_content_food_logs"]:
            save_food_log(meal_type, food_id, quantity, calories, dt.date.today())
        st.success("Meal log saved successfully!")
        st.session_state["main_content_food_logs"] = []

# Function to log exercises with multiple entries
def display_log_exercises():
    st.title("Log Your Exercises")
    exercises = fetch_exercises()
    exercise_options = {exercise['ExerciseName']: exercise['ExerciseID'] for exercise in exercises}

    if "main_content_exercise_logs" not in st.session_state:
        st.session_state["main_content_exercise_logs"] = []

    def add_exercise():
        selected_exercise = st.session_state[f"main_content_exercise_{len(st.session_state['main_content_exercise_logs'])}_name"]
        duration = st.session_state[f"main_content_exercise_{len(st.session_state['main_content_exercise_logs'])}_duration"]
        exercise_id = exercise_options[selected_exercise]
        st.session_state["main_content_exercise_logs"].append((exercise_id, duration))

    for i, (exercise_id, duration) in enumerate(st.session_state["main_content_exercise_logs"]):
        exercise_name = next(name for name in exercise_options if exercise_options[name] == exercise_id)
        st.write(f"Exercise {i + 1}: {duration} minutes of {exercise_name}")

    selected_exercise = st.selectbox("Select Exercise", list(exercise_options.keys()), key=f"main_content_exercise_{len(st.session_state['main_content_exercise_logs'])}_name")
    duration = st.number_input("Duration (minutes)", min_value=1, key=f"main_content_exercise_{len(st.session_state['main_content_exercise_logs'])}_duration")
    st.button("Add Exercise", on_click=add_exercise, help="Add new exercise")

    if st.button("Save Exercise Log"):
        for exercise_id, duration in st.session_state["main_content_exercise_logs"]:
            save_workout_log(exercise_id, duration, dt.date.today())
        st.success("Exercise log saved successfully!")
        st.session_state["main_content_exercise_logs"] = []

# Function to view meal logs with optional filtering
def view_meal_logs():
    st.title("View Your Meal Logs")
    meal_type_filter = st.selectbox("Filter by Meal Type", ["All", "Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"])
    meal_logs = fetch_meal_logs(meal_type_filter if meal_type_filter != "All" else None)
    if meal_logs:
        for log in meal_logs:
            st.write(f"Date: {log['Date']}, Meal: {log['MealType']}, Food: {log['ItemName']}, Quantity: {log['Quantity']}g, Calories: {log['Calories']} kcal")
    else:
        st.info("No meal logs found.")

# Function to view exercise logs with optional date filtering
def view_exercise_logs():
    st.title("View Your Exercise Logs")
    date_filter = st.date_input("Filter by Date", value=dt.date.today())
    exercise_logs = fetch_exercise_logs(date_filter)
    if exercise_logs:
        for log in exercise_logs:
            st.write(f"Date: {log['Date']}, Exercise: {log['ExerciseName']}, Duration: {log['Duration']} minutes")
    else:
        st.info("No exercise logs found.")

# View reports left by the nutritionist for the user
def view_reports():
    st.title("Your Reports")
    reports = fetch_reports()
    if reports:
        for report in reports:
            st.write(f"Date: {report['Date']}, Recommendation: {report['Recommendation']}")
    else:
        st.info("No reports available.")
            

# Main user dashboard with sidebar options
def user_dashboard():
    if "first_name" not in st.session_state or "last_name" not in st.session_state:
        user_email = st.session_state.get("user_email")
        if user_email:
            fetch_name(user_email, "Users", "UserEmail")
    
    display_greeting()
    
    with st.sidebar:
        st.header("Navigation")
        if st.button("Log Meals"):
            st.session_state.page = "log_meals"
            clear_main_content()
        if st.button("Log Exercises"):
            st.session_state.page = "log_exercises"
            clear_main_content()
        if st.button("View Meal Logs"):
            st.session_state.page = "view_meal_logs"
            clear_main_content()
        if st.button("View Exercise Logs"):
            st.session_state.page = "view_exercise_logs"
            clear_main_content()
        
    if st.session_state.get("page") == "log_meals":
        display_log_meals()
    elif st.session_state.get("page") == "log_exercises":
        display_log_exercises()
    elif st.session_state.get("page") == "view_meal_logs":
        view_meal_logs()
    elif st.session_state.get("page") == "view_exercise_logs":
        view_exercise_logs()

# Run user dashboard if logged in
if __name__ == '__main()__':
    user_dashboard()

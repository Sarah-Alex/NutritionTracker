CREATE DATABASE IF NOT EXISTS NutritionTracker;
USE NutritionTracker;
-- Users table
CREATE TABLE Users (
    Username VARCHAR(50) NOT NULL,
    Password VARCHAR(64) NOT NULL,
    UserEmail VARCHAR(100) PRIMARY KEY NOT NULL,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    DOB DATE,
    Gender CHAR(1),
    Height FLOAT,
    Weight FLOAT
);

-- Nutritionists table
CREATE TABLE Nutritionists (
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
	NutritionistEmail VARCHAR(100) PRIMARY KEY NOT NULL,
    Password VARCHAR(64) NOT NULL
    
);

-- Food_Items table
CREATE TABLE Food_Items (
    ItemID INT PRIMARY KEY,
    ItemName VARCHAR(100) NOT NULL,
    Calories INT NOT NULL
    -- Protein FLOAT,
--     Carbs FLOAT,
--     Fat FLOAT
);

-- Supplements table
CREATE TABLE Supplements (
    SupplementID INT PRIMARY KEY,
    SupplementName VARCHAR(100) NOT NULL,
    Description TEXT
);

-- Exercises table
CREATE TABLE Exercises (
    ExerciseID INT PRIMARY KEY,
    ExerciseName VARCHAR(100) NOT NULL,
    CaloriesBurnt DECIMAL(10, 6)
);

-- User_Foods table (for tracking user's food intake)
CREATE TABLE User_Eats (
    UserEmail VARCHAR(100),
    ItemID INT,
    Date DATE,
    Quantity INT,
    MealType ENUM('Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner') NOT NULL,
    
    PRIMARY KEY (UserEmail, ItemID, Date, MealType),
    FOREIGN KEY (UserEmail) REFERENCES Users(UserEmail) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (ItemID) REFERENCES Food_Items(ItemID) ON UPDATE CASCADE ON DELETE CASCADE
);

-- User_Supplements table (for tracking user's supplement intake)
CREATE TABLE User_Supplements (
    UserEmail VARCHAR(100),
    SupplementID INT,
    StartDate DATE,
    PRIMARY KEY (UserEmail, SupplementID, StartDate),
    FOREIGN KEY (UserEmail) REFERENCES Users(UserEmail) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (SupplementID) REFERENCES Supplements(SupplementID) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Workouts table (for tracking user's exercises)
CREATE TABLE Workouts (
    UserEmail VARCHAR(100),
    ExerciseID INT,
    Date DATE,
    Duration INT,
    PRIMARY KEY (UserEmail, ExerciseID, Date),
    FOREIGN KEY (UserEmail) REFERENCES Users(UserEmail) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (ExerciseID) REFERENCES Exercises(ExerciseID) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE NutritionistUserMapping(
	UserEmail VARCHAR(100),
    NutritionistEmail VARCHAR(100),
    PRIMARY KEY (UserEmail, NutritionistEmail),
    FOREIGN KEY (UserEmail) REFERENCES Users(UserEmail) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (NutritionistEmail) REFERENCES Nutritionists(NutritionistEmail) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Reports (
	UserEmail  VARCHAR(100),
    Recommendation text,
    Date DATE,
    PRIMARY KEY (UserEmail, Date),
    FOREIGN KEY (UserEmail) REFERENCES Users(UserEmail) ON UPDATE CASCADE ON DELETE CASCADE
    
);


-- Clean up any existing temporary table first
DROP TEMPORARY TABLE IF EXISTS temp_food_items;



-- Load data from CSV file
CREATE TEMPORARY TABLE temp_food_items (
    temp_id INT AUTO_INCREMENT PRIMARY KEY,
    FoodCategory VARCHAR(100),
    FoodItem VARCHAR(100),      -- Changed to match CSV
    per100grams VARCHAR(100),   -- Added this column
    Cals_per100grams VARCHAR(100),  -- Changed to VARCHAR to accept "cal" suffix
    KJ_per100grams VARCHAR(100)     -- Changed to VARCHAR to accept "kJ" suffix
);


LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\calories.csv'
INTO TABLE temp_food_items
FIELDS TERMINATED BY ','
ENCLOSED BY '"'           -- Added this line to handle quoted fields
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(FoodCategory, FoodItem, per100grams, Cals_per100grams, KJ_per100grams);


INSERT INTO Food_Items (ItemID, ItemName, Calories)
SELECT 
    temp_id as ItemID,
    FoodItem as ItemName,
    CAST(SUBSTRING_INDEX(Cals_per100grams, ' ', 1) AS UNSIGNED) as Calories
FROM temp_food_items;

-- Clean up: drop temporary table
DROP TEMPORARY TABLE IF EXISTS temp_food_items;


DROP TEMPORARY TABLE IF EXISTS temp_supplements;

CREATE TEMPORARY TABLE temp_supplements (
    temp_id INT AUTO_INCREMENT PRIMARY KEY,
    supplement VARCHAR(100),
    Claimed_improved_aspect_of_fitness TEXT
);

LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\sports_supplements.csv'
INTO TABLE temp_supplements
FIELDS TERMINATED BY ','
ENCLOSED BY '"'            
LINES TERMINATED BY '\r\n'  -- Use '\r\n' if '\n' alone doesn't work
IGNORE 1 ROWS
(supplement, Claimed_improved_aspect_of_fitness);

-- Insert relevant data into the Supplements table
INSERT INTO Supplements (SupplementID, SupplementName, Description)
SELECT 
    temp_id AS SupplementID,
    supplement AS SupplementName,
    Claimed_improved_aspect_of_fitness AS Description
FROM temp_supplements;

-- Clean up: Drop temporary table after data insertion
DROP TEMPORARY TABLE IF EXISTS temp_supplements;



-- Drop temporary table if it exists
DROP TEMPORARY TABLE IF EXISTS temp_exercises;

-- Create a temporary table to match the CSV structure
CREATE TEMPORARY TABLE temp_exercises (
    temp_id INT AUTO_INCREMENT PRIMARY KEY,
    Activity VARCHAR(100),
    Calories_per_kg DECIMAL(10, 6)
);

-- Load data from CSV into the temporary table
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\exercises.csv'
INTO TABLE temp_exercises
FIELDS TERMINATED BY ','
ENCLOSED BY '"'            
LINES TERMINATED BY '\r\n'  -- Adjust if needed to '\n'
IGNORE 1 ROWS
(Activity, Calories_per_kg);

-- Insert data into Exercises table, converting calories per kg to integer if needed
INSERT INTO Exercises (ExerciseID, ExerciseName, CaloriesBurnt)
SELECT 
    temp_id AS ExerciseID,
    Activity AS ExerciseName,
    Calories_per_kg AS CaloriesBurnt  -- Convert to INT by rounding
FROM temp_exercises;

-- Drop the temporary table after data insertion
DROP TEMPORARY TABLE IF EXISTS temp_exercises;


USE NutritionTracker;
DROP TRIGGER IF EXISTS AssignNutritionistAfterInsert;
DROP FUNCTION IF EXISTS GetMinUserNutritionist;

DELIMITER //

CREATE FUNCTION GetMinUserNutritionist() 
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE min_nutritionist_email VARCHAR(255);

    -- Select the nutritionist with the fewest users (if the table is empty, it will return NULL)
    SELECT NutritionistEmail
    INTO min_nutritionist_email
    FROM Nutritionists
    WHERE NutritionistEmail NOT IN (SELECT NutritionistEmail FROM NutritionistUserMapping)
    LIMIT 1;

    -- If all nutritionists have users, select the one with the least number of users
    IF min_nutritionist_email IS NULL THEN
        SELECT NutritionistEmail
        INTO min_nutritionist_email
        FROM NutritionistUserMapping
        GROUP BY NutritionistEmail
        ORDER BY COUNT(UserEmail) ASC
        LIMIT 1;
    END IF;

    RETURN min_nutritionist_email;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER AssignNutritionistAfterInsert
AFTER INSERT ON Users
FOR EACH ROW
BEGIN
    DECLARE assigned_nutritionist VARCHAR(255);

    -- Call the function to get the nutritionist with the fewest users or unassigned nutritionist
    SET assigned_nutritionist = GetMinUserNutritionist();

    -- Insert a new record into the NutritionistUserMapping table
    INSERT INTO NutritionistUserMapping (NutritionistEmail, UserEmail)
    VALUES (assigned_nutritionist, NEW.UserEmail);
END //

DELIMITER ;

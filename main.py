import cv2
import os
import mysql.connector

def capture_face(name, user_id):
    # Create 'faces' directory if it doesn't exist
    if not os.path.exists("faces"):
        os.makedirs("faces")

    # Open webcam
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("Error: Could not open camera")
        return

    cv2.namedWindow("Register")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Register", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to capture
            img_name = f"{name}_{user_id}.png"
            img_path = os.path.join("faces", img_name)
            cv2.imwrite(img_path, frame)  # Save the captured face
            print(f"Face image saved at {img_path}")
            # Save details to the database
            save_to_db(name, user_id, img_path)
            break

    # Release the camera and close windows
    cam.release()
    cv2.destroyAllWindows()

def save_to_db(name, user_id, img_path):
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",  # Update with your database host
            user="root",       # Update with your MySQL username
            password="",       # Update with your MySQL password
            database="imagedetection"  # Update with your database name
        )
        if conn.is_connected():
            print("Database connection successful!")
        else:
            print("Database connection failed.")
            return

        cursor = conn.cursor()

        # Print the query and values before execution for debugging
        sql = "INSERT INTO register (name, atten_id, image) VALUES (%s, %s, %s)"
        val = (name, user_id, img_path)
        print(f"Executing query: {sql} with values {val}")

        cursor.execute(sql, val)

        # Commit the transaction
        conn.commit()

        # Check if the data was inserted
        if cursor.rowcount > 0:
            print(f"Data saved successfully in the database for {name}")
        else:
            print("Data insertion failed.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the connection
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

# Input validation
name = input("Enter Name: ").strip()
user_id = input("Enter ID: ").strip()

if name and user_id:
    capture_face(name, user_id)
else:
    print("Name and ID cannot be empty!") 
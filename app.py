from flask import Flask, request, render_template
import cv2
import os
import re
import subprocess  # Import subprocess to run detection.py
import mysql.connector

from datetime import datetime
app = Flask(__name__)

# Function to check if a user with the same name and ID already exists
def user_already_exists(name, user_id):
    img_name = f"{name}_{user_id}.png"
    img_path = os.path.join("faces", img_name)
    return os.path.exists(img_path)

# Function to capture the face image using OpenCV
def capture_face(name, user_id):
    # Create 'faces' directory if it doesn't exist
    if not os.path.exists("faces"):
        os.makedirs("faces")

    # Open webcam
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        return "Error: Could not open camera"

    cv2.namedWindow("Register",  cv2.WINDOW_NORMAL)  # Make the window resizable)
    #cv2.setWindowProperty("Register", cv2.WND_PROP_TOPMOST, 1)  # Keep window on top
    while True:
        ret, frame = cam.read()
        if not ret:
            return "Failed to grab frame"
        
        img_name = f"{name}_{user_id}.png"  # Create image name
        img_path = os.path.join("faces", img_name)  # Define the full image path

        cv2.imshow("Register", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to capture
            cv2.imwrite(img_path, frame)  # Save the captured face
            break

    # Release the camera and close windows
    cam.release()
    cv2.destroyAllWindows()
    return f"Face image saved at {img_path}"

# Home route - displays the registration form
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/capture', methods=['POST'])
def capture():
    name = request.form['name'].strip()
    user_id = request.form['id'].strip()

    if not name or not user_id:
        return render_template('register.html', message="Name and ID cannot be empty!")

    # Check if the user already exists
    if user_already_exists(name, user_id):
        return render_template('result.html', message="User Already Registered.")

    # Proceed to capture the face image
    result = capture_face(name, user_id)

    if "saved" in result:  # If the capture was successful, proceed to save in the database
        img_name = f"{name}_{user_id}.png"
        img_path = os.path.join("faces", img_name)

        # Save to database
        save_to_db(name, user_id, img_path)
        return render_template('result.html', message=f"Face image captured and data saved for {name}.")
    else:
        return render_template('result.html', message=result)


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

        # Insert user data into the 'register' table
        sql = "INSERT INTO register (name, atten_id, image) VALUES (%s, %s, %s)"
        val = (name, user_id, img_path)
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


@app.route('/scan')
def scan():
    try:
        # Call the detection.py script using subprocess
        result = subprocess.run(["python", "detection.py"], capture_output=True, text=True, check=True)

        print("result", result.stdout)  # Print standard output for debugging

        # Use regex to extract the last attendance information from stdout
        match = re.search(r"Last Attendance Marked: Name: (.*), ID: (.*)", result.stdout)
        if match:
            name = match.group(1).strip()  # Extract name
            user_id = match.group(2).strip()  # Extract ID
        else:
            name = None
            user_id = None

        # If face was detected and matched
        if name and user_id:
            # Generate current timestamp
            timestamp = datetime.now()
            current_date = timestamp.strftime("%Y-%m-%d")
            current_time = timestamp.strftime("%H:%M:%S")

            # Assume the scanned image is saved during detection
            img_name = f"{name}_{user_id}_{current_date}.png"
            img_path = os.path.join("attendance_faces", img_name)  

            # Save the attendance to the database
            save_attendance_to_db(name, user_id, current_date, current_time, img_path)

            return render_template('result.html', Name=name, ID=user_id, msg="Attendance Marked")
        else:
            return render_template('result.html', msg="Attendance could not be marked. No match found.")
    
    except subprocess.CalledProcessError as e:
        print(e.stderr)  # Print the error message for debugging
        return render_template('result.html', msg=f"Error during scanning: {e.stderr}")
    
def save_attendance_to_db(name, user_id, date, time, img_path):
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

        # Insert attendance data into the 'attendance' table
        sql = "INSERT INTO attendance (name, atten_id, date, time, image) VALUES (%s, %s, %s, %s, %s)"
        val = (name, user_id, date, time, img_path)
        cursor.execute(sql, val)

        # Commit the transaction
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Attendance recorded for {name} on {date} at {time}.")
        else:
            print("Attendance record insertion failed.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the connection
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")
   

if __name__ == '__main__':
    app.run(debug=True)

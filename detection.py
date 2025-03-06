import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# Specify the absolute path to your images directory
#path = "C:/Users/pavit/PycharmProjects/face detection/faces"
path = "C:/facedetection/faces"
# Check if the directory exists
if not os.path.exists(path):
    print(f"Directory {path} does not exist. Please create it and add images.")
    exit()

# Load images and names from the directory
images = []
classNames = []
ids = []  # List to store IDs
myList = os.listdir(path)
print(myList)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is not None:  # Ensure the image was loaded successfully
        images.append(curImg)
        name = os.path.splitext(cl)[0]
        classNames.append(name)
        
        # Extracting ID from the filename, assuming it is after the last underscore
        id_number = name.split('_')[-1]  # Split by underscore and take the last part
        ids.append(id_number)  # Store the extracted ID

print(f"Class Names: {classNames}")
print(f"IDs: {ids}")  # Print IDs for debugging

# Function to find encodings for known images
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
        encode = face_recognition.face_encodings(img)
        if encode:  # Ensure that at least one encoding is found
            encodeList.append(encode[0])
        else:
            print("Warning: No encoding found for an image.")
    return encodeList

# Attendance list to store in-memory attendance data
attendance_list = []

# Function to mark attendance
def markAttendance(name, id_number):
    if name not in [record[0] for record in attendance_list]:  # Check if name is already in the list
        time_now = datetime.now()
        tString = time_now.strftime('%H:%M:%S')
        dString = time_now.strftime('%d/%m/%Y')
        attendance_list.append((name, id_number, tString, dString))  # Store attendance in a list
        print(f'Attendance Marked: Name: {name}, ID: {id_number}, Time: {tString}, Date: {dString}')
        return True  # Return True if attendance is marked

# Find encodings for known faces
encodeListKnown = findEncodings(images)
if not encodeListKnown:
    print("Error: No face encodings found in the images directory.")
    exit()

print('Encoding Complete')

# Start video capture
cap = cv2.VideoCapture(0)

# Flag to indicate if attendance has been marked
attendance_marked = False

while not attendance_marked:  # Run until attendance is marked
    success, img = cap.read()
    if not success:
        print("Error: Could not read frame.")
        break

    # Resize frame for faster processing
    imgS = cv2.resize(img, (0, 0), None, 0.5, 0.5)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces and get encodings in the current frame
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    print(f"Detected faces: {facesCurFrame}")
    print(f"Current encodings: {encodesCurFrame}")

    if encodesCurFrame:  # Check if there are any encodings found
        # Loop through detected faces and their encodings
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDist = face_recognition.face_distance(encodeListKnown, encodeFace)

            if len(faceDist) > 0:  # Ensure faceDist is not empty
                matchIndex = np.argmin(faceDist)

                if matches[matchIndex]:
                    name = classNames[matchIndex]
                    
                    # Ensure matchIndex is valid for the ids list
                    if matchIndex < len(ids):
                        id_number = ids[matchIndex]  # Get the corresponding ID
                    else:
                        print(f"Error: matchIndex {matchIndex} is out of range for IDs list.")
                        continue  # Skip this iteration if there's an index error

                    attendance_marked = markAttendance(name, id_number)  # Mark attendance and update flag

                    # Draw a rectangle and label around the detected face
                    y1, x2, y2, x1 = faceLoc
                    cv2.rectangle(img, (x1 * 4, y1 * 4), (x2 * 4, y2 * 4), (0, 255, 0), 2)
                    cv2.putText(img, f'{name} (ID: {id_number})', (x1 * 4, y1 * 4 - 10), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 255, 0), 2)

                    break  # Exit the face loop once attendance is marked
    else:
        print("No faces found in the current frame.")

    # Display the webcam feed with detection
    cv2.imshow('Webcam', img)

    # Break the loop when 'q' is pressed (optional)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the windows
cap.release()
cv2.destroyAllWindows()

# Print the final attendance list at the end of the session
print("Attendance List:")
for record in attendance_list:
    print(f"Name: {record[0]}, ID: {record[1]}, Time: {record[2]}, Date: {record[3]}")
# After marking attendance in your scan function

if attendance_list:
    last_record = attendance_list[-1]
    # Extract the name from the stored class name
    name_with_id = last_record[0]  # e.g., 'pavithra arulselvam_0987'
    name = name_with_id.split('_')[0]  # Extracting just the name

    print(f"Last Attendance Marked: Name: {name}, ID: {last_record[1]}")

    # Pass only the name and ID to the HTML template
    #return render_template('result.html', Name=name, ID=last_record[1], message="Attendance Marked")

@echo off
:: Minimize Command Prompt
powershell -windowstyle hidden -command ""

:: Check if the app is already running
curl -s --head http://127.0.0.1:5000/ | find "200 OK" >nul
if %errorlevel%==0 (
    echo App is already running. Stopping Apache, MySQL, and Python...
    taskkill /F /IM mysqld.exe /T >nul 2>&1
    taskkill /F /IM httpd.exe /T >nul 2>&1
    taskkill /F /IM python.exe /T >nul 2>&1
    exit
)

:: App is not running, start services
echo Starting Apache and MySQL...
start /min "" "C:\xampp\xampp_start.exe"
timeout /t 2 >nul

:: Run Python script in the background
start /min cmd /c "C:\facedetection\venv\Scripts\python.exe C:\facedetection\app.py"

:: Open the web app in the browser
start "" "http://127.0.0.1:5000/"



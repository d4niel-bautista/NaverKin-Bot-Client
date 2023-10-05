@echo off
setlocal enabledelayedexpansion

REM Specify the path to your .env file
set "envFile=.env"

REM Initialize SERVER
set "SERVER="

REM Loop through each line in the .env file
for /f "usebackq tokens=1,* delims==" %%a in ("%envFile%") do (
  REM Trim leading and trailing spaces from the variable name and value
  set "varName=%%a"
  set "varValue=%%b"
  for %%A in (!varName!) do set "varName=%%~A"
  for %%B in (!varValue!) do set "varValue=%%~B"

  REM Check if the current line contains "SERVER"
  if /i "!varName!"=="SERVER" (
    set "SERVER=!varValue!"
  )
)

REM Check if SERVER was found
if defined SERVER (
  echo SERVER: !SERVER!

  call .\venv\Scripts\python.exe main.py -bt q -s !SERVER!
) else (
  echo SERVER not found in %envFile%
)

endlocal
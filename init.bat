@echo off

set BASE_DIR=%~dp0
set VENV_DIR=%BASE_DIR%venv
set REQUIREMENTS_FILE=%BASE_DIR%requirements.txt
set DB_FILE=%BASE_DIR%db.sqlite3

for /d %%i in ("%BASE_DIR%*") do (
    if "%%~nxi"=="migrations" (
        set MIGRATIONS_DIR=%%i
    )
)

set JSON_DATA_FILE=%BASE_DIR%populate.json
set DELETE_DB=false
set DELETE_ENV=false

:parse_args
if "%~1"=="" goto :reset_database
if "%~1"=="-db" (
    set DELETE_DB=true
    shift
    goto :parse_args
)
if "%~1"=="--delete-db" (
    set DELETE_DB=true
    shift
    goto :parse_args
)
if "%~1"=="-env" (
    set DELETE_ENV=true
    shift
    goto :parse_args
)
if "%~1"=="--delete-env" (
    set DELETE_ENV=true
    shift
    goto :parse_args
)
echo Unknown option: %1
exit /b 1

:reset_database
if "%DELETE_ENV%"=="true" (
    if exist "%VENV_DIR%" (
        echo Deleting existing virtual environment...
        rmdir /s /q "%VENV_DIR%"
    )
    echo Creating a new virtual environment...
    python -m venv "%VENV_DIR%"
    call "%VENV_DIR%\Scripts\activate"
    echo Installing dependencies from requirements.txt...
    pip install -r "%REQUIREMENTS_FILE%"
    echo ----------------------------------------
)

git config commit.template .gitmessage.txt
echo Git commit template configured.
echo ----------------------------------------

if "%DELETE_DB%"=="true" if exist "%DB_FILE%" (
    del "%DB_FILE%"
    echo Existing db.sqlite3 file deleted.
    echo ----------------------------------------

    for /d %%i in ("%MIGRATIONS_DIR%") do (
        if exist "%%i" (
            for /r "%%i" %%f in (*) do (
                if "%%~nxf" neq "__init__.py" (
                    del "%%f"
                )
            )
            echo Migration files in %%i deleted, excluding __init__.py.
        )
    )
    echo ----------------------------------------

    if "%DELETE_DB%"=="true" (
        type nul > "%DB_FILE%"
        echo db.sqlite3 file created.
        echo ----------------------------------------
    )
)

python manage.py makemigrations
echo Migrations updated.
echo ----------------------------------------

python manage.py migrate
echo Migrations applied.
echo ----------------------------------------

for %%i in ("%JSON_DATA_FILE%") do (
    if exist "%%i" (
        python manage.py loaddata "%%i"
        echo Data loaded from JSON file: %%i
    )
)

echo ----------------------------------------
echo Process completed successfully!
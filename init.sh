#!/bin/bash

BASE_DIR=$(dirname "$0")
VENV_DIR="$BASE_DIR/.venv"
REQUIREMENTS_FILE="$BASE_DIR/requirements.txt"
DB_FILE="$BASE_DIR/db.sqlite3"
MIGRATIONS_DIR=$(find "$BASE_DIR" -type d -name migrations -not -path "*/lib/*")

JSON_DATA_FILE="$BASE_DIR/populate.json"
DELETE_DB=false
DELETE_ENV=false

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        -db|--delete-db)
            DELETE_DB=true
            shift
            ;;
        -env|--delete-env)
            DELETE_ENV=true
            shift
            ;;
        *)
            # Unknown option
            echo "Unknown option: $key"
            exit 1
            ;;
    esac
done

reset_database() {
    # Delete existing virtual environment
    if [ "$DELETE_ENV" == true ]; then
        if [ -d "$VENV_DIR" ]; then
            echo "Deleting existing virtual environment..."
            rm -rf "$VENV_DIR"
        fi

        # Create a new virtual environment
        echo "Creating a new virtual environment..."
        python3 -m venv "$VENV_DIR"

        # Activate the virtual environment
        echo "Activating the virtual environment..."
        source "$VENV_DIR/bin/activate"

        # Install dependencies from requirements.txt
        echo "Installing dependencies from requirements.txt..."
        pip install -r "$REQUIREMENTS_FILE"
        echo "----------------------------------------"
    fi

    # Configure template for commits
    git config commit.template .gitmessage.txt
    echo "Git commit template configured."
    echo "----------------------------------------"

    # Delete the existing db.sqlite3 file if DELETE_DB is true
    if [ "$DELETE_DB" == true ] && [ -e "$DB_FILE" ]; then
        rm "$DB_FILE"
        echo "Existing db.sqlite3 file deleted."
        echo "----------------------------------------"

        # Delete migration files excluding __init__.py
        for dir in $MIGRATIONS_DIR; do
            if [ -e "$dir" ]; then
                find "$dir" -type f ! -name "__init__.py" ! -path "*/venv/*" -exec rm {} \;
                echo "Migration files in $dir deleted, excluding __init__.py."
            fi
        done
        echo "----------------------------------------"

        # Create the db.sqlite3 file
        if [ "$DELETE_DB" == true ]; then
            touch "$DB_FILE"
            echo "db.sqlite3 file created."
            echo "----------------------------------------"
        fi
    fi

    # Update migrations
    python manage.py makemigrations
    echo "Migrations updated."
    echo "----------------------------------------"

    # Apply migrations
    python manage.py migrate
    echo "Migrations applied."
    echo "----------------------------------------"

    # Load data from JSON files
    for file in $JSON_DATA_FILE; do
        if [ -e "$file" ]; then
            python manage.py loaddata "$file"
            echo "Data loaded from JSON file: $file"
        fi
    done

    echo "----------------------------------------"
    echo "Process completed successfully!"
}

reset_database
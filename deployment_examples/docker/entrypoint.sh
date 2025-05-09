#!/bin/bash
set -e

# Function to handle application shutdown
function handle_shutdown() {
    echo "Received shutdown signal. Gracefully shutting down..."
    kill -TERM "$child_pid"
    wait "$child_pid"
    echo "Application shut down successfully"
    exit 0
}

# Set up signal trapping
trap handle_shutdown SIGTERM SIGINT

# Wait for database to be ready
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "Waiting for PostgreSQL to be ready..."
    
    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -e 's/^.*@\(.*\):[0-9]*\/.*$/\1/')
    DB_PORT=$(echo $DATABASE_URL | sed -e 's/^.*:\([0-9]*\)\/.*$/\1/')
    
    # Default port if not specified
    if [ -z "$DB_PORT" ]; then
        DB_PORT=5432
    fi
    
    # Wait for database connection
    until pg_isready -h $DB_HOST -p $DB_PORT -U postgres; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    
    echo "PostgreSQL is up - continuing"
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "Created logs directory"
fi

# Apply database migrations if needed
# In a real application, you might use Flask-Migrate or Alembic
echo "Initializing database..."
python -c "from app import db, app; app.app_context().push(); db.create_all()"

# Set proper file permissions
chown -R appuser:appuser /app
chmod -R 755 /app

# Start application with Gunicorn
echo "Starting Flask application with Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 60 --access-logfile - --error-logfile - app:app &

# Store child PID
child_pid=$!

# Wait for child process to terminate
wait "$child_pid"

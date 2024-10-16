#!/bin/bash

echo "Running the app"

# Start the Flask app in the background
python app.py &

# Start the main script in the foreground
python main.py

# Wait for all background jobs to finish
wait

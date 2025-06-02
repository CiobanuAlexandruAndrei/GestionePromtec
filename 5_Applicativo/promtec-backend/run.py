"""
Main application entry point for the Promtec backend service.
This script initializes and runs the Flask application.
"""
from app import create_app

# Create the Flask application instance
app = create_app()

# Run the application if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)  # Start the development server with debug mode enabled
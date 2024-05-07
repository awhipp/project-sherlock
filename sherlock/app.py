"""Entry point for the Sherlock application.

It will be a flask application that will be used to serve the web interface, 
and allow users to ask questions of the generative AI chat bot.
"""

from flask import Flask

app = Flask(__name__)

# Define a route for the default URL
@app.route('/')
def home():
    """Home Route."""
    return 'Hello, World!'

# Start Flask App
if __name__ == '__main__':
    # Run the app on localhost port 5000
    app.run(port=5000, debug=True)
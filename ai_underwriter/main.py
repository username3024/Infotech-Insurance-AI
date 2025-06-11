import logging
from flask import Flask
from app.api.application_api import application_bp # Import the blueprint

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(application_bp)

@app.route('/')
def hello_world():
  return 'Hello, World!'

if __name__ == '__main__':
  app.run(debug=True)

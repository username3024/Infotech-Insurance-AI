from flask import Flask
from app.api.application_api import application_bp # Import the blueprint

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(application_bp)

@app.route('/')
def hello_world():
  return 'Hello, World!'

if __name__ == '__main__':
  app.run(debug=True)

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI
from models import db
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db.init_app(app)
migrate = Migrate(app, db)

# Example Route
@app.route("/")
def home():
    return jsonify({"message": "Flask App Running"})

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI
from models import db
from flask_migrate import Migrate
from flasgger import Swagger
import os 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db.init_app(app)
migrate = Migrate(app, db)

swagger_file = os.path.join(os.path.dirname(__file__), "docs", "book_docs.yml")
swagger = Swagger(app, template_file=swagger_file)

# Register blueprints (routes)
from routes.book_routes import book_blueprint
app.register_blueprint(book_blueprint, url_prefix="/api/v1/books")

# Example Route
@app.route("/")
def home():
    return jsonify({"message": "Flask App Running"})

if __name__ == "__main__":
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint} | Route: {rule.rule} | Methods: {', '.join(rule.methods)}")
    app.run(debug=True)

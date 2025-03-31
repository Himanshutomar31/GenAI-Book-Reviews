from flask import Blueprint, request, jsonify
from models import db, Book, Review
import os 
from werkzeug.utils import secure_filename
from openai_service import extract_text_from_pdf, generate_summary
from utils import upload_to_s3


book_blueprint = Blueprint("books", __name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@book_blueprint.route("/", methods=["POST"])
def create_book():
    title = request.form.get("title")
    author = request.form.get("author")
    genre = request.form.get("genre")
    year_published = request.form.get("year_published")

    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    # Save the file temporarily
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(file_path)

    extracted_text = extract_text_from_pdf(file_path)
    summary = generate_summary(extracted_text)
    
    if not extracted_text.strip():
        return jsonify({"error": "Could not extract text from the PDF"}), 400

    pdf_s3_url = upload_to_s3(file, title)  

    os.remove(file_path)

    new_book = Book(
        title=title,
        author=author,
        genre=genre,
        year_published=year_published,
        summary=summary,
        pdf_file_path=pdf_s3_url
    )
    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        "message": "Book added successfully!",
        "id": new_book.id,
        "pdf_s3_url": pdf_s3_url,
        "summary": summary
    }), 201


# Retrieve all books
@book_blueprint.route("/", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([{"id": book.id, "title": book.title, "author": book.author, "summary": book.summary} for book in books])


# Retrieve a specific book by ID
@book_blueprint.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404
    return jsonify({"id": book.id, "title": book.title, "author": book.author, "genre": book.genre})


# Update a book's information
@book_blueprint.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    data = request.json
    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.genre = data.get("genre", book.genre)
    book.year_published = data.get("year_published", book.year_published)
    book.summary = data.get("summary", book.summary)

    db.session.commit()
    return jsonify({"message": "Book updated successfully!"})


# Delete a book
@book_blueprint.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully!"})


# Add a review for a book
@book_blueprint.route("/<int:book_id>/reviews", methods=["POST"])
def add_review(book_id):
    data = request.json
    review = Review(
        book_id=data["book_id"],
        user_id=data["user_id"],
        review_text=data["review_text"],
        rating=data["rating"]
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review added successfully!"}), 201


# Retrieve all reviews for a book
@book_blueprint.route("/<int:book_id>/reviews", methods=["GET"])
def get_reviews(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    reviews = Review.query.filter_by(book_id=book_id).all()
    return jsonify([{"id": r.id, "user_id": r.user_id, "review_text": r.review_text, "rating": r.rating} for r in reviews])


# Get a summary & average rating for a book
@book_blueprint.route("/<int:book_id>/summary", methods=["GET"])
def get_book_summary(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    return jsonify({
        "title": book.title,
        "summary": book.summary,
        "average_rating": book.average_rating
    })


@book_blueprint.route("/generate-summary", methods=["POST"])
def generate_book_summary():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    # Save the file temporarily
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(file_path)

    extracted_text = extract_text_from_pdf(file_path)
    
    if not extracted_text.strip():
        return jsonify({"error": "Could not extract text from the PDF"}), 400

    summary = generate_summary(extracted_text)
    os.remove(file_path)

    return jsonify({"summary": summary})



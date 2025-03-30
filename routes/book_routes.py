from flask import Blueprint, request, jsonify
from models import db, Book, Review

book_blueprint = Blueprint("books", __name__)

# Add a new book
@book_blueprint.route("/", methods=["POST"])
def create_book():
    data = request.json
    new_book = Book(
        title=data["title"],
        author=data["author"],
        genre=data.get("genre"),
        year_published=data.get("year_published"),
        summary=data.get("summary")
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully!", "id": new_book.id}), 201

# Retrieve all books
@book_blueprint.route("/", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([{"id": book.id, "title": book.title, "author": book.author} for book in books])

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
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    data = request.json
    review = Review(
        book_id=book_id,
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





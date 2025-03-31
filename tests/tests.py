import sys
import pytest
from io import BytesIO
from app import app, db
from models import Book
import os 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_book(client, mocker):
    """Test book creation via POST request."""
    mocker.patch("openai_service.extract_text_from_pdf", return_value="Sample text")
    mocker.patch("openai_service.generate_summary", return_value="Sample summary")
    mocker.patch("utils.upload_to_s3", return_value="https://s3-bucket/test.pdf")

    data = {
        "title": "Test Book",
        "author": "Test Author",
        "genre": "Fiction",
        "year_published": "2022"
    }
    file_data = {
        "file": (BytesIO(b"%PDF-1.4 Sample PDF content"), "test.pdf")
    }

    response = client.post("/api/v1/books/", data={**data, **file_data}, content_type='multipart/form-data') 
    assert response.status_code == 201
    assert "book_id" in response.json

def test_get_books(client):
    """Test retrieving the list of books."""
    response = client.get("/api/v1/books") 
    assert response.status_code == 200

def test_add_review(client):
    """Test adding a review to a book."""
    with app.app_context():
        book = Book(title="Test Book", author="Test Author", genre="Fiction", year_published=2022, summary="Sample summary", pdf_file_path="")
        db.session.add(book)
        db.session.commit()

        # Explicitly query the book again before using its ID
        book = db.session.get(Book, book.id)

    review_data = {
        "book_id": book.id,
        "user_id": 1,
        "review_text": "Great book!",
        "rating": 5
    }

    response = client.post("/api/v1/reviews/", json=review_data)
    assert response.status_code == 201

def test_delete_book(client):
    """Test deleting a book."""
    with app.app_context():
        book = Book(title="To Delete", author="Author", genre="Fiction", year_published=2022, summary="Sample summary", pdf_file_path="")
        db.session.add(book)
        db.session.commit()

        # Explicitly query the book again before using its ID
        book = db.session.get(Book, book.id)

    response = client.delete(f"/api/v1/books/{book.id}")  
    assert response.status_code == 200

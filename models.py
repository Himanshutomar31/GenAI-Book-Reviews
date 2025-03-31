from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import func

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    year_published = db.Column(db.Integer)
    summary = db.Column(db.Text)
    pdf_file_path = db.Column(db.String(255))

    reviews = relationship("Review", backref="book", cascade="all, delete-orphan")

    @property
    def average_rating(self):
        """Returns the average rating of the book based on reviews."""
        if self.reviews:
            return round(sum(review.rating for review in self.reviews) / len(self.reviews), 2)
        return None

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

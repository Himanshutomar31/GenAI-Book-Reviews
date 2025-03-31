import boto3
from werkzeug.utils import secure_filename
from config import AWS_ACCESS_KEY_ID, AWS_S3_BUCKET, AWS_SECRET_ACCESS_KEY, AWS_REGION

# Initialize S3 client using environment variables
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_to_s3(file, book_title):
    """Uploads a PDF file to S3 and returns the file URL."""
    filename = secure_filename(file.filename)
    s3_key = f"books/{book_title}/{filename}"  

    # Upload the file
    s3_client.upload_fileobj(file, AWS_S3_BUCKET, s3_key)

    # Generate the public S3 URL
    s3_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    return s3_url

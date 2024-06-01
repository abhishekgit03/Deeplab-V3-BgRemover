# Background Remover

This is a Flask application that allows users to upload files and returns the foreground of the uploaded image as a base64 encoded string.

## Setup

1. **Clone the repository:**

    ```bash
   https://github.com/abhishekgit03/Deeplab-V3-BgRemover
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application:**

    ```bash
    python app.py
    ```

    The application will start running on http://localhost:5000 by default.

## Usage

1. **Uploading a file:**

    Send a POST request to the `/remove` endpoint with the file attached as form data. The server will process the uploaded image, remove its background, and return the foreground image as a base64 encoded string.

    Example using cURL:
    ```bash
    curl -X POST -F "file=@/path/to/your/file.jpg" http://localhost:5000/upload
    ```

2. **Response:**

    Upon successful upload, the server will respond with a JSON object containing the base64 encoded foreground image.

    Example response:
    ```json
    {
        "foregroundimage": "/9j/4AAQSkZJRgABAQEAYABgAAD/4QBYRXhpZgAATU0AKgAAAAgAA..."
    }
    ```


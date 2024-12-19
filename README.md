# Waste Classification Management System using YOLOv8

## Overview

This project is a web-based waste classification management system that helps users classify waste using the YOLOv8 deep learning model. It provides additional features such as the latest waste management news, a chatbot for user assistance, and a contact form to send feedback via email.

## Features

- **Waste Classification**: Users can upload an image, and the YOLOv8 model will classify the type of waste.
- **News Feed**: Displays the latest waste management news and technologies.
- **AI Chatbot**: Assists users in learning more about waste management and the platform.
- **Contact Form**: Users can send messages and feedback. Admins will receive these messages via email.
- **Email Notifications**: Automated email notifications for the contact form submissions.

## Tech Stack

- **Backend**: Flask, Python
- **Frontend**: HTML5, CSS3, Bootstrap 4, JavaScript
- **Machine Learning**: YOLOv8 Model for image classification
- **APIs**: News API for fetching waste management news
- **Email**: SMTP for sending email notifications

## Installation

To run this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/PiyushBhatnagar09/waste-classification-yolov8.git
    ```

2. Navigate into the project directory:
    ```bash
    cd waste-classification-yolov8
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure environment variables for email functionality. In your `.env` file, add:
    ```bash
    EMAIL_USERNAME=<your-email>
    EMAIL_PASSWORD=<your-email-password>
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    NEWS_API_KEY=<your-news-api-key>
    ```

5. Run the Flask app:
    ```bash
    python app.py
    ```

6. Open a web browser and visit:
    ```
    http://127.0.0.1:5000
    ```

## Usage

- **Classify Waste**: Navigate to the "Classify Waste" page, upload an image, and the system will classify the waste.
- **News Feed**: Go to the "News Feed" page to view the latest updates and articles on waste management.
- **Chat with AI**: Engage with the chatbot to learn more about waste management and the platform's features.
- **Contact Us**: Fill out the contact form to send a message or feedback. A pop-up will confirm that the message has been successfully sent.

## Email Functionality

When a user submits a message via the contact form, the admin will receive the message through an automated email sent using SMTP. Make sure to properly configure your email credentials in the `.env` file.

## Contributing

Feel free to contribute to the project by creating issues or submitting pull requests. Any contributions are appreciated!

## License

This project is licensed under the MIT License.

# WasteWise

## Overview

This project is a web-based waste classification and awareness system that helps users classify waste using the YOLOv8 deep learning model. It provides additional features such as the latest waste management news and subscription option, a chatbot for user assistance, and a contact form to send feedback via email.

![home_page](https://github.com/user-attachments/assets/3dbc9bd1-7b6d-4f32-bed8-45b969824c1c)
![home_page2](https://github.com/user-attachments/assets/dede4213-9627-41c3-961a-623b357d5381)

## Features

- **Waste Classification and Disposal Guide**: Users can upload an image, and the YOLOv8 model will classify the type of waste.

![classify1](https://github.com/user-attachments/assets/0b01b3e7-114b-4b1a-b607-64869b11566f)
![classify2](https://github.com/user-attachments/assets/837bf6fc-d7a1-4b4c-9e3c-6fe931a9d11d)
![disposal_guide](https://github.com/user-attachments/assets/26bab523-d36e-4b76-a162-4310dbe287a2)

- **News Feed and Subscription Option**: Displays the latest waste management news and technologies. Allows users to subscribe for daily waste-related news.

![news_feed](https://github.com/user-attachments/assets/1cefb373-b265-4a07-be2c-42096efe7382)

- **AI Chatbot**: Assists users in learning more about waste management and the platform.

![chat_with_ai](https://github.com/user-attachments/assets/2e6a5f18-b23c-4623-959c-b430457584d1)

- **Email Notifications**: Automated email for daily news with unsubscribe button.

![daily_news](https://github.com/user-attachments/assets/a3f42a39-0d02-4238-82eb-990b9cd494c9)
![unsubscribe](https://github.com/user-attachments/assets/a501409f-3b42-4da9-9a14-438253227bee)

- **Contact Form**: Users can send messages and feedback. Admins will receive these messages via email.

![contact_form](https://github.com/user-attachments/assets/84b98186-92ee-4f1b-9a7d-620bf6db8474)

## Tech Stack

- **Backend**: Flask, Python, MongoDB
- **Frontend**: HTML5, CSS3, Bootstrap 4, JavaScript
- **Machine Learning**: YOLOv8 Model for image classification, Gemini Model for AI Chat Bot
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

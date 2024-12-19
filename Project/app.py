from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image
import settings
import helper
import requests  # Import the requests library for API calls
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime
import uuid, io
import tensorflow as tf
import numpy as np
from pymongo import MongoClient
import config

# import util

app = Flask(__name__)
model1= None
model2= None

# MongoDB Setup
client = MongoClient(config.MONGO_URI)
db = client[config.MONGO_DB_NAME]
users_collection = db[config.MONGO_COLLECTION_NAME]

output_class = ["Batteries", "Clothes", "E-waste", "Glass", "Light Blubs", "Metal", "Organic", "Paper", "Plastic"]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/classify')
def classify():
    return render_template('classify.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route to handle image uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    global model1, model2

    # Model config
    confidence = float(request.form.get('confidence', 40))
    confidence = float(confidence)/100

    # Selecting model path
    model_path1 = Path(settings.DETECTION_MODEL1)
    model_path2 = Path(settings.DETECTION_MODEL2)

    # Load model if not already loaded
    if model1 is None:
        try:
            model1 = helper.load_model1(model_path1)
        except Exception as ex:
            return render_template('classify.html', error=f"Error loading model1: {ex}")
    
    if model2 is None:
        try:
            model2 = helper.load_model2(model_path2)
        except Exception as ex:
            return render_template('classify.html', error=f"Error loading model2: {ex}")
        
    # Handling image file upload
    if 'file' not in request.files:
        return redirect(request.url)

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return redirect(request.url)

    # Process the image
    if uploaded_file:
        # Save the original uploaded image
        original_image_path = 'static/results/original_image.jpg'
        uploaded_file.save(original_image_path)

        #model1
        img = Image.open(uploaded_file)
        res = model1.predict(img, conf=confidence)

        # detected_objects = []
        # for detection in res[0].boxes:  # Assuming `res[0].boxes` holds the detection results
        #     object_name = detection.label  # Name of the detected object
        #     confidence_score = detection.score  # Confidence score of detection
        #     detected_objects.append(f"{object_name} ({confidence_score:.2f})")

        # Assuming `results` is your YOLOv8 results object
        detected_classes = set()  # Use a set to avoid duplicates

        # Loop over detected boxes and extract the class name for each detected object
        for box in res[0].boxes:
            class_id = int(box.cls[0])  # Extract the class ID
            detected_classes.add(res[0].names[class_id])  # Map class ID to class name

        # Convert to a comma-separated string
        detected_objects_text = ', '.join(detected_classes)

        res_plotted = res[0].plot()[:, :, ::-1]
        result_image_path = 'static/results/detected_image.jpg'
        Image.fromarray(res_plotted).save(result_image_path)

        #model2
        test_image = tf.keras.preprocessing.image.load_img(original_image_path, target_size=(224, 224))
        test_image = tf.keras.preprocessing.image.img_to_array(test_image) / 255
        test_image = np.expand_dims(test_image, axis = 0)
        predicted_array = model2.predict(test_image)
        predicted_value = output_class[np.argmax(predicted_array)]

        return render_template('classify.html', result_image=result_image_path, uploaded_image=original_image_path, classification_result=predicted_value, detected_objects_text=detected_objects_text)

    return redirect(url_for('classify'))

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_prompt = request.json.get('prompt', '')
    response_text = ""

    print("User prompt:", user_prompt)

    try:
        response = requests.post(config.GEMINI_URL + '/ask', json={"prompt": user_prompt})
        response_data = response.json()
        response_text = response_data.get("answer", "No response received.")
        print("Answer:", response_text)
    except requests.exceptions.RequestException as e:
        response_text = f"Error connecting to Gemini API: {str(e)}"

    return jsonify({"answer": response_text})

# Route to handle sending the contact message
@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Prepare email details
    subject = f"Contact Form Submission from {name}"
    body = f"Name: {name}\n\nEmail: {email}\n\nMessage:\n{message}"

    try:
        # Construct the email with MIME
        msg = MIMEMultipart()
        msg['From'] = config.EMAIL_USERNAME
        msg['To'] = config.EMAIL_USERNAME
        msg['Subject'] = subject

        # Attach the body with line breaks
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_USERNAME, config.EMAIL_USERNAME, msg.as_string())

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'status': 'error'}), 500

# News feed route
@app.route('/news')
def news_feed():
    today = datetime.today().strftime('%Y-%m-%d')
    last_week = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    url = f'https://newsapi.org/v2/everything?q=waste%20recycling&from={last_week}&to={today}&sortBy=publishedAt&apiKey={config.NEWS_API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
    except requests.exceptions.RequestException as e:
        articles = []
        print(f"Error fetching news: {e}")

    return render_template('news.html', articles=articles)

# Subscription route
@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    email = data['email']
    password = data['password']

    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({'message': 'User already subscribed!'}), 400
    
    # Save user to MongoDB
    user_data = {
        "email": email,
        "password": password,  # Ideally, hash passwords before storing them
        "subscribed": True,
        "subscribed_at": datetime.utcnow()
    }
    print(user_data)
    users_collection.insert_one(user_data)

    # Send welcome email
    subject = "Welcome to Our Newsletter!"
    body = (
        "Thank you for subscribing to our newsletter!\n\n"
        "You will receive weekly updates with the latest news and insights.\n"
        "Stay tuned for our upcoming issues filled with valuable information.\n\n"
        "Best regards,\n"
        "The Team"
    )
    send_email(email, subject, body)
    print('email sent')
    send_daily_news()
    print('news sent')
    return jsonify({'message': 'Subscribed successfully!'}), 200


# Unsubscribe route
@app.route('/unsubscribe/<email>', methods=['GET'])
def unsubscribe(email):
    print(email)
    result = users_collection.update_one({"email": email}, {"$set": {"subscribed": False}})
    if result.modified_count == 0:
        return jsonify({"message": "User not found or already unsubscribed."}), 404
    return jsonify({"message": "You have been unsubscribed successfully!"}), 200

# Function to send daily news email
def send_daily_news():
    today = datetime.today().strftime('%Y-%m-%d')
    seven_days_ago = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    url = f'https://newsapi.org/v2/everything?q=plastic%20recycling%20metal&from={seven_days_ago}&to={today}&sortBy=publishedAt&apiKey={config.NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])

    # Filter articles that have an image
    articles_with_images = [article for article in articles if article.get('urlToImage')]
    if articles_with_images:
        subject = "Weekly Waste Management News"

        # Create the HTML body with articles
        html_body = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }
                .email-container { max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; }
                .header { background: #4caf50; color: #ffffff; text-align: center; padding: 20px; font-size: 24px; }
                .content { padding: 20px; }
                .article { margin-bottom: 20px; }
                .article img { max-width: 100%; border-radius: 8px; }
                .article-title { font-size: 18px; margin: 10px 0; }
                .article-description { font-size: 14px; color: #555555; }
                .footer { text-align: center; padding: 10px; background: #f4f4f9; font-size: 12px; color: #999999; }
                .unsubscribe { color: #0073e6; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">Weekly Waste Management News</div>
                <div class="content">
        """

        # Add articles to the HTML
        for article in articles_with_images[:5]:  # Limit to 5 articles per email
            image = article.get('urlToImage', 'https://via.placeholder.com/600x400')
            html_body += f"""
                <div class="article">
                    <img src="{image}" alt="Article Image">
                    <div class="article-title"><strong>{article['title']}</strong> ({article['publishedAt'][:10]})</div>
                    <div class="article-description">{article['description']}</div>
                    <a href="{article['url']}" target="_blank">Read more</a>
                </div>
            """

    # Query the collection for subscribed users
    subscribed_users = users_collection.find({"subscribed": True})

    # Send emails to subscribed users
    for user_data in subscribed_users:
        email = user_data.get('email')  # Retrieve the email from the document
        if email:  # Ensure the email field exists
            html_body1= html_body
            website_url = config.WEBSITE_URL
            # Add footer and unsubscribe link
            html_body1 += f"""
                    </div>
                    <div class="footer">
                        You are receiving this email because you subscribed to our newsletter.<br>
                        <a href="{website_url}/unsubscribe/{email}" class="unsubscribe">Unsubscribe</a>
                    </div>
                </div>
            </body>
            </html>
            """
            
            send_email(email, subject, html_body1)

# Function to send an HTML email
def send_email(recipient, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = config.EMAIL_USERNAME
    msg['To'] = recipient

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
        server.sendmail(config.EMAIL_USERNAME, recipient, msg.as_string())

# Uncomment the scheduler if needed
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=send_daily_news, trigger="interval", days=1)
# scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
    # send_daily_news()

from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image
import settings
import helper
import requests  # Import the requests library for API calls
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta
import uuid, io
import tensorflow as tf
import numpy as np

# import util

app = Flask(__name__)
model1= None
model2= None

# helper.load_artifacts()

# Simulated user database (in-memory)
subscribed_users = {}

NEWS_API_KEY = '1a38e49478d446f1816690b31dc12004'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USERNAME = 'pbpiyush34@gmail.com'
EMAIL_PASSWORD = 'vgkhbvyqhnucryav'

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
    model_type = request.form.get('model_type', 'Detection')
    confidence = float(request.form.get('confidence', 40))
    confidence = float(confidence)/100

    # Selecting model path
    if model_type == 'Detection':
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
            print('check3: ', box)
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
        response = requests.post('http://127.0.0.1:5001/ask', json={"prompt": user_prompt})
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
    body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"

    try:
        send_email(EMAIL_USERNAME, subject, body)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'status': 'error'}), 500

# News feed route
@app.route('/news')
def news_feed():
    today = datetime.today().strftime('%Y-%m-%d')
    last_week = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    url = f'https://newsapi.org/v2/everything?q=waste%20recycling&from={last_week}&to={today}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error if the request fails
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
    
    # Save user in the in-memory database
    subscribed_users[email] = {
        'password': password,
        'subscribed': True
    }
    
    subject = "Welcome to Our Newsletter!"
    body = (
        "Thank you for subscribing to our newsletter!\n\n"
        "You will receive weekly updates with the latest news and insights.\n"
        "Stay tuned for our upcoming issues filled with valuable information.\n\n"
        "Best regards,\n"
        "The Team"
    )

    send_email(email, subject, body)
    
    return jsonify({'message': 'Subscribed successfully!'}), 200


# Unsubscribe route
@app.route('/unsubscribe/<email>', methods=['GET'])
def unsubscribe(email):
    if email in subscribed_users:
        subscribed_users[email]['subscribed'] = False
        return 'You have been unsubscribed successfully!'
    else:
        return 'User not found.', 404

# Function to send daily news email
def send_daily_news():
    today = datetime.today().strftime('%Y-%m-%d')
    seven_days_ago = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    url = f'https://newsapi.org/v2/everything?q=plastic%20recycling%20metal&from={seven_days_ago}&to={today}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])

    if articles:
        subject = "Weekly Waste Management News"
        
        # Create the body with articles from the last 7 days
        body = "Here are the top waste management news articles from the last 7 days:\n\n"
        for article in articles[:5]:  # Limit to 5 articles per email
            body += f"- {article['title']} ({article['publishedAt'][:10]})\n{article['description']}\nRead more: {article['url']}\n\n"
        
        body += "Click here to unsubscribe: http://localhost:5000/unsubscribe/{{email}}"
        
        # Send emails to subscribed users
        for email, user_data in subscribed_users.items():
            if user_data['subscribed']:
                send_email(email, subject, body)


# Function to send an email
def send_email(recipient, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USERNAME
    msg['To'] = recipient
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, recipient, msg.as_string())

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=send_daily_news, trigger="interval", days=1)
# scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)

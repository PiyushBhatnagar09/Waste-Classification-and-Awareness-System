from pathlib import Path
from flask import Flask, render_template, request, jsonify
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import timedelta, datetime
from pymongo import MongoClient
import config
from flask_cors import CORS  # Import the CORS package

app = Flask(__name__)
CORS(app)

# MongoDB Setup
client = MongoClient(config.MONGO_URI)
db = client[config.MONGO_DB_NAME]
users_collection = db[config.MONGO_COLLECTION_NAME]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/classify')
def classify():
    return render_template('classify.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

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
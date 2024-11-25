# gemini_api.py
from flask import Flask, request, jsonify
import google.generativeai as genai
import config

app = Flask(__name__)

# Configure the API key
genai.configure(api_key= config.GEMINI_API_KEY)

# Define the model and configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Only answer questions related to waste classification, waste recycling, metal, plastic, biodegradable, clothes, paper, cardboard, organic, glass, light bulb, batteries waste. \n",
)

@app.route('/ask', methods=['POST'])
def ask():
    user_prompt = request.json.get('prompt', '')
    response_text = ""

    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_prompt)
        response_text = response.text.strip()  # Get the text from the response
        formatted_response = format_response(response_text)
    except Exception as e:
        formatted_response = f"Error: {str(e)}"

    return jsonify({"answer": formatted_response})

def format_response(response_text):
    """Format the response text into structured HTML for better readability."""
    lines = response_text.splitlines()
    formatted_lines = []
    in_bullet_list = False

    for line in lines:
        stripped_line = line.strip()
        
        # Remove all instances of '**' before processing
        cleaned_line = stripped_line.replace("**", "").strip()
        
        if cleaned_line.startswith("## "):  # Heading level 1
            formatted_lines.append(f"<h2>{cleaned_line[3:]}</h2>")
        elif cleaned_line.endswith(":"):  # Heading level 2 (if it ends with a colon)
            formatted_lines.append(f"<h3>{cleaned_line[:-1].strip()}</h3>")
        elif cleaned_line.startswith("* ") and not in_bullet_list:  # Start of bullet points
            formatted_lines.append("<ul>")
            in_bullet_list = True
            formatted_lines.append(f"<li>{cleaned_line[2:]}</li>")
        elif cleaned_line.startswith("* ") and in_bullet_list:  # Bullet points
            formatted_lines.append(f"<li>{cleaned_line[2:]}</li>")
        elif in_bullet_list and cleaned_line:  # End of bullet points
            formatted_lines.append("</ul>")
            in_bullet_list = False
            formatted_lines.append(f"<p>{cleaned_line}</p>")
        elif cleaned_line:  # Non-empty lines
            formatted_lines.append(f"<p>{cleaned_line}</p>")

    # After the loop, if we were still in a bullet list, close it
    if in_bullet_list:
        formatted_lines.append("</ul>")



    return "\n".join(formatted_lines)

if __name__ == '__main__':
    app.run(port=5001)  # Run on a different port

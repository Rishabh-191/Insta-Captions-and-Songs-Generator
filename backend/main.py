import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile

app = Flask(__name__)
CORS(app)

# Configure the Generative AI API key
genai.configure(api_key=os.environ.get("API_KEY"))

def upload_to_gemini(file_storage, mime_type="image/jpeg"):
    """Uploads the given image file (saved to disk) to Gemini."""
    try:
        # Create a temporary file to save the image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            file_path = temp_file.name
            file_storage.save(file_path)
            print(f"Saved image temporarily at {file_path}")

        # Upload the image file using its file path
        gemini_file = genai.upload_file(file_path, mime_type=mime_type)
        print(f"Uploaded file '{file_storage.filename}' as: {gemini_file.uri}")

        # Clean up the temporary file after uploading
        os.remove(file_path)
        return gemini_file

    except Exception as e:
        print(f"Error uploading file to Gemini: {e}")
        return None

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Instagram Assistant API!"})

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Check if api key is provided
        if 'API_KEY' not in os.environ:
            return jsonify({"error": "API_KEY environment variable is missing"}), 500

        # Check if the image file is part of the request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        img = request.files['image']

        # Upload the image to Gemini
        gemini_file = upload_to_gemini(img)

        if not gemini_file:
            return jsonify({"error": "Failed to upload image to Gemini"}), 500

        # Define the model configuration
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        try:
            # Create the generative model
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                system_instruction="""
                You are an Instagram assistant specialized in creating engaging captions with relevant hashtags and recommending songs to enhance the mood of each photo. Every time I upload a photo, follow these steps:
                Generate Captions: Analyze the photo's content, mood, and setting. Based on this analysis, create 3-5 unique, creative captions for Instagram that reflect the visual elements or emotions in the image. Use a mix of descriptive language, emojis, and engaging phrases.
                Add Hashtags: With each caption, include 5-10 relevant hashtags to maximize visibility. Focus on popular and niche hashtags related to the photo's theme, location, or emotions.
                Suggest Songs: Suggest 5-10 songs that match the mood, theme, or setting of the photo. Include both classic and trending options if relevant, and choose songs that would resonate well as background music for social media posts. Aim for a variety that appeals to different tastes.
                Respond in the following JSON format:
                {
                  "captions": [
                    "Caption 1 with hashtags #example1 #example2",
                    "Caption 2 with hashtags #example3 #example4"
                  ],
                  "songs": [
                    "Song Title 1 - Artist Name",
                    "Song Title 2 - Artist Name"
                  ]
                }
                Only output the JSON object with captions and songs in this structured format.
                """
            )

            # Start a chat session with the uploaded image
            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [gemini_file],
                    }
                ]
            )

            # Send a message to generate captions and song suggestions
            response = chat_session.send_message("Analyze the uploaded image and provide captions and song suggestions.")

            # Parse the JSON response
            try:
                final_response = json.loads(response.text)
                print(f"Final response from model: {final_response}")

                # Return the response as JSON
                return jsonify(final_response), 200

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                return jsonify({"error": "Failed to parse model response"}), 500

        except Exception as e:
            print(f"Error during model interaction: {e}")
            return jsonify({"error": "An error occurred while processing the request"}), 500

    return jsonify({"error": "Invalid request method"}), 405


if __name__ == "__main__":
    app.run(debug=True)

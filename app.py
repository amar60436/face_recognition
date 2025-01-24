from flask import Flask, render_template, request, jsonify,send_from_directory
import os
from deepface import DeepFace
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd
import json
from flask_cors import CORS

app = Flask(__name__, static_folder='dataset_images')
CORS(app)

# Path to database folder for actor recognition
db_path = "dataset_images"

# Path to the CSV file with actor details
csv_path = "actors_enhanced_data/actors_info_updated.csv"

# Temporary folder for saving frames
os.makedirs("temp_frames", exist_ok=True)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Load the CSV into a DataFrame for actor details lookup
actors_data = pd.read_csv(csv_path)

# Create a mapping of folder names to actor names in the CSV
folder_to_actor = {name.replace(" ", "_"): name for name in actors_data['name']}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


catalog = pd.read_csv("catalog/catalog.csv")

@app.route('/')
def index2():
    return render_template('index.html')

@app.route('/real_time_face_recognisation')
def index():
    return render_template('real_time_face_recognisation.html')

@app.route('/get_recognisation')
def index3():
    return render_template('get_recognisation.html')

@app.route('/check_actor')
def index4():
    return render_template('check_actor.html')

@app.route('/live_emotion_detection')
def index5():
    return render_template('live_emotion_detection.html')


app.config['VIDEO_FOLDER'] = os.path.join(os.getcwd(), 'static', 'video')

@app.route('/video/<filename>')
def video(filename):
    # Ensure the video file is found and served correctly
    return send_from_directory(app.config['VIDEO_FOLDER'], filename)


@app.route('/pause', methods=['POST'])
def pause_video():


    if 'image' not in request.files:
        return jsonify({"error": "No image file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename)
        image_path = f"temp_frames/{timestamp}_{filename}"
        file.save(image_path)

        try:
            # Try extracting faces and handle the case if no faces are detected
            try:
                faces = DeepFace.extract_faces(img_path=image_path, detector_backend='opencv')
            except ValueError:
                return jsonify({"message": "No faces detected in the image. No actors found."})

            actors = []
            seen_actors = set()  # To track unique actors

            for face in faces:
                result = DeepFace.find(img_path=image_path, db_path=db_path, model_name="VGG-Face", enforce_detection=True)

                # Check if the result is empty or invalid
                if result and len(result) > 0 and result[0].empty:
                    continue  # Skip if no match is found for this face
                elif result and len(result) > 0:
                    identity = result[0]['identity'].values[0]
                    folder_name = identity.split('\\')[-2]

                    # Match folder name with actor name in CSV
                    if folder_name in folder_to_actor:
                        actor_name = folder_to_actor[folder_name]

                        # Skip if the actor has already been added
                        if actor_name not in seen_actors:
                            # Retrieve actor details from the CSV
                            actor_row = actors_data[actors_data['name'] == actor_name]
                            if not actor_row.empty:
                                born = actor_row.iloc[0]['born']
                                known_for = actor_row.iloc[0]['known_for']
                                
                                # Emotion detection using DeepFace
                                analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=True)
                                emotion = analysis[0]['dominant_emotion'] if analysis else "Unknown"
                                
                                # Construct the path to the matched actor image inside dataset_images
                                matched_image_path = os.path.join(db_path, folder_name, f"{actor_name.replace(' ', '_')}.jpg")

                                # Construct the URL for the matched image (adjusted for static files)
                                matched_image_url = f"{request.host_url}dataset_images/{folder_name}/{actor_name.replace(' ', '_')}.jpg"

                                # Find all movies in the catalog where actor_name is present
                                all_movies_in_platform = catalog[catalog["actor_name"].str.contains(actor_name, case=False, na=False)]["movie_name"].tolist()

                                actors.append({
                                    "name": actor_name,
                                    "born": born,
                                    "known_for": known_for,
                                    "emotion": emotion,  
                                    "matched_image_url": matched_image_url,  
                                    "all_movies_in_platform": all_movies_in_platform  
                                })
                                seen_actors.add(actor_name)  

            # Return no actors found message if no actors were matched
            if not actors:
                return jsonify({"message": "No actors found"})
            
            response = jsonify({"actors": actors})
            response.headers.add('Access-Control-Allow-Origin', '*')

            return jsonify({"actors": actors})

        except Exception as e:
            # Improved error handling to catch any unexpected errors
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format. Please upload a valid image."}), 400
    



# New route to get famous icons and their image URLs
@app.route('/content/v1/global_icons', methods=['GET'])
def get_famous_icons():
    try:
        # Assuming you want to return a list of famous actors and their images
        famous_icons = []

        # Here, you can modify the logic to fetch the famous actors and their image URLs
        for actor in actors_data['name']:
            folder_name = actor.replace(" ", "_")
            actor_name = actor
            matched_image_url = f"{request.host_url}dataset_images/{folder_name}/{actor_name.replace(' ', '_')}.jpg"

            famous_icons.append({
                "name": actor_name,
                "image_url": matched_image_url
            })

        return jsonify({"icons": famous_icons})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# http://127.0.0.1:5000/get_recognition?input=partner    

@app.route('/get_recognition', methods=['GET'])
def get_recognition():
    # Get the input parameter from the query string
    input_value = request.args.get('input')
    
    if not input_value:
        return jsonify({"error": "Input parameter 'input' is required"}), 400
    
    # Define the file path based on the input
    file_path = os.path.join('Already_recognised', f"{input_value}.json")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": f"File {input_value}.json not found"}), 404

    # Read and return the JSON content
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"}), 500


@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    if 'image' not in request.files:
        return jsonify({"error": "No image file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename)
        image_path = f"temp_frames/{timestamp}_{filename}"
        file.save(image_path)

        try:
            # Emotion detection using DeepFace
            analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=True)

            # Check if emotion analysis is successful
            if analysis:
                emotion = analysis[0]['dominant_emotion']  # Extract the dominant emotion
                return jsonify({"emotion": emotion})

            else:
                return jsonify({"error": "Could not detect emotions in the image"}), 400

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    else:
        return jsonify({"error": "Invalid file format. Please upload a valid image."}), 400


if __name__ == "__main__":
    app.run(debug=True)

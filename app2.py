from flask import Flask, render_template, Response
import cv2
import time

app = Flask(__name__)

# Video path and timestamps file
video_path = "salman_dialogue_short.mp4"  # Replace with your video path
timestamps_file = "actor_timestamps.txt"  # File containing actor timestamps

# Read actor timestamps into a list
timestamps = []
with open(timestamps_file, "r") as file:
    lines = file.readlines()[1:]  # Skip header
    for line in lines:
        timestamp, actor, _ = line.strip().split(", ")
        timestamps.append((float(timestamp), actor))  # Store as (time, actor)

# Initialize video capture
cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)  # Explicitly use FFmpeg
fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
frame_time = 1 / fps  # Time per frame

# Disable multi-threading in OpenCV to avoid threading issues on Windows
cv2.setNumThreads(1)

def generate_frames():
    frame_count = 0
    current_actor = None
    current_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate timestamp in seconds
        current_time = frame_count * frame_time

        # Check if we need to display actor name at this timestamp
        for timestamp, actor in timestamps:
            if abs(current_time - timestamp) < 0.1:  # Allowing a small window for matching
                current_actor = actor
                break

        # Show actor's name on the side, not on the video frame
        if current_actor:
            # Create a black rectangle for the actor name on the side
            side_rect = cv2.rectangle(frame, (640, 0), (800, 50), (0, 0, 0), -1)
            cv2.putText(side_rect, f"Actor: {current_actor}", (650, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Display the current time below the video frame
        cv2.putText(frame, f"Time: {current_time:.2f}s", (10, 350),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        frame_count += 1
        time.sleep(frame_time)  # Ensure correct frame rate

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/reset_video')
def reset_video():
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset the video to the beginning
    return render_template('index.html')  # Re-render the page to display video again

if __name__ == "__main__":
    app.run(debug=True)

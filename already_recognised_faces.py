import cv2
from deepface import DeepFace
import os
import time  # Import time module

# Load video
video_path = "static/video/Partner.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Database path containing actor images
db_path = "dataset_images"  # Replace with your folder path
if not os.path.exists(db_path):
    print(f"Error: Database path {db_path} does not exist.")
    exit()

# Create output directory for frames
os.makedirs("temp_frames", exist_ok=True)

# Create or overwrite a text file to save timestamps for actors
output_file_actor = "actors_face_recognised.txt"
with open(output_file_actor, "w") as f:
    f.write("Timestamp (s), Actor Name\n")  # Header for the actor file

# Process every 5th frame
frame_count = 0
frame_skip = 5  # Process every 5th frame
fps = cap.get(cv2.CAP_PROP_FPS)  # Get frame rate of the video

if fps == 0:
    print("Error: Could not get FPS from video.")
    exit()

# Track total execution time
start_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Process only every 5th frame
    if frame_count % frame_skip == 0:
        # Calculate timestamp in seconds
        timestamp = frame_count / fps

        # Save current frame temporarily
        frame_path = f"temp_frames/frame_{frame_count}.jpg"
        cv2.imwrite(frame_path, frame)

        try:
            # Measure time taken for face recognition
            frame_start_time = time.time()

            # Perform face recognition
            result = DeepFace.find(img_path=frame_path, db_path=db_path, model_name="VGG-Face", enforce_detection=False)

            frame_end_time = time.time()
            processing_time = frame_end_time - frame_start_time  # Time taken for the frame

            # Check if any match found for the actor
            if len(result[0]) > 0:
                # Get actor name
                identity = result[0]['identity'].values[0]
                actor_name = identity.split('/')[-1].split('.')[0]  # Extract name from path

                # Save actor timestamp to file
                with open(output_file_actor, "a") as f:
                    f.write(f"{timestamp:.2f}, {actor_name}\n")

                # Display actor name on the frame
                cv2.putText(frame, f"Actor: {actor_name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                print(f"Actor Match Found at {timestamp:.2f}s - {actor_name}")

            else:
                cv2.putText(frame, "No Match", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        except Exception as e:
            print(f"Error at {timestamp:.2f}s:", str(e))
            cv2.putText(frame, "Error/No Face", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Increment frame count
    frame_count += 1

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Total execution time
end_time = time.time()
total_time = end_time - start_time

print(f"Results saved in {output_file_actor}")
print(f"Total processing time: {total_time:.2f} seconds")

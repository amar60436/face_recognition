import json

# Read the input file
input_file = "partner_actors_face_recognised.txt"
result = {}

# Open the file and process the lines
with open(input_file, 'r') as file:
    # Skip the header line
    next(file)
    
    for line in file:
        # Split the line by comma
        timestamp_str, actor_path = line.strip().split(', ')
        
        # Convert the timestamp to a float
        timestamp = float(timestamp_str)
        
        # Convert the timestamp into minutes:seconds format
        minutes = int(timestamp // 60)
        seconds = round(timestamp % 60, 2)
        time_key = f"{minutes}:{str(int(seconds)).zfill(2)}"
        
        # Extract the actor name (middle part of the path)
        actor_name = actor_path.split("\\")[1]  # The second part, e.g., 'Govinda'
        
        # Add the timestamp to the actor's list, ensuring uniqueness
        if actor_name not in result:
            result[actor_name] = []
        if time_key not in result[actor_name]:
            result[actor_name].append(time_key)

# Convert the result to JSON
output_json = json.dumps(result, indent=4)

# Print the result
print(output_json)

# Optionally, save to a file
with open('output.json', 'w') as json_file:
    json_file.write(output_json)

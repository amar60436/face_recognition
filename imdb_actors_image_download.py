import csv
import os
import requests
from imdb import IMDb

# Create an instance of the IMDb class
ia = IMDb()

# Base folder where the images will be saved
BASE_FOLDER = 'dataset_folder'

# Function to get top 4 actor images for a given movie
def get_top_actors_images(movie_name, movie_year):
    # Search for the movie
    movies = ia.search_movie(f"{movie_name} {movie_year}")
    if not movies:
        print(f"Movie {movie_name} ({movie_year}) not found on IMDb")
        return []
    
    movie = movies[0]  # Get the first result from the search
    
    # Get top 4 actors
    ia.update(movie)
    top_actors = movie.get('cast', [])[:4]
    
    actor_images = []
    
    for actor in top_actors:
        actor_name = actor['name']
        ia.update(actor)
        # Get actor's image URL
        actor_image_url = actor.get('full-size headshot', None)
        if actor_image_url:
            actor_images.append((actor_name, actor_image_url))
        else:
            print(f"No image found for {actor_name}")
    
    return actor_images

# Function to save the actor's image inside a folder named after the actor
def save_actor_image(actor_name, image_url):
    # Normalize actor name for folder creation
    folder_name = actor_name.replace(' ', '_').lower()
    folder_path = os.path.join(BASE_FOLDER, folder_name)

    # Check if the folder exists (case-insensitive)
    if not any(folder_name.lower() == f.lower() for f in os.listdir(BASE_FOLDER)):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

    # Save the image in the actor's folder
    image_name = f"{actor_name.replace(' ', '_')}.jpg"
    image_path = os.path.join(folder_path, image_name)

    # Download the image
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Saved {actor_name}'s image in {folder_path}")
    else:
        print(f"Failed to download image for {actor_name}. Status code: {response.status_code}")

# Load movie data from CSV
csv_file = 'catalog/catalog.csv'  # Change this to your actual CSV file path

with open(csv_file, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        movie_name = row['movie_name']
        movie_year = row['release_year']
        
        print(f"Processing {movie_name} ({movie_year})...")
        
        # Get top 4 actor images
        actor_images = get_top_actors_images(movie_name, movie_year)
        
        if actor_images:
            for actor_name, image_url in actor_images:
                save_actor_image(actor_name, image_url)

import csv
import requests
from bs4 import BeautifulSoup
from imdb import IMDb

# Create an instance of the IMDb class
ia = IMDb()

# Function to fetch "Born" information from an actor's IMDb page
def fetch_born_info(actor_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(actor_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        birth_date_section = soup.find('div', {'data-testid': 'birth-and-death-birthdate'})
        if birth_date_section:
            spans = birth_date_section.find_all('span', class_='sc-59a43f1c-2 bMLVWg')
            if spans and len(spans) > 1:
                return spans[1].text  # Return the second span containing the birth date
    return "Born information not found"

# Function to fetch "Known for" movies from an actor's IMDb page
def fetch_known_for(actor_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(actor_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        og_description = soup.find('meta', {'property': 'og:description'})
        if og_description:
            content = og_description.get('content', '')
            if 'Known for:' in content:
                return content.split('Known for:')[1].strip()
    return "Known for information not found"

# Function to get the top 4 actors and their "Born" and "Known for" information for a given movie
def get_top_actors_info(movie_name, movie_year):
    # Search for the movie
    movies = ia.search_movie(f"{movie_name} {movie_year}")
    if not movies:
        print(f"Movie {movie_name} ({movie_year}) not found on IMDb")
        return []
    
    movie = movies[0]  # Get the first result from the search
    
    # Get top 4 actors
    ia.update(movie)
    top_actors = movie.get('cast', [])[:4]
    
    actor_info = []
    for actor in top_actors:
        actor_name = actor['name']
        actor_id = actor.personID
        actor_url = f"https://www.imdb.com/name/nm{actor_id}/"  # Construct IMDb URL
        born_info = fetch_born_info(actor_url)
        known_for_info = fetch_known_for(actor_url)
        actor_info.append({"name": actor_name, "born": born_info, "known_for": known_for_info})
    
    return actor_info

# Load data from test3.csv and fetch data for actors
def process_csv(input_csv, output_csv):
    seen_actors = set()  # To avoid processing duplicate actors
    results = []

    with open(input_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie_name = row.get("movie_name")
            movie_year = row.get("release_year")

            if movie_name and movie_year:
                print(f"Processing {movie_name} ({movie_year})...")
                actors_info = get_top_actors_info(movie_name, movie_year)
                for actor in actors_info:
                    if actor["name"] not in seen_actors:
                        seen_actors.add(actor["name"])
                        results.append(actor)

    # Write the results to the output CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "born", "known_for"])
        writer.writeheader()
        writer.writerows(results)

# Example usage
input_csv = "catalog/catalog.csv"
output_csv = "actors_enhanced_data/actors_info_updated.csv"
process_csv(input_csv, output_csv)

print(f"Saved updated actor information to {output_csv}")

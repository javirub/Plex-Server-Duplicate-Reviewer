from plexapi.server import PlexServer
import csv

# URL from Plex Server
BASEURL = 'http://127.0.0.1:32400'  # This is for local server, change it to your server URL
TOKEN = 'Your-Token-Here'  # This is your Plex Token


# Connect to the Plex Server
plex = PlexServer(BASEURL, TOKEN)

# Select the library that you want to check
library = plex.library.section('Films')  # Change 'Films' to the name of your library

# Get all movies from the library
movies = library.all()

# List movies with more than one file
csv_rows = []

for movie in movies:
    files = [part.file for media in movie.media for part in media.parts]
    if len(files) > 1:
        for file in files:
            csv_rows.append([movie.title, file])

# Save the results in a CSV file
with open('multi_file_movies.csv', mode='w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Movie', 'File'])
    csv_writer.writerows(csv_rows)

print("Results saved as 'multi_file_movies.csv'")
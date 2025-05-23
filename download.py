import requests

# Your Pixabay API key
API_KEY = "49921335-048067464a6481c83ce1cf60c"
# The search query for the image you want
query = "nature"
# Pixabay API endpoint
url = f"https://pixabay.com/api/?key={API_KEY}&q={query}&image_type=photo&per_page=1"

# Send a GET request to the Pixabay API
response = requests.get(url)
# Parse the JSON response
data = response.json()

# Check if any images were found
if data["hits"]:
    # Get the URL of the first image
    image_url = data["hits"][0]["largeImageURL"]
    # Download the image
    img_data = requests.get(image_url).content
    # Save the image to a file
    with open("downloaded_image.jpg", "wb") as f:
        f.write(img_data)
    print("Image downloaded successfully!")
else:
    print("No images found for the query.")
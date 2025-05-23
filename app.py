# main flask app
from flask import Flask, render_template, request
import random
import copy
from download import create_download_link, register_download_routes

app = Flask(__name__)

# Register download routes
register_download_routes(app)

# Dictionary of compliments
compliments = {
    "A": ["Admirable", "Awesome", "Ambitious", "Amazing", "Affectionate", "Astounding"],
    "B": ["Brilliant", "Bold", "Benevolent", "Beautiful", "Bright", "Balanced"],
    "C": ["Charismatic", "Creative", "Compassionate", "Charming", "Courageous", "Capable"],
    "D": ["Daring", "Dedicated", "Dynamic", "Delightful", "Dependable", "Determined"],
    "E": ["Elegant", "Excellent", "Empathetic", "Energetic", "Exceptional", "Encouraging"],
    "F": ["Fabulous", "Fearless", "Friendly", "Fantastic", "Faithful", "Flexible"],
    "G": ["Generous", "Gracious", "Gifted", "Genuine", "Glorious", "Grounded"],
    "H": ["Honest", "Humble", "Hopeful", "Hardworking", "Helpful", "Harmonious"],
    "I": ["Incredible", "Innovative", "Inspiring", "Impressive", "Intelligent", "Independent"],
    "J": ["Joyful", "Just", "Jubilant", "Jolly", "Judicious", "Jaw-dropping"],
    "K": ["Kind-hearted", "Knowledgeable", "Keen", "Kingly", "Kaleidoscopic", "Kinetic"],
    "L": ["Loving", "Loyal", "Legendary", "Luminous", "Leader-like", "Logical"],
    "M": ["Magnificent", "Motivated", "Mindful", "Marvelous", "Meticulous", "Mighty"],
    "N": ["Noble", "Nurturing", "Noteworthy", "Neighborly", "Neat", "Nonjudgmental"],
    "O": ["Outstanding", "Optimistic", "Original", "Open-minded", "Observant", "Organized"],
    "P": ["Patient", "Passionate", "Powerful", "Polished", "Pleasant", "Pioneering"],
    "Q": ["Quick-witted", "Quietly-confident", "Quintessential", "Quirky", "Quality-focused", "Questioning"],
    "R": ["Resilient", "Radiant", "Reliable", "Remarkable", "Resourceful", "Respectful"],
    "S": ["Strong", "Sincere", "Spectacular", "Smart", "Supportive", "Sophisticated"],
    "T": ["Talented", "Trustworthy", "Thoughtful", "Tenacious", "Thriving", "Terrific"],
    "U": ["Unique", "Understanding", "Unstoppable", "Upbeat", "Uplifting", "Ultimate"],
    "V": ["Vibrant", "Virtuous", "Visionary", "Valiant", "Versatile", "Victorious"],
    "W": ["Wise", "Warm-hearted", "Wonderful", "Welcoming", "Well-rounded", "Witty"],
    "X": ["Xenial", "Xtraordinary", "Xceptional", "Xpressive", "Xemplary", "Xciting"],
    "Y": ["Youthful", "Yielding", "Yearning-for-excellence", "Yen-for-knowledge", "Yes-minded", "Yummy-hearted"],
    "Z": ["Zealous", "Zesty", "Zany", "Zen-like", "Zestful", "Zoom-focused"]
}


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/compliment", methods=["POST"])
def compliment(name=None, return_results=False):

    if name is None:
        name = request.form.get("name", "").upper()
    else:
        name = name.upper()
        
    results = []
    
    # Keep track of used compliments for each letter
    used_compliments = {}
    # Count how many times each letter appears in the name
    letter_count = {}
    
    # Count letters first to check if we have enough compliments for each letter
    for letter in name:
        if letter in compliments and letter != " ":
            letter_count[letter] = letter_count.get(letter, 0) + 1
    
    # For each unique letter, make a copy of available compliments
    for letter in letter_count:
        # If we don't have enough unique compliments for this letter, we'll have to allow repeats
        if letter_count[letter] > len(compliments[letter]):
            used_compliments[letter] = []
        else:
            used_compliments[letter] = []
    
    # Handle each letter in the name, skipping characters not in our dictionary
    for letter in name:
        if letter in compliments:
            available_compliments = [c for c in compliments[letter] if c not in used_compliments.get(letter, [])]
            
            # If we've used all compliments for this letter, reset the used list
            # This only happens if there are more instances of the letter than available compliments
            if not available_compliments:
                used_compliments[letter] = []
                available_compliments = compliments[letter]
            
            # Select a random compliment from the available ones
            selected_compliment = random.choice(available_compliments)
            used_compliments.setdefault(letter, []).append(selected_compliment)
        elif letter == " ":
            results.append((letter, "", ""))
    
    # If no valid letters were found, provide a default message
    if not results:
        results = [("", "Your name is unique! Try entering letters A-Z.", "✨")]
    
    if return_results:
        return results
    
    # Generate the download link with Python instead of JavaScript
    download_link = create_download_link(name, results)
    
    return render_template("result.html", name=name, results=results, download_link=download_link)

if __name__ == "__main__":
    app.run(debug=True)

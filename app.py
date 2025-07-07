# main flask app
from flask import Flask, render_template, request
import random
import copy

app = Flask(__name__)


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

# Dictionary of emojis (increased variety for each letter)
emojis = {
    "A": ["🌟", "🦄", "✨", "😃", "💫", "🥇", "🍏", "🧩", "🦋", "🎈"],
    "B": ["🎉", "🌈", "😎", "💡", "🎈", "🦋", "🍌", "🧸", "🦄", "🎂"],
    "C": ["🌻", "🍀", "🎨", "🧠", "🦸", "🌊", "🍫", "🦜", "🧁", "🎃"],
    "D": ["🔥", "💪", "🎯", "🌞", "🏆", "🦅", "🍩", "🦖", "🧭", "🎲"],
    "E": ["🌹", "🎶", "🦉", "🧚", "🦢", "🌼", "🍆", "🦅", "🧝", "🎗️"],
    "F": ["🍀", "🦊", "🎁", "🌸", "🧩", "🦄", "🍟", "🦩", "🧚", "🎏"],
    "G": ["🌟", "🍇", "🦒", "🎸", "🧸", "🌳", "🍀", "🦍", "🧤", "🎻"],
    "H": ["🏅", "🦔", "🎩", "🌺", "🧲", "🦉", "🍯", "🦛", "🧡", "🎃"],
    "I": ["🦋", "🌈", "🧠", "🎇", "🦄", "🌟", "🍦", "🦑", "🧊", "🎐"],
    "J": ["🎷", "🦘", "🎊", "🧃", "🦄", "🎺", "🍏", "🦡", "🧩", "🎲"],
    "K": ["🥝", "🦘", "🎋", "🧿", "🦄", "🎠", "🍪", "🦏", "🧀", "🎋"],
    "L": ["🍋", "🦁", "🌙", "🧡", "🦄", "🌲", "🍭", "🦙", "🧊", "🎶"],
    "M": ["🌝", "🦣", "🎵", "🧩", "🦄", "🌻", "🍈", "🦡", "🧁", "🎹"],
    "N": ["🌃", "🦑", "🎶", "🧸", "🦄", "🌵", "🍜", "🦏", "🧢", "🎷"],
    "O": ["🌞", "🦉", "🎱", "🧡", "🦄", "🍊", "🍩", "🦦", "🧅", "🎸"],
    "P": ["🍍", "🦚", "🎨", "🧸", "🦄", "🥧", "🍕", "🦜", "🧃", "🎭"],
    "Q": ["👑", "🦄", "🎸", "🧩", "🦄", "🌟", "🍳", "🦆", "🧞", "🎯"],
    "R": ["🌈", "🦏", "🎻", "🧡", "🦄", "🌹", "🍎", "🦝", "🧢", "🎀"],
    "S": ["🌞", "🦥", "🎷", "🧡", "🦄", "🌸", "🍓", "🦦", "🧦", "🎸"],
    "T": ["🌴", "🦃", "🎺", "🧡", "🦄", "🌻", "🍅", "🦖", "🧵", "🎩"],
    "U": ["☂️", "🦄", "🎵", "🧡", "🦄", "🌊", "🍇", "🦙", "🧇", "🎷"],
    "V": ["🌋", "🦚", "🎻", "🧡", "🦄", "🌟", "🍉", "🦘", "🧛", "🎻"],
    "W": ["🌊", "🦓", "🎷", "🧡", "🦄", "🌻", "🍉", "🦢", "🧇", "🎩"],
    "X": ["❌", "🦄", "🎲", "🧩", "🦄", "🌟", "🍫", "🦓", "🧊", "🎮"],
    "Y": ["🌱", "🦓", "🎸", "🧡", "🦄", "🌼", "🍋", "🦒", "🧁", "🎷"],
    "Z": ["⚡", "🦓", "🎶", "🧡", "🦄", "🌟", "🍕", "🦓", "🧢", "🎺"]
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
    
    # Keep track of used compliments and emojis for each letter
    used_compliments = {}
    used_emojis = {}
    # Count how many times each letter appears in the name
    letter_count = {}
    
    # Count letters first to check if we have enough compliments/emojis for each letter
    for letter in name:
        if letter in compliments and letter != " ":
            letter_count[letter] = letter_count.get(letter, 0) + 1
    
    # For each unique letter, make a copy of available compliments and emojis
    for letter in letter_count:
        used_compliments[letter] = []
        used_emojis[letter] = []
    
    # Handle each letter in the name, skipping characters not in our dictionary
    for letter in name:
        if letter in compliments:
            # Compliment selection without repetition
            available_compliments = [c for c in compliments[letter] if c not in used_compliments[letter]]
            if not available_compliments:
                used_compliments[letter] = []
                available_compliments = compliments[letter][:]
            selected_compliment = random.choice(available_compliments)
            used_compliments[letter].append(selected_compliment)

            # Emoji selection without repetition
            available_emojis = [e for e in emojis.get(letter, ["✨"]) if e not in used_emojis[letter]]
            if not available_emojis:
                used_emojis[letter] = []
                available_emojis = emojis.get(letter, ["✨"])[:]
            selected_emoji = random.choice(available_emojis)
            used_emojis[letter].append(selected_emoji)

            results.append((letter, selected_compliment, selected_emoji))
        elif letter == " ":
            results.append((letter, "", ""))

    # If no valid letters were found, provide a default message
    if not results:
        results = [("", "Your name is unique! Try entering letters A-Z.", "✨")]

    if return_results:
        return results

    return render_template("result.html", name=name, results=results)

if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True)

# main flask app
from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import random
import copy
import os
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complementor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date, default=date.today)
    
    def __repr__(self):
        return f'<UserSession {self.name} - {self.timestamp}>'

class DailyStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    user_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<DailyStats {self.date} - {self.user_count}>'

admin_token = os.getenv('ADMIN_TOKEN')

def log_user_session(name):
    """Log a user session using SQLAlchemy"""
    # Create new session record
    session = UserSession(name=name)
    db.session.add(session)
    
    # Update daily stats
    today = date.today()
    daily_stat = DailyStats.query.filter_by(date=today).first()
    if daily_stat:
        daily_stat.user_count += 1
    else:
        daily_stat = DailyStats(date=today, user_count=1)
        db.session.add(daily_stat)
    
    db.session.commit()

def get_stats():
    """Get statistics for admin dashboard"""
    today = date.today()
    
    # Total users (all sessions)
    total_users = UserSession.query.count()
    
    # Today's users
    today_users = UserSession.query.filter(UserSession.date == today).count()
    
    # Total sessions (same as total users in this case)
    total_sessions = total_users
    
    # Active days (days with at least one session)
    active_days = DailyStats.query.count()
    
    return {
        'total_users': total_users,
        'today_users': today_users,
        'total_sessions': total_sessions,
        'active_days': active_days
    }

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

# Dictionary of emojis (rearranged to match compliments better)
emojis = {
    "A": ["🌟", "🏆", "🎯", "💪", "❤️", "✨", "🚀", "👑", "🦅", "🔥"],  # Admirable, Awesome, Ambitious, Amazing, Affectionate, Astounding
    "B": ["🧠", "🦁", "💖", "🌺", "☀️", "⚖️", "✨", "🎨", "🌟", "💎"],  # Brilliant, Bold, Benevolent, Beautiful, Bright, Balanced
    "C": ["✨", "🎨", "💝", "😊", "🦁", "💪", "🌟", "🎭", "🎪", "🏆"],  # Charismatic, Creative, Compassionate, Charming, Courageous, Capable
    "D": ["🦁", "🎯", "⚡", "🌟", "🛡️", "💪", "🚀", "🌈", "🔥", "🏔️"],  # Daring, Dedicated, Dynamic, Delightful, Dependable, Determined
    "E": ["👑", "🏆", "💖", "⚡", "🌟", "📣", "🌹", "🦋", "💎", "🎪"],  # Elegant, Excellent, Empathetic, Energetic, Exceptional, Encouraging
    "F": ["🌟", "🦁", "🤝", "🎉", "🤗", "🌿", "✨", "💖", "🎈", "🌈"],  # Fabulous, Fearless, Friendly, Fantastic, Faithful, Flexible
    "G": ["🎁", "🙏", "🎁", "💯", "👑", "🌍", "💖", "🌟", "🤝", "🌱"],  # Generous, Gracious, Gifted, Genuine, Glorious, Grounded
    "H": ["💯", "🙏", "🌟", "💪", "🤝", "🎵", "❤️", "⚖️", "🌈", "🕊️"],  # Honest, Humble, Hopeful, Hardworking, Helpful, Harmonious
    "I": ["🌟", "💡", "🔥", "👑", "🧠", "🚀", "✨", "💪", "🎯", "🦄"],  # Incredible, Innovative, Inspiring, Impressive, Intelligent, Independent
    "J": ["😊", "⚖️", "🎉", "😄", "🧠", "😲", "🌟", "🎪", "💖", "🎈"],  # Joyful, Just, Jubilant, Jolly, Judicious, Jaw-dropping
    "K": ["💖", "📚", "🎯", "👑", "🌈", "⚡", "🤝", "💡", "🦋", "🌟"],  # Kind-hearted, Knowledgeable, Keen, Kingly, Kaleidoscopic, Kinetic
    "L": ["💝", "🤝", "👑", "✨", "🦁", "🧠", "❤️", "🏆", "🌟", "💖"],  # Loving, Loyal, Legendary, Luminous, Leader-like, Logical
    "M": ["👑", "🚀", "🧘", "🌟", "🔍", "💪", "✨", "🦁", "🎯", "🏆"],  # Magnificent, Motivated, Mindful, Marvelous, Meticulous, Mighty
    "N": ["👑", "🌱", "🏆", "🤝", "✨", "🙏", "🎯", "💖", "⚖️", "🌟"],  # Noble, Nurturing, Noteworthy, Neighborly, Neat, Nonjudgmental
    "O": ["🌟", "☀️", "💡", "🧠", "👁️", "📋", "🏆", "🚀", "🎯", "✨"],  # Outstanding, Optimistic, Original, Open-minded, Observant, Organized
    "P": ["🙏", "🔥", "💪", "💎", "😊", "🚀", "🌟", "🎯", "💖", "🦋"],  # Patient, Passionate, Powerful, Polished, Pleasant, Pioneering
    "Q": ["🧠", "🤫", "👑", "🎭", "🎯", "❓", "⚡", "💡", "🌟", "🔍"],  # Quick-witted, Quietly-confident, Quintessential, Quirky, Quality-focused, Questioning
    "R": ["🦋", "✨", "🛡️", "🌟", "💡", "🙏", "🚀", "💪", "🔥", "🏆"],  # Resilient, Radiant, Reliable, Remarkable, Resourceful, Respectful
    "S": ["💪", "💖", "🌟", "🧠", "🤝", "💎", "🏆", "🎯", "🚀", "✨"],  # Strong, Sincere, Spectacular, Smart, Supportive, Sophisticated
    "T": ["🌟", "🤝", "💭", "💪", "🌱", "🎉", "🏆", "💖", "🎯", "🚀"],  # Talented, Trustworthy, Thoughtful, Tenacious, Thriving, Terrific
    "U": ["🦄", "🤗", "🚀", "😊", "🌟", "👑", "💖", "⚡", "🔥", "✨"],  # Unique, Understanding, Unstoppable, Upbeat, Uplifting, Ultimate
    "V": ["🌈", "👑", "🔮", "🦁", "🎭", "🏆", "⚡", "🚀", "💪", "🌟"],  # Vibrant, Virtuous, Visionary, Valiant, Versatile, Victorious
    "W": ["🧠", "💖", "🌟", "🤗", "🌍", "😄", "🦉", "💡", "🌈", "✨"],  # Wise, Warm-hearted, Wonderful, Welcoming, Well-rounded, Witty
    "X": ["🤝", "🌟", "🏆", "🎭", "👑", "🎉", "⚡", "🚀", "💖", "✨"],  # Xenial, Xtraordinary, Xceptional, Xpressive, Xemplary, Xciting
    "Y": ["🌱", "🤝", "🏆", "📚", "✅", "💖", "😊", "🌟", "⚡", "🎯"],  # Youthful, Yielding, Yearning-for-excellence, Yen-for-knowledge, Yes-minded, Yummy-hearted
    "Z": ["🔥", "⚡", "🎭", "🧘", "🌟", "🎯", "🚀", "💪", "🏆", "✨"]   # Zealous, Zesty, Zany, Zen-like, Zestful, Zoom-focused
}


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/compliment", methods=["POST"])
def compliment(name=None, return_results=False):
    if name is None:
        name = request.form.get("name", "").upper()
        # Log the user session
        log_user_session(name)
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

@app.route("/admin")
def admin_login():
    return render_template('admin_login.html')

@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if request.method == "POST":
        token = request.form.get("token")
        if token != admin_token:
            return render_template('admin_login.html', error="Invalid admin token")
    else:
        # Check for token in query params
        token = request.args.get("token")
        if token != admin_token:
            return render_template('admin_login.html', error="Access denied")
    
    try:
        # Get stats from database
        stats = get_stats()
        
        # Get recent sessions (last 10)
        recent_sessions = UserSession.query.order_by(UserSession.timestamp.desc()).limit(10).all()
        
        # Get daily stats for chart/display
        daily_stats = DailyStats.query.order_by(DailyStats.date.desc()).limit(30).all()
        
        # Convert recent_sessions to dict format for template compatibility
        recent_sessions_list = []
        for session in recent_sessions:
            recent_sessions_list.append({
                'name': session.name,
                'timestamp': session.timestamp.isoformat(),
                'date': session.date.strftime('%Y-%m-%d')
            })
        
        # Convert daily_stats to dict format for template compatibility
        daily_stats_dict = {}
        for daily_stat in daily_stats:
            daily_stats_dict[daily_stat.date.strftime('%Y-%m-%d')] = daily_stat.user_count
        
        # Add sessions and daily_stats to stats for template compatibility
        stats['sessions'] = recent_sessions_list
        stats['daily_stats'] = daily_stats_dict
        
        return render_template('admin_dashboard.html', 
                             stats=stats, 
                             recent_sessions=recent_sessions_list,
                             daily_stats=daily_stats,
                             today_count=stats['today_users'])
    except Exception as e:
        print(f"Error in admin dashboard: {e}")
        return f"Error: {str(e)}", 500

@app.route("/download/<name>")
def download_compliment(name):
    """Generate and download compliment results as an image"""
    try:
        # Get the compliment results for the name
        results = compliment(name.upper(), return_results=True)
        
        # Create image
        img_width, img_height = 800, 600
        background_color = (255, 255, 255)  # White background
        text_color = (51, 51, 51)  # Dark gray text
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default if not available
        try:
            title_font = ImageFont.truetype("arial.ttf", 36)
            name_font = ImageFont.truetype("arial.ttf", 28)
            compliment_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            compliment_font = ImageFont.load_default()
        
        # Draw title
        title = "Your Personalized Compliments"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((img_width - title_width) // 2, 50), title, fill=text_color, font=title_font)
        
        # Draw name
        name_text = f"Hello, {name.title()}!"
        name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
        name_width = name_bbox[2] - name_bbox[0]
        draw.text(((img_width - name_width) // 2, 100), name_text, fill=text_color, font=name_font)
        
        # Draw compliments
        y_position = 160
        for letter, compliment, emoji in results:
            if letter and compliment:  # Skip empty entries
                compliment_text = f"{letter}: {compliment} {emoji}"
                
                # Wrap text if it's too long
                wrapped_text = textwrap.fill(compliment_text, width=50)
                lines = wrapped_text.split('\n')
                
                for line in lines:
                    line_bbox = draw.textbbox((0, 0), line, font=compliment_font)
                    line_width = line_bbox[2] - line_bbox[0]
                    draw.text(((img_width - line_width) // 2, y_position), line, fill=text_color, font=compliment_font)
                    y_position += 35
                
                y_position += 10  # Extra space between compliments
        
        # Add footer
        footer = "Generated by Complementor App"
        footer_bbox = draw.textbbox((0, 0), footer, font=compliment_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(((img_width - footer_width) // 2, img_height - 50), footer, fill=(128, 128, 128), font=compliment_font)
        
        # Save image to memory
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Return file for download
        return send_file(
            img_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'{name.lower()}_compliments.png'
        )
        
    except Exception as e:
        print(f"Error generating download: {e}")
        return f"Error generating download: {str(e)}", 500

# Initialize database
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database initialized!")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

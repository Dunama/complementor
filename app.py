# main flask app
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import copy
import os
from datetime import datetime, date

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

# Initialize database
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database initialized!")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

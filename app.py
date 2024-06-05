from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define your models here...
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(100), default='default.png')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('topics', lazy=True))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='topic', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Your routes and views here...
@app.route('/')
def index():
    topics = Topic.query.order_by(Topic.created_at.desc()).all()
    return render_template('index.html', topics=topics)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/new_topic', methods=['GET', 'POST'])
@login_required
def new_topic():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        topic = Topic(title=title, content=content, author_id=current_user.id, created_at=datetime.now())
        db.session.add(topic)
        db.session.commit()
        flash('Topic created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('new_topic.html')

@app.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == 'POST':
        content = request.form['content']
        comment = Comment(content=content, author_id=current_user.id, topic_id=topic.id, created_at=datetime.now())
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('topic', topic_id=topic.id))
    return render_template('topic.html', topic=topic)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

import os

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SECRET_KEY']='your-secret-key-here'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 2* 1024 * 1024 #2MB LIMIT


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Book(db.Model):
           id = db.Column(db.Integer, primary_key = True)
           title = db.Column(db.String(200), nullable = False)
           author = db.Column(db.String(200), nullable = False)
           current_page = db.Column(db.Integer, nullable = False)
           total_pages = db.Column(db.Integer, nullable = False)
           finished = db.Column(db.Boolean, default = False)
           date_completed = db.Column(db.DateTime, nullable = True)
           user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
           
           def days_left(self,daily_pace=30):
                pages_left = self.total_pages - self.current_page
                return round(pages_left/daily_pace)
           
@app.route('/uploads/<filename>')
def uploaded_file(filename):
     return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


class User(db.Model,UserMixin):
     id = db.Column(db.Integer,primary_key = True)
     email = db.Column(db.String(200),unique=True, nullable = False)
     password = db.Column(db.String(200),nullable = False)

     books = db.relationship('Book',backref = 'owner',lazy = True)
     display_name = db.Column(db.String(100), nullable = True)
     favorite_genre = db.Column(db.String(100))
     daily_goal = db.Column(db.Integer, default = 0)
     yearly_goal = db.Column(db.Integer, default = 0)
     daily_pace = db.Column(db.Integer, default = 0)
     date_joined = db.Column(db.Date, default=date.today)

     pages_read_today = db.Column(db.Integer, default = 0)
     last_reset = db.Column(db.Date, default=None)

     profile_photo = db.Column(db.String(300),default = 'default.png')



@app.route('/profile', methods = ['GET','POST'])
@login_required
def profile():
     if request.method == 'POST':
          current_user.display_name = request.form.get('display_name')
          current_user.favorite_genre = request.form.get('favorite_genre')
          current_user.daily_goal = int(request.form.get('daily_goal', 0))
          current_user.yearly_goal = int(request.form.get('yearly_goal',0))

          if 'profile_photo' in request.files:
               file = request.files ['profile_photo']
               if file.filename != "":
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
                    file.save(filepath)
                    current_user.profile_photo = filename
          db.session.commit()
          flash('Profile updated successfully!')
          return redirect(url_for('profile'))
     return render_template('profile.html', user = current_user)

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
     if current_user.is_authenticated:
          return redirect(url_for('index'))
     
     if request.method =='POST':
          email = request.form['email']
          password = generate_password_hash(request.form['password'])

          if User.query.filter_by(email=email).first():
               flash ('User already exists!')
               print('Email already exists.')
               return render_template('signup.html')
          new_user = User(email = email, password = password)
          db.session.add(new_user)
          db.session.commit()
          return redirect(url_for('login'))
     return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        
        # Optional: Add a flash message here for invalid credentials
        print("Login failed: Invalid email or password")

    return render_template('login.html')


@app.route('/logout')
def logout():
     logout_user()
     return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def index():
     today = date.today()
     if current_user.last_reset != today:
         current_user.pages_read_today = 0
         current_user.last_reset = today
         db.session.commit()
     
     
     days_active = (date.today() - current_user.date_joined).days or 1
     total_pages = sum(book.current_page for book in current_user.books)
     average_pace = round(total_pages/days_active) if total_pages > 0 else 0

     books = Book.query.filter_by(finished = False, user_id= current_user.id).all()
     books_this_year = Book.query.filter(
          Book.date_completed >= datetime(2026,1,1)
    ).count()

     return render_template('dashboard.html', 
                            books=books, 
                            books_this_year = books_this_year, 
                            average_pace=average_pace)


@app.route('/add_book_form', methods=['GET', 'POST'])
def add_book_form():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        current_page = request.form['current_page']
        total_pages = request.form['total_pages']
        print(title, author, current_page, total_pages)
        new_book = Book(
            title = title,
            author = author,
            current_page = int(current_page),
            total_pages = int(total_pages),
            user_id = current_user.id
            )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_book_form.html')

@app.route('/delete/<int:id>', methods = ['POST'])
def delete_book(id):
     book = Book.query.get_or_404(id)
     db.session.delete(book)
     db.session.commit()
     return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)

    if request.method == 'POST':
        #For Stat Card
        old_page = book.current_page
        new_page = int(request.form['current_page'])

        #Track pages read today
        pages_read = max(new_page - old_page, 0)
        current_user.pages_read_today += pages_read

        #Update Book
        book.title = request.form['title']
        book.author = request.form['author']
        book.current_page = int(request.form['current_page'])
        book.total_pages = int(request.form['total_pages'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_book.html', book=book)


@app.route('/finish/<int:id>', methods = ['POST'])
def finish_book(id):
     book = Book.query.get_or_404(id)
     book.finished = True
     book.date_completed = datetime.now()
     db.session.commit()
     return redirect(url_for('index'))

@app.route('/completed_books')
def completed_books():
     books = Book.query.filter_by(finished = True).all()
     return render_template('completed_books.html', books = books)    

with app.app_context():
     db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
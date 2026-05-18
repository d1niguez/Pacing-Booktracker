from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

class Book(db.Model):
           id = db.Column(db.Integer, primary_key = True)
           title = db.Column(db.String(200), nullable = False)
           author = db.Column(db.String(200), nullable = False)
           current_page = db.Column(db.Integer, nullable = False)
           total_pages = db.Column(db.Integer, nullable = False)
           

books = [
    {"title": "The Lovely Bones", "author": "Alice Sebold", "current_page": 49, "total_pages": 500},
    {"title": "A Court of Thorns and Roses", "author": "Sarah J. Maas", "current_page": 90, "total_pages": 500},
    {"title": "The Fault in Our Stars", "author": "John Green", "current_page": 55, "total_pages": 500},
]



@app.route('/')
def index():
    books = Book.query.all()
    return render_template('dashboard.html', books=books)

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
            total_pages = int(total_pages)
            )
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('add_book_form.html')

with app.app_context():
     db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
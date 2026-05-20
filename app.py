from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

class Book(db.Model):
           id = db.Column(db.Integer, primary_key = True)
           title = db.Column(db.String(200), nullable = False)
           author = db.Column(db.String(200), nullable = False)
           current_page = db.Column(db.Integer, nullable = False)
           total_pages = db.Column(db.Integer, nullable = False)
           finished = db.Column(db.Boolean, default = False)
           date_completed = db.Column(db.DateTime, nullable = True)
           


@app.route('/')
def index():
    books = Book.query.filter_by(finished = False).all()
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
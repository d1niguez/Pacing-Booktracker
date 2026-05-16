from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

books = [
    {"title": "The Lovely Bones", "author": "Alice Sebold", "current_page": 49, "total_pages": 500},
    {"title": "A Court of Thorns and Roses", "author": "Sarah J. Maas", "current_page": 90, "total_pages": 500},
    {"title": "The Fault in Our Stars", "author": "John Green", "current_page": 55, "total_pages": 500},
]



@app.route('/')
def index():
    return render_template('dashboard.html', books=books)

@app.route('/add_book_form', methods=['GET', 'POST'])
def add_book_form():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        current_page = request.form['current_page']
        total_pages = request.form['total_pages']
        print(title, author, current_page, total_pages)
        books.append({
            'title':title,
            'author':author,
            'current_page':int(current_page),
            'total_pages':int(total_pages)
            })

        return redirect(url_for('index'))
    return render_template('add_book_form.html')



if __name__ == '__main__':
    app.run(debug=True)
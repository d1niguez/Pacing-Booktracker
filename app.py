from flask import Flask, render_template

app = Flask(__name__)

books = [
    {"title": "The Lovely Bones", "author": "Alice Sebold", "current_page": 49, "total_pages": 500},
    {"title": "A Court of Thorns and Roses", "author": "Sarah J. Maas", "current_page": 90, "total_pages": 500},
    {"title": "The Fault in Our Stars", "author": "John Green", "current_page": 55, "total_pages": 500},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "current_page": 55, "total_pages": 500},
]



@app.route('/')
def index():
    return render_template('dashboard.html',books=books)

if __name__ == '__main__':
    app.run(debug=True)
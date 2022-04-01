import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, request, render_template, url_for, redirect
import config
from loguru import logger

engine = create_engine(f"postgresql://{config.db_username}:{config.password}@localhost/{config.db_name}")  # postgresql://login:password@host/db
db = scoped_session(sessionmaker(bind=engine))
app = Flask(__name__)


def create_bd():
    db.execute("""CREATE TABLE books(
        ID SERIAL,
        name varchar(30),
        description Text
    );""")


    db.execute("""CREATE TABLE comments(
        ID INTEGER,
        email varchar(30),
        comment TEXT
    );""")

    db.commit()

def Insert_Book(title, description):
    db.execute(f"INSERT INTO books(name, description) VALUES ('{title}', '{description}')")
    db.commit()

    info = db.execute(f"SELECT * FROM books WHERE name = '{title}' AND description = '{description}'").fetchone()
    return info



def GetBooks():
    return db.execute("SELECT * FROM books").fetchall()


# (3, 'Roman Номер: 1', 'lorem ipusm i tak dalee')

@app.route("/")
def index():
    return render_template("index.html", elements=GetBooks())

@app.route("/add", methods=["POST", "GET"])
def AddBook():

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")

        book_id = Insert_Book(title, description)

        logger.success(book_id)

        return redirect(url_for('book', id=book_id[0]))


    elif request.method == "GET":
        return render_template("add_book.html")


@app.route("/comment", methods=["POST"])
def AddComment():
    email = request.form.get("email")
    description = request.form.get("description")
    ids = request.form.get("ids")
    logger.success(f"{ids} | {description} | {email}")
    db.execute(f"INSERT INTO comments(ID, email, comment) VALUES ({ids}, '{email}', '{description}')")
    db.commit()

    return redirect(url_for('book', id=ids))

@app.route("/book/<string:id>", methods=["GET"])
def book(id):

    book = db.execute(f"SELECT * FROM books WHERE ID = {id}").fetchone()
    if book is None:
        return "<h1>Error 404, КНИГА НЕ НАЙДЕНА</h1>"

    comments = db.execute(f"SELECT * FROM comments WHERE ID = {id}").fetchall()

    logger.error(db.execute("SELECT * FROM comments").fetchall())

    logger.debug(comments)

    return render_template("templates_book.html", title=book[1], description=book[2], id=book[0], elements=comments)

if __name__ == "__main__":
    app.run()
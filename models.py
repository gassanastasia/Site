from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titlename = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text(2500), nullable=True)
    avtor = db.Column(db.String(120))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"News(titlename='{self.titlename}', content='{self.content}', avtor='{self.avtor}')"
    
    def repr(self):
        return f'<News {self.title}>'
    
    @classmethod
    def newest_first(cls):
        return cls.query.order_by(cls.date.desc())
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    newss = db.relationship('News', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    newss = db.relationship('News', secondary='news_tag', backref='tags', lazy=True)

    def __repr__(self):
        return f'<Tag {self.name}>'

news_tag = db.Table('news_tag',
    db.Column('news_id', db.Integer, db.ForeignKey('news.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)
# class Artist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)

# class Album(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     year = db.Column(db.String(4), nullable=False)
#     artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
#     artist = db.relationship('Artist', backref=db.backref('albums', lazy=True))

# class Song(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     length = db.Column(db.String(4), nullable=False)
#     track_number = db.Column(db.Integer, nullable=False)
#     album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
#     album = db.relationship('Album', backref=db.backref('songs', lazy=True))
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, News, Category, Tag, db
import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'secret-key-goes-here'
# связываем приложение и экземпляр SQLAlchemy
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Login'

#Декоратор устанавливает маршрут для главной страницы нашего приложения,а метод def определяет, что будет отображаться на этой странице
@app.route('/about')
def About():
    return render_template('about.html')

#аутентификация 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    else:
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session["id"] = user.id
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        email = request.form['email']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already taken')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, role=role, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile')
def profile():
    now = datetime.datetime.now()
    if current_user.is_authenticated:
        role=current_user.role
        if now.hour >= 6 and now.hour < 12:
            greeting = 'Доброе утро, '
        elif now.hour >= 12 and now.hour < 16:
            greeting = 'Добрый день, '
        elif now.hour >= 16 and now.hour < 22:
            greeting = 'Добрый вечер, '
        else:
            greeting = 'Доброй ночи, '
        return render_template('profile.html', greeting=greeting, user=current_user, role=role)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        titlename = request.form['titlename']
        content = request.form['content']
        avtor = request.form['avtor']
        category_id = request.form['category']
        tag_ids = [int(tag_id) for tag_id in request.form.getlist('tags')]
        news = News(titlename=titlename, content=content, category_id=category_id, avtor=avtor, user_id=session['id'])
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            news.tags.append(tag)
        db.session.add(news)
        db.session.commit()
        flash('Запись создана', 'success')
        return redirect(url_for('news'))
    else:
        user_id = session["id"]
        user = User.query.filter_by(id=user_id).first()
        categories = Category.query.all()
        tags = Tag.query.all()
        return render_template('add.html', categories=categories, tags=tags, user = user)

@app.route('/news')
def news():
    user_id = session["id"]
    user = User.query.filter_by(id=user_id).first()
    newss = News.newest_first().all()
    return render_template('news.html', type = 'news',  newss=newss, user=user)

@app.route('/news/<int:news_id>')
def newss(news_id):
    user_id = session["id"]
    user = User.query.filter_by(id=user_id).first()
    news = News.query.get_or_404(news_id)
    return render_template('news.html', type = 'new', newss=[news], user=user)

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    newss = News.query.filter(News.category_id==category_id).order_by(News.date.desc()).all()
    return render_template('news.html', type = 'category', category=category, newss=newss)

@app.route('/tag/<int:tag_id>')
def tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    newss = News.query.filter(News.tags.any(id=tag_id)).order_by(News.date.desc()).all()
    return render_template('news.html',type = 'tag' , tag=tag, newss=newss)

@app.route('/edit_news/<int:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    news = News.query.get_or_404(news_id)
    if request.method == 'POST':
        news.title = request.form['title']
        news.content = request.form['content']
        news.category_id = request.form['category']
        tag_ids = [int(tag_id) for tag_id in request.form.getlist('tags')]
        news.tags = []
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            news.tags.append(tag)
        db.session.commit()
        flash('Запись обновлена!', 'success')
        return redirect(url_for('news'))
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('edit_news.html', news=news, categories=categories, tags=tags)

@app.route('/delete_news/<int:news_id>', methods=['GET', 'POST'])
def delete_news(news_id):
    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()
    flash('Запись удалена!', 'success')
    return redirect(url_for('news'))  

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
import os
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aT3J6yUWANPrwzm'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True  # Включено для SSL
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = None

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Проверь тут данные! Измени your_password на реальный пароль от mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://superpuperchelic:McpcjlsLYTQbkIa@localhost/BakeryDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app, supports_credentials=True, origins=["*"]) 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Admin(UserMixin, db.Model):
    __tablename__ = 'Admins'
    id = db.Column('Id', db.Integer, primary_key=True)
    username = db.Column('Username', db.String(50), unique=True)
    password_hash = db.Column('PasswordHash', db.String(255))

class Category(db.Model):
    __tablename__ = 'Categories'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'Products'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Weight = db.Column(db.String(50))
    Price = db.Column(db.Float)
    ImagePath = db.Column(db.String(1000))
    CategoryId = db.Column(db.Integer, db.ForeignKey('Categories.Id'))

class Promotion(db.Model):
    __tablename__ = 'Promotion'
    Id = db.Column(db.Integer, primary_key=True)
    ImageUrl = db.Column(db.String(1000))

class News(db.Model):
    __tablename__ = 'News'
    Id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255))
    ImageUrl = db.Column(db.String(1000))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect('/')

@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({"status": "authenticated", "user": current_user.username}), 200
    return jsonify({"status": "unauthorized"}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password): 
            login_user(admin)
            if request.is_json:
                return jsonify({"status": "ok"}), 200
            return redirect('/') 
        
        return jsonify({"error": "Неверный логин или пароль"}), 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- API ЭНДПОИНТЫ ---

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        "id": p.Id, "name": p.Name, "weight": p.Weight, "price": p.Price,
        "image": p.ImagePath, "category_id": p.CategoryId,
        "category_name": p.category.Name if p.category else "Без категории"
    } for p in products])

@app.route('/api/categories', methods=['GET'])
def get_categories():
    cats = Category.query.all()
    return jsonify([{"id": c.Id, "name": c.Name} for c in cats])

@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    promos = Promotion.query.all()
    return jsonify([{"id": p.Id, "image": p.ImageUrl} for p in promos])

@app.route('/api/news', methods=['GET'])
def get_news():
    news_list = News.query.all()
    return jsonify([{"id": n.Id, "title": n.Title, "image": n.ImageUrl} for n in news_list])

@app.route('/api/products', methods=['POST'])
def add_product():
    name = request.form.get('name')
    weight = request.form.get('weight')
    price = request.form.get('price')
    category_id = request.form.get('category_id')
    file = request.files.get('image')

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = f"/static/uploads/{filename}"
    else:
        image_url = ""

    try:
        new_product = Product(
            Name=name, Weight=weight, Price=float(price) if price else 0.0,
            CategoryId=int(category_id) if category_id else None, ImagePath=image_url
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Товар успешно добавлен!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ (ВЫНЕСЕНА ИЗ __main__) ---
with app.app_context():
    db.create_all()
    
    if not Category.query.first():
        categories_list = [
            "Все", "Сладкая выпечка", "Хлеб", "Десерты", "Пироги", "Торты",
            "Первые блюда", "Вторые блюда", "Гарниры", "Салаты", "Закуски",
            "Горячие напитки", "Холодные напитки"
        ]
        for cat_name in categories_list:
            db.session.add(Category(Name=cat_name))
        db.session.commit()

    if not Admin.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('admin123')
        db.session.add(Admin(username='admin', password_hash=hashed_pw))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

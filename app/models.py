from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.BigInteger, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=False)
    password_hash = db.Column(db.String(300))
    role = db.Column(db.String(20), default='store_owner')

    # One-to-many relation: user -> stores
    stores = db.relationship('Store', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    store_address = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    phone2 = db.Column(db.BigInteger)
    logo_filename = db.Column(db.String(200))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    store = db.relationship('Store', backref='products')
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    display_picture = db.Column(db.String(200))
    images = db.Column(db.ARRAY(db.String(200)))  # List of image filenames
    metal_type = db.Column(db.String(20))
    category = db.Column(db.String(20))
    metal_purity = db.Column(db.Integer)
    metal_quantity = db.Column(db.Float)
    jarti = db.Column(db.Float)
    jyala = db.Column(db.Float)
    status = db.Column(db.String(20), default='published')  # 'published' or 'hold'

class GoldSilverRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gold_price = db.Column(db.Numeric, nullable=False)
    silver_price = db.Column(db.Numeric, nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


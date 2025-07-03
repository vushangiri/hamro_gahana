import os
from flask import Flask
from .extensions import db, migrate
from flask_login import LoginManager




login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config['SECRET_KEY'] = 'Sydney@123'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import blueprints
    from .auth_routes import auth
    app.register_blueprint(auth)

    # Import routes
    from .routes import main
    app.register_blueprint(main)

    from .user_routes import user
    app.register_blueprint(user)

    from .admin_routes import admin
    app.register_blueprint(admin)

    from app.models import GoldSilverRate

    @app.context_processor
    def inject_rates():
        rate = GoldSilverRate.query.order_by(GoldSilverRate.updated_at.desc()).first()
        return dict(current_rate=rate)
    
    @app.context_processor
    def utility_processor():
        def compute_price(product, rates):
            if not product or not rates:
                return 0

            purity = float(product.metal_purity or 0)
            quantity = float(product.metal_quantity or 0)
            jarti_percent = float(product.jarti or 0)  # percentage of quantity
            jyala_fixed = float(product.jyala or 0)    # fixed amount
            gold_price = float(rates.gold_price or 0)
            silver_price = float(rates.silver_price or 0)

            # Adjust quantity with jarti%
            adjusted_quantity = quantity + (quantity * (jarti_percent / 100))

            if product.metal_type.lower() == "gold":
                metal_value = (purity / 24) * adjusted_quantity * gold_price
                return metal_value + jyala_fixed

            elif product.metal_type.lower() == "silver":
                metal_value = adjusted_quantity * silver_price
                return metal_value + jyala_fixed

            else:
                return 0


        return dict(compute_price=compute_price)


    return app

from .models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
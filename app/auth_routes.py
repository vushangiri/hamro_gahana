from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Store
from .forms import RegistrationForm, ForgotPasswordForm
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if phone exists
        if User.query.filter_by(phone=form.phone.data).first():
            flash('Phone number already registered.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            phone=form.phone.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.flush()  # Get user.id before commit

        # Handle logo upload
        logo_filename = None
        if form.store_logo.data:
            filename = secure_filename(form.store_logo.data.filename)
            form.store_logo.data.save('app/static/uploads/' + filename)
            logo_filename = filename

        store = Store(
            user_id=user.id,
            store_name=form.store_name.data,
            store_address=form.store_address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            phone2=form.phone2.data,
            logo_filename=logo_filename
        )
        db.session.add(store)
        db.session.commit()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = User.query.filter_by(phone=phone).first()
        if user and user.check_password(password):
            login_user(user)
            # flash('Logged in successfully.', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        phone = form.phone.data
        new_password = form.new_password.data

        user = User.query.filter_by(phone=phone).first()

        if not user:
            flash("No user found with that phone number.", "danger")
            return redirect(url_for('auth.forgot_password'))

        user.set_password(new_password)
        db.session.commit()

        flash("Password reset successfully. Please log in with your new password.", "success")
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', form=form)

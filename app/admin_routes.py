from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .models import db, Store, Product, GoldSilverRate, User
from .forms import RateForm, AdminProfileForm

admin = Blueprint('admin', __name__)

@admin.route('/admin/stores')
@login_required
def all_stores():
    if current_user.role != 'admin':
        abort(403)

    # stores = stores = Store.query.join(User).filter(User.role != "admin").all()
    # products = Product.query.all()
    page = request.args.get("page", 1, type=int)
    per_page = 10
    search = request.args.get("q", "", type=str)

    query = Store.query.join(User).filter(User.role != "admin")

    if search:
        query = query.filter(
            db.or_(
                Store.store_name.ilike(f"%{search}%"),
                Store.products.any(Product.name.ilike(f"%{search}%"))
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    stores = pagination.items

    return render_template("admin_stores.html", stores=stores, pagination=pagination, search=search, admin_stores=True)

@admin.route('/admin/change-status/<int:id>', methods=['POST'])
@login_required
def change_status(id):
    if current_user.role != 'admin':
        abort(403)

    product = Product.query.get_or_404(id)
    new_status = request.form['status']
    if new_status not in ['published', 'hold']:
        flash("Invalid status.", "danger")
        return redirect(url_for('admin.all_stores'))

    product.status = new_status
    db.session.commit()
    flash("Product status updated.", "success")
    return redirect(url_for('admin.all_stores'))

@admin.route('/admin/set-rates', methods=['GET', 'POST'])
@login_required
def set_rates():
    if current_user.role != 'admin':
        abort(403)

    # Get the latest rate record or create one
    rate = GoldSilverRate.query.first()
    if not rate:
        rate = GoldSilverRate(gold_price=0, silver_price=0)
        db.session.add(rate)
        db.session.commit()

    form = RateForm(obj=rate)

    if form.validate_on_submit():
        rate.gold_price = form.gold_price.data
        rate.silver_price = form.silver_price.data
        db.session.commit()
        flash("Rates updated successfully!", "success")
        return redirect(url_for('admin.set_rates'))

    return render_template('set_rates.html', form=form, rate=rate, set_rates=True)

@admin.route("/admin_profile", methods=["GET", "POST"])
@login_required
def admin_profile():
    if current_user.role != "admin":
        abort(403)

    form = AdminProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.phone = form.phone.data
        current_user.email = form.email.data

        if form.password.data:
            current_user.set_password(form.password.data)

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("admin.admin_profile"))

    return render_template("admin_profile.html", form=form, profile=True)

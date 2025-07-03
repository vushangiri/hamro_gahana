from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from .models import db, Store, Product, User
from werkzeug.utils import secure_filename
import os
from .forms import ProductForm, ProfileForm

user = Blueprint('user', __name__)

@user.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'store_owner':
        abort(403)

    stores = Store.query.filter_by(user_id=current_user.id).all()
    products = (
        Product.query
        .join(Store)
        .filter(Store.user_id == current_user.id)
        .all()
    )

    return render_template('dashboard.html', stores=stores, products=products, dashboard=True)

@user.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'store_owner':
        abort(403)

    form = ProductForm()

    if form.validate_on_submit():
        # Save display picture
        dp_file = form.display_picture.data
        dp_filename = secure_filename(dp_file.filename)
        dp_path = os.path.join(current_app.root_path, "static/uploads/products", dp_filename)
        dp_file.save(dp_path)

        # Save additional images
        image_filenames = []
        if form.images.data:
            for f in request.files.getlist("images"):
                if f.filename:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(current_app.root_path, "static/uploads/products", filename))
                    image_filenames.append(filename)

        # Get the first store (if multiple stores)
        store = Store.query.filter_by(user_id=current_user.id).first()
        if not store:
            flash("You don't have a store yet.", "danger")
            return redirect(url_for('user.dashboard'))

        product = Product(
            store_id=store.id,
            name=form.name.data,
            description=form.description.data,
            display_picture=dp_filename,
            images=image_filenames,
            metal_type=form.metal_type.data,
            metal_purity=form.metal_purity.data,
            metal_quantity=form.metal_quantity.data,
            jarti=form.jarti.data,
            jyala=form.jyala.data,
            status='published'  # Auto-publish
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for('user.dashboard'))

    return render_template('add_product.html', form=form)

@user.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if current_user.role != 'store_owner':
        abort(403)

    # Make sure the product belongs to the current user
    product = (
        Product.query
        .join(Store)
        .filter(
            Product.id == id,
            Store.user_id == current_user.id
        )
        .first()
    )
    if not product:
        flash("Product not found or not authorized.", "danger")
        return redirect(url_for('user.dashboard'))

    form = ProductForm(obj=product)

    if form.validate_on_submit():
        # Update fields
        product.name = form.name.data
        product.description = form.description.data
        product.metal_type = form.metal_type.data
        product.category = form.category.data
        product.metal_purity = form.metal_purity.data
        product.metal_quantity = form.metal_quantity.data
        product.jarti = form.jarti.data
        product.jyala = form.jyala.data

        # If new display picture uploaded
        if form.display_picture.data:
            dp_filename = secure_filename(form.display_picture.data.filename)
            form.display_picture.data.save(
                os.path.join(current_app.root_path, "static/uploads/products", dp_filename)
            )
            product.display_picture = dp_filename

        # If new additional images uploaded
        image_filenames = []
        if form.images.data:
            for f in request.files.getlist("images"):
                if f.filename:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(current_app.root_path, "static/uploads/products", filename))
                    image_filenames.append(filename)
            product.images = image_filenames

        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for('user.dashboard'))

    # Pre-populate form fields on GET
    return render_template('edit_product.html', form=form, product=product)


import os

@user.route('/product/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if current_user.role != 'store_owner':
        abort(403)

    product = (
        Product.query
        .join(Store)
        .filter(
            Product.id == id,
            Store.user_id == current_user.id
        )
        .first()
    )
    if not product:
        flash("Product not found or unauthorized.", "danger")
        return redirect(url_for('user.dashboard'))

    # Delete display picture
    dp_path = os.path.join(current_app.root_path, "static/uploads/products", product.display_picture)
    if os.path.exists(dp_path):
        os.remove(dp_path)

    # Delete additional images
    if product.images:
        for img in product.images:
            img_path = os.path.join(current_app.root_path, "static/uploads/products", img)
            if os.path.exists(img_path):
                os.remove(img_path)

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully.", "success")
    return redirect(url_for('user.dashboard'))

@user.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    # Load current user and their store
    if current_user.role != 'store_owner':
        abort(403)
    store = current_user.stores[0]  # assuming one store per user

    form = ProfileForm(
        phone=current_user.phone,
        email=current_user.email,
        store_name=store.store_name,
        store_address=store.store_address,
        latitude=store.latitude,
        longitude=store.longitude,
        phone2=store.phone2
    )

    if form.validate_on_submit():
        # Update user fields
        current_user.phone = form.phone.data
        current_user.email = form.email.data

        if form.password.data:
            current_user.set_password(form.password.data)

        # Update store fields
        store.store_name = form.store_name.data
        store.store_address = form.store_address.data
        store.latitude = form.latitude.data
        store.longitude = form.longitude.data
        store.phone2 = form.phone2.data

        # Handle logo upload
        if form.store_logo.data:
            filename = secure_filename(form.store_logo.data.filename)
            form.store_logo.data.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            store.logo_filename = filename

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("user.profile"))

    return render_template("profile.html", form=form, store=store, profile=True)

@user.route("/store/<int:store_id>")
def view_store(store_id):
    store = Store.query.get_or_404(store_id)
    search = request.args.get("q", "", type=str)
    
    products_query = Product.query.filter_by(store_id=store.id, status="published")

    if search:
        products_query = products_query.filter(Product.name.ilike(f"%{search}%"))
    
    products = products_query.all()

    return render_template(
        "store.html",
        store=store,
        products=products,
        search=search
    )


@user.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    back_url = request.args.get("next") or url_for("user.dashboard")
    return render_template("product_detail.html", product=product, back_url=back_url)

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .models import Product, GoldSilverRate, Store
import random
from flask_login import current_user
from sqlalchemy import or_, and_

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.all_stores'))
        return redirect(url_for('user.dashboard'))
    
    # Get all published products
    products = Product.query.filter_by(status="published").all()

    # Shuffle and pick 5 unique products
    if products:
        random.shuffle(products)
        # random_value = random.randint()
        featured_products = products[:5]
        popular_products = products[5:10]
    else:
        featured_products = []
        popular_products = []

    # Get current rates
    rates = GoldSilverRate.query.first()

    return render_template(
        "home.html",
        featured_products=featured_products,
        popular_products=popular_products,
        rates=rates,
        home=True
    )

@main.route('/explore')
def explore():
    args_dict = request.args.to_dict()

    # Filters
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    metal_type = request.args.get("metal_type", "").strip()
    page = request.args.get("page", 1, type=int)

    # Base query: only published products
    query = Product.query.join(Store).filter(Product.status == "published")

    # Apply search
    if search:
        like_term = f"%{search}%"
        query = query.filter(or_(
                Product.name.ilike(like_term),
                Store.store_name.ilike(like_term)
            )
        )

    # Apply category filter
    if category and category != "all":
        query = query.filter(Product.category == category)

    # Apply metal_type filter
    if metal_type and metal_type != "both":
        query = query.filter(Product.metal_type == metal_type)

    # Sort by most recent (you can adjust as needed)
    query = query.order_by(Product.id.desc())

    # Pagination
    per_page = 5
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    # Rates
    rates = GoldSilverRate.query.first()

    return render_template(
        "explore.html",
        products=products,
        pagination=pagination,
        rates=rates,
        explore=True,
        search=search,
        category=category,
        metal_type=metal_type
    )


# @main.route('/explore')
# def explore():
#     args_dict = request.args.to_dict()
   
#     # Get query params
#     search = request.args.get("search", "").strip()
#     category = request.args.get("category", "").strip()
#     metal_type = request.args.get("metal_type", "").strip()
#     min_purity = request.args.get("min_purity", type=int)
#     max_purity = request.args.get("max_purity", type=int)
#     min_quantity = request.args.get("min_quantity", type=float)
#     max_quantity = request.args.get("max_quantity", type=float)
#     page = request.args.get("page", 1, type=int)
#     lat = request.args.get("lat", type=float)
#     lng = request.args.get("lng", type=float)

#     # Base query: only published products
#     query = Product.query.join(Store).filter(Product.status == "published")

#      # Previous page link
#     if page > 1:
#         prev_args = args_dict.copy()
#         prev_args["page"] = page - 1
#         prev_url = url_for("main.explore", **prev_args)
#     else:
#         prev_url = None

    

#     # Filters
#     if category and category != 'all':
#         query = query.filter(Product.category == category)

#     if metal_type and metal_type != 'both':
#         query = query.filter(Product.metal_type == metal_type)

#     if min_purity is not None:
#         query = query.filter(Product.metal_purity >= min_purity)

#     if max_purity is not None:
#         query = query.filter(Product.metal_purity <= max_purity)

#     if min_quantity is not None:
#         query = query.filter(Product.metal_quantity >= min_quantity)

#     if max_quantity is not None:
#         query = query.filter(Product.metal_quantity <= max_quantity)

#     products = query.all()

#     # If location provided, sort by distance
#     if lat is not None and lng is not None:
#         def haversine(lat1, lon1, lat2, lon2):
#             from math import radians, cos, sin, asin, sqrt
#             R = 6371
#             dlat = radians(lat2 - lat1)
#             dlon = radians(lon2 - lon1)
#             a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
#             c = 2 * asin(sqrt(a))
#             return R * c

#         product_list = []
#         for p in products:
#             store = p.store
#             if store.latitude and store.longitude:
#                 distance = haversine(lat, lng, store.latitude, store.longitude)
#             else:
#                 distance = 99999  # Put unsorted ones last
#             product_list.append((p, distance))

#         # Sort by distance
#         product_list.sort(key=lambda x: x[1])
#         sorted_products = [p[0] for p in product_list]
#     else:
#         sorted_products = products

#     # Pagination
#     per_page = 5
#     total = len(sorted_products)
#     start = (page - 1) * per_page
#     end = start + per_page
#     paginated_products = sorted_products[start:end]
    

#     # Rates
#     rates = GoldSilverRate.query.first()

#     # Next page link
#     if end < total:
#         next_args = args_dict.copy()
#         next_args["page"] = page + 1
#         next_url = url_for("main.explore", **next_args)
#     else:
#         next_url = None

#     # Search
#     if search:
#         like_term = f"%{search}%"
#         query = query.filter(or_(
#             Product.name.ilike(like_term),
#             Store.store_name.ilike(like_term)
#         ))

#     return render_template(
#         "explore.html",
#         products=paginated_products,
#         total=total,
#         page=page,
#         per_page=per_page,
#         rates=rates,
#         explore=True,
#         search=search,
#         category=category,
#         metal_type=metal_type,
#         min_purity=min_purity,
#         max_purity=max_purity,
#         min_quantity=min_quantity,
#         max_quantity=max_quantity,
#         has_next = len(sorted_products) > end,
#         lat=lat,
#         lng=lng,
#         args=args_dict,
#         prev_url=prev_url,
#         next_url=next_url
#     )


@main.route('/api/nearby-stores')
def nearby_stores():
    try:
        user_lat = float(request.args.get('lat'))
        user_lng = float(request.args.get('lng'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid coordinates"}), 400

    # Get all stores
    stores = Store.query.all()

    # Calculate distance manually (simple approximation)
    def haversine(lat1, lon1, lat2, lon2):
        from math import radians, cos, sin, asin, sqrt
        R = 6371  # Earth radius in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    store_list = []
    for store in stores:
        if store.latitude and store.longitude:
            distance = haversine(user_lat, user_lng, store.latitude, store.longitude)
            store_list.append({
                "id": store.id,
                "store_name": store.store_name,
                "address": store.store_address,
                "phone": store.phone2,
                "logo": store.logo_filename,
                "distance": round(distance, 2)
            })

    # Sort by distance and take top 5
    store_list = sorted(store_list, key=lambda x: x["distance"])[:5]

    return jsonify(store_list)

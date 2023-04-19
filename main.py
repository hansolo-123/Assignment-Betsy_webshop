__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

import peewee
from models import *
from decimal import Decimal

db = peewee.SqliteDatabase('betsy_data.db')

run_main()
    

search_term = 'sweater'

def search(search_term):
    print("")
    print("query 1 result:")
    products = Products.select().where(peewee.fn.lower(Products.name).contains(search_term.lower()))
    for product in products:
        print(product.name)
    print("")

user_id = 1
user_name = 'John Hancock'

def list_user_products(user_id, user_name):
    print("query 2A result:")
    user = Users.get(Users.username == user_name)
    owned_products = Orders.select().join(Products).where(Orders.buyer == user)
    for product in owned_products:
        print(f"{user.username} owns: {product.item.name}")
    print("")
    print("query 2B result:")
    user = Users.get(Users.id == user_id)
    owned_products = Orders.select().join(Products).where(Orders.buyer == user)
    for product in owned_products:
        print(f"user id: {user.id} owns: {product.item.name}")

tag_id = 1
tag_name = "cool"

def list_products_per_tag(tag_id, tag_name):
    print("")

    print("query 3A result:")
    products = Products.get(Products.id == tag_id)
    selected_products = Products.select().where(Products.id == products)
    for product in selected_products:
        print(f"{product.name}")
        print("")

    print("query 3B result:")
    products = Products.get(Products.tag == tag_name)
    selected_products = Products.select().where(Products.tag.contains(tag_name))
    for product in selected_products:
        print(f"{product.name}: {product.description}")

user_id = 1
product = 'Pink socks'

def add_product_to_catalog(user_id, product):
    print("")
    print("query 4 result:")
    user = Users.get(Users.id == user_id)
    socks = Products(name=product, seller=user, tag='comfortable', description="A pair of comfortable socks", price=10, stock=50)
    socks.save()
    selected_products = Products.select().where(Products.seller == user_id)
    for products in selected_products:
        print(f"{products.seller.username} sells: {products.name}")

user_id = 1
products = 'Shoes'

def delete_product_from_catalog(user_id, products):
    print("")
    print("query 5 result:")
    user = Users.get(Users.id == user_id)
    product_id = Products.get(Products.name == products)
    product_name = product_id.name
    selected_product = Products.select(Products.id).where((Products.seller == user) & (Products.name == products)).scalar()
    delete_product = Products.delete().where(Products.id == selected_product)
    delete_row = delete_product.execute()
    print(f"Deleted {delete_row} {product_name} for {user.username}")
    all_products = Products.select().where(Products.seller == user_id)
    for products in all_products:
        print(f"{products.seller.username} sells: {products.name}")


product_ids = 4
new_quantity = 10

def update_stock(product_ids, new_quantity):
    print("")
    print("query 6 result:")
    product_id = Products.get(Products.id == product_ids)
    old_stock = product_id.stock
    product_id.stock = new_quantity
    product_id.save()
    print(f"updated {product_id.name} stock from {old_stock} to {new_quantity}")

products_id = 5
users_id = 3
quantity = 2

def purchase_product(products_id, users_id, quantity):
    print("")
    print("query 7 result:")
    user = Users.get(Users.id == users_id)
    user_name = user.username
    product = Products.get(Products.id == products_id)
    Orders.select().join(Products).where(Orders.buyer == user)
    product_name = product.name
    seller = product.seller.id
    product_quantity = product.stock

    # Add selected order
    decrement = Decimal('1')
    for i in range(quantity):
        order = Orders.create(buyer=user_id, item=products_id, seller=seller)
        order.save()

        product_quantity -= decrement

    product.stock = product_quantity
    product.save()

    # Load new selection of owned products
    owned_instances = Sold.select().where(Sold.buyer == user_name)
    for instance in owned_instances:
        products_list = [item for item in instance.products_id.split(', ') if item.strip()]
        try:
            for i in range(quantity):
                products_list.append(product_name)
        except ValueError:
            pass
        instance.products_id = ', '.join(products_list)
        with db.atomic():
            instance.save()
    print(f"user {user_name} purchased {quantity} {product_name}")

    # Update amounts of products owned for user
    for user_products in Sold.select(Sold.buyer, Sold.products):
        products_str = user_products.products_id
        product_list = products_str.split(", ")
        for i in range(quantity):
            Sold.update(amount=len(product_list)).where(
                (Sold.buyer == user_name) & (Sold.products == products_str)
            ).execute()
    

product_id = 2
user_id = 1

def remove_product(product_id, user_id):
# Remove selected order
    user = Users.get(Users.id == user_id)
    user_name = user.username
    product = Products.get(Products.id == product_id)
    product_name = product.name
    print("")
    subquery = (Orders
                .select(Orders.id)
                .where(Orders.buyer == user_id, Orders.item == product_id)
                .order_by(Orders.id)
                .limit(1))
    query1 = Orders.delete().where(Orders.id == subquery)
    deleted_rows1 = query1.execute()
    print('query 8 result:')
    print(f"Deleted {deleted_rows1} {product_name} for {user_name}")

    # Load new selection of owned products
    owned_instances = Sold.select().where(Sold.buyer == user_name)
    for instance in owned_instances:
        products_list = instance.products_id.split(', ')
        try:
            products_list.remove(product_name)
        except ValueError:
            pass
        instance.products_id = ', '.join(products_list)
    with db.atomic():
        for instance in owned_instances:
            instance.save()

    # Update amounts of products owned for user
    for user_products in Sold.select(Sold.buyer, Sold.products):
        products_str = user_products.products_id
        product_list = products_str.split(", ")
        Sold.update(amount=len(product_list)).where(
            (Sold.buyer == user_name) & (Sold.products == user_products.products_id)
        ).execute()
    owned_products = Orders.select().join(Products).where(Orders.buyer == user)
    amount_list = []
    for product in owned_products:
        amount_list.append(product.item.name)
    if (len(amount_list)) == 0:
        Sold.update(amount=0).where(Sold.buyer == user.username).execute()

search(search_term)
list_user_products(user_id, user_name)
list_products_per_tag(tag_id, tag_name)
add_product_to_catalog(user_id, product)
delete_product_from_catalog(user_id, products)
update_stock(product_ids, new_quantity)
purchase_product(products_id, users_id, quantity)
remove_product(product_id, user_id)
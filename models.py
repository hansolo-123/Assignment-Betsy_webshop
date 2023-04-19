from peewee import *
import os.path
import time

db = SqliteDatabase('betsy_data.db')

mock_userdata = (
            ('John Hancock', ['Schrijverskwartier 100, 1967JJ, Heemskerk','IBANNLAMR123456789']),
            ('Dave Harrison', ['Snelweg 91, 2000FF, Amsterdam', 'IBANNLABNA123456789']),
            ('Doeke Douwis', ['`t Pad 2, 1234AA, Hoofddorp', 'IBANNLRABO123456789']),
            ('Ed Eet', ['Kade 115, 1582BA, Rotterdam', 'IBANNLINGB123456789']),
            ('Sara Safari', ['Europastraat 108, 1582BA, Rotterdam', 'IBANNLAMRO123456789']), 
            ('Sandy Sandwich', ['Amadillushoevepad 1, 3050IO, Almere', 'IBANNLABNB123456789']), 
            )

mock_productdata =   (
            ('T-shirt', 'Sandy Sandwich', ['a worn out dirty white t-shirt',  1, 2]),
            ('Jeans', 'Doeke Douwis', ['a blue jeans made to be filthy', 5, 8]),
            ('Beautifull sweater', 'Doeke Douwis', ['an amazing gift for your amazing person', 5, 5]),
            ('Jacket', 'Dave Harrison', ['a jacket made of the skin of cool banana''s', 9, 3]),
            ('Baseball hat', 'Ed Eet', ['if you want to look savvy and avoid the sun', 4, 15]),
            ('Shoes', 'John Hancock', ['a pair of purple shoes with with gum underneath', 1, 2]),
            ('Ugly sweater', 'John Hancock', ['a perfect gift for your not so perfect person', 3, 1]),
            )

bought_products = (
            ('John Hancock', ['Jeans', 'Jeans', 'Baseball hat']),
            ('Dave Harrison', ['T-shirt']),
            ('Ed Eet', ['Shoes', 'Shoes']),
            ('Sara Safari', ['Jeans', 'Baseball hat']), 
            ('John Hancock', ['Jeans']),
            )

def validate_bank_account_number(bank_account):
    # Remove any non-numeric characters from the bank account number
    bank_account = ''.join(filter(str.isdigit, bank_account))

    # Check if the bank account number has the correct length (9 digits)
    if len(bank_account) != 9:
        return False

    # Calculate the checksum using the 11-proef algorithm
    checksum = 0
    for i, digit in enumerate(reversed(bank_account)):
        checksum += int(digit) * (i % 9 + 1)
    return checksum % 11 == 0

class BaseModel(Model):
    class Meta:
        database = db

class Users(BaseModel):
    username = TextField(unique=True, null=False)
    adress = TextField(null=False)
    bank_account = CharField(unique=True, null=False)

class Products(BaseModel):
    name = TextField(unique=True)
    seller = ForeignKeyField(Users, backref='seller')
    tag = TextField(unique=True, null=True)
    description = TextField()
    price = DecimalField(constraints=[Check('price >= 0')], auto_round=True, decimal_places=0)
    stock = DecimalField(constraints=[Check('stock >= 0')])

class Orders(BaseModel):
    buyer = ForeignKeyField(Users, backref='owner')
    item = ForeignKeyField(Products, backref='item')
    seller = ForeignKeyField(Users, backref='products')

class Sold(BaseModel):
    buyer = ForeignKeyField(Users, backref='owned')
    products = ForeignKeyField(Products, backref='item', null=True)
    amount = IntegerField([Check('amount >= 0')], default=0)

path = './betsy_data.db'
check_file = os.path.isfile(path)
if check_file == True:
    pass
else:
   def run_main():
        """
    Handling exceptions
        """
        try:
            Users.create_table()
        except OperationalError:
            print ("Users table already exists!")
        try:
            Products.create_table()
        except OperationalError:
            print ("Products table already exists!")
        try:
            Orders.create_table()
        except OperationalError:
            print ("Orders table already exists!")
        try:
            Sold.create_table()
        except OperationalError:
            print ("Owned table already exists!")
    
        # Create users
        for userdata in mock_userdata:
            username = userdata[0]
            adress = userdata[1][0]
            bank_account = userdata[1][1]
            if validate_bank_account_number(bank_account):
                user = Users.create(username=username, adress=adress, bank_account=bank_account)
            else:
                print(f"Error: {username}'s Bank account number is invalid")

        # Create products
        for productdata in mock_productdata:
            name = productdata[0]
            traders = productdata[1]
            description = productdata[2][0]
            price = productdata[2][1]
            stock = productdata[2][2]
            seller = Users.get(Users.username == traders)

            product = Products.create(name=name, seller=seller.id, description=description, price=price, stock=stock)


        unique_tags = set(['beautiful', 'comfortable', 'filthy', 'savvy', 'perfect', 'ugly', 'awesome', 'dirty', 'amazing', 'cool', 'purple'])

        for product in Products.select():
            words = product.description.split()
            tags = set(filter(lambda word: word in unique_tags, words))
            product.tag = ', '.join(tags)
            product.save()

        for buyerdata in bought_products:
            buyer_name = buyerdata[0]
            buyer = Users.get(Users.username == buyer_name)
            products = buyerdata[1]
            for product_name in products:
                product = Products.get(Products.name == product_name)
                Orders.create(buyer=buyer, item=product, seller=product.seller_id)


        # Making Owned table (a collection of owned products for all users)
        for user_data in mock_userdata:
            username = user_data[0]
            user = Users.get(Users.username == username)
            products = []
            for owned_data in bought_products:
                if owned_data[0] == username:
                    products += owned_data[1]
            products_str = ", ".join(products)
            Sold.create(buyer=user.username, products=products_str, amount=len(products))

        # Adjusting Product stock field for the items appointed to users
        for product in Orders.select().join(Products):
            product_stock = product.item.stock
            for item in Sold.select().where(Sold.products.contains(product.item.name)):
                product_stock -= 1
            product.item.stock = product_stock
            product.item.save()

        print(f"betsy_data.db created sucessfully")
        time.sleep(0.5)  # delay for 5 seconds
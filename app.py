
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import random

#CREATING DATABASE TABLES AND DATABASE ITSELF
from werkzeug.utils import secure_filename

db_location = os.getcwd() + '//db//store1.sqlite'
db_Connection = sqlite3.connect(db_location)


app = Flask(__name__)
app.secret_key='6476e8jfhddudjdhetyd'

# Function to create database table in sqlite
def create_DB():
    try:
        db_Connection.execute('CREATE TABLE IF NOT EXISTS Myusers (email varchar PRIMARY KEY,userpassword varchar,surname varchar,firstname varchar)')
    except sqlite3.Error as error:
        print(error)
    finally:
        db_Connection.close()


def show_products_on_the_index():
    try:
        with sqlite3.connect(db_location) as myconnect:
            cursor = myconnect.cursor()
            products = cursor.execute("select * from roof").fetchall()
            if products:
                return products
            else:
                flash("Store is Empty", "warning")
                return products
    except sqlite3.Error as error1:
        flash(str(error1), "danger")
    except Exception as error:
        flash(str(error), "danger")


@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/')
def home():
    #cart_count = 0
    #cart_count = get_cart_count()
    products_for_sale = show_products_on_the_index()
    return render_template('index.html', products = products_for_sale)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method =="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            with sqlite3.connect(db_location) as myconnect:
                cursor = myconnect.cursor()
                get_user = cursor.execute("select * from Myusers where email =? and userpassword =?",(email, password)).fetchone()
                if get_user:
                    session['user'] = email
                    flash("login is successful")
                    return redirect(url_for('home'))
                else:
                    flash("Wrong Email or password")
                    return render_template('login.html')
        except sqlite3.Error as error1:
            flash(f"LOGIN not successful: {error1}")
        except Exception as error:
            flash(str(error))
    return render_template('login.html')

@app.route('/signup', methods =["GET", "POST"])
def signup():
    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        surname = request.form.get("surname")
        firstname = request.form.get("firstname")

        try:
            with sqlite3.connect(db_location) as myconnect:
                cursor = myconnect.cursor()
                cursor.execute("insert into Myusers (email, userpassword, surname, firstname) values (?,?,?,?)",(email, password, surname, firstname))
                myconnect.commit()
                print("sign up successful")
                flash("Account Created successful", "info")
                return redirect(url_for('login'))
                # return render_template('signup.html')
        except sqlite3.Error as error1:
            print(f"sign up not successful: {error1}")
            flash(str(error1), "danger")
        except Exception as error:
            print(error)
            flash(str(error), "danger")
    return render_template('signup.html')




#Admin section for adding product

@app.route('/admin', methods =["GET", "POST"])
def admin():
    Pid = generate_Product_ID()
    products = get_products_from_DB()
    return render_template('admin.html', pid = Pid, products=products)

# FUNCTION TO GENERATE PRODUCT ID
def generate_Product_ID():
    pID = random.randint(00000, 99999)
    product_IDs = 'Roof' + str(pID)
    return product_IDs

# FUNCTION TO UPLOAD PRODUCT IMAGES AND DETAILS
@app.route('/add_product', methods=["POST"])
def add_product():
    pID = request.form.get('product_ID')
    Pname = request.form.get('product_name')
    Pprice = request.form.get('price')
    Pdetail = request.form.get('product_description')
    Pcat = request.form.get('Pcat')

# PROCESS PRODUCT IMAGES FOR IMAGE PROCESSING
    upload_product_img = request.files['product_img']
    filename = secure_filename(upload_product_img.filename)
    if filename == '':
        flash("Product Image not selected, please select product image", "danger")
        return redirect(url_for('admin'))


    if Pcat == 'None':
        flash("Please select Product Category Before sending to DB")
        return redirect(url_for('admin'))
    else:

        uploadedProductImage = upload_product_img

        try:
            with sqlite3.connect(db_location) as myconnect:
                cursor = myconnect.cursor()
                cursor.execute("insert into roof(product_id, product_name, product_price, product_details, category) values (?,?,?,?,?)",(pID, Pname, Pprice, Pdetail, Pcat))
                myconnect.commit()
                # Saving your image into the news image folder
                uploadedProductImage.save(os.path.join(app.config['ProductImagePath'], pID + '.png'))
                if uploadedProductImage:
                    flash("Product Uploaded successfully", "info")
                return redirect(url_for('admin'))
        except sqlite3.Error as error1:(
                flash(str(error1), "danger"))
        except Exception as error:
            flash(str(error), "danger")
    return redirect(url_for('admin'))



# FUNCTION TO GET PRODUCTS FROM THE DATABASE AND UPLOAD IT TO OUR ADMIN PAGE
def get_products_from_DB():
    try:
        with sqlite3.connect(db_location) as myconnect:
            cursor = myconnect.cursor()
            products = cursor.execute("select  * from roof").fetchall()
            if products:
                return products
            else:
                flash("Store is Empty", "warning")
                return products
    except sqlite3.Error as error1:
        flash(str(error1), "danger")
    except Exception as error:
        flash(str(error), "danger")


# FOR IMAGE PROCESS CONFIGURATION
app.config['ProductImagePath'] = 'static/product_imgs'


if __name__ == ('__main__'):
    create_DB()
    app.run(host='0.0.0.0', debug=True)
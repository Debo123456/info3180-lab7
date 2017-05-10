"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required
from image_getter import getUrls
from bs4 import BeautifulSoup
from send_email import send_email
import requests
import urlparse
from models import User, Item
from forms import LoginForm
import smtplib


###
# Routing for your application.
###

@app.route('/')
def home():
    #if current_user.is_authenticated():
    #    redirect(url_for('homepage'))
        
    """Render website's home page."""
    return render_template('home.html')

@app.route('/api/users/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_email = request.json['email']
        user_name = request.json['name']
        user_password = request.json['password']
        user_age = request.json['age']
        user_gender = request.json['gender']
        
        user = User.query.filter_by(name=user_name).first()
        if user is not None:
            flash('Please select another name', 'danger')
            return redirect(url_for('home'))
                
        user = User.query.filter_by(email=user_email).first()
        if user is not None:
            flash('There is already an account for this email', 'danger')
            return redirect(url_for('home'))
        
        user = User(user_name, user_email, user_age, user_gender, user_password)
        db.session.add(user)
        db.session.commit()
        flash('User registered!', 'success')
        
        user = {
                "error": None,
                "data": {        
                    "user": {
                        "id": user.get_id(), 
                        "name": user_name,
                        "email": user_email,
                        "age": user_age,
                        "gender": user_gender,
                        }
                    },
                "message": "Success"
                }

        return jsonify(user=user), 200 
    return render_template('register.html')
    
@app.route('/api/users/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email, password=password).first()
        if user is not None:
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('homepage'));
        else:
            flash('Email or Password is incorrect.', 'danger')
            
    return render_template('login.html',form=form)
    
    
@app.route('/wishlist')
@login_required
def homepage():
    return render_template('wishlist.html', user = current_user)
    
@app.route('/get-thumbnail', methods=["GET", "POST"])
@login_required
def getThumbnail():
    url = request.json['url']
    return jsonify(getUrls(url)), 200
    
@app.route('/additem')
@login_required
def addItem():
    return render_template('add_item.html', user = current_user)

@app.route('/api/users/<int:id>/wishlist', methods=["GET", "POST"])
@login_required
def wishlist(id):
    if request.method == "GET":
        itemlist = []
        items = Item.query.filter_by(user_id = current_user.id).all()
        for item in items:
            i = {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "url": item.url,
                "thumbnail_url": item.thumbnail_url,
                "user_id": id
                }
            itemlist.append(i)
    
        return jsonify(items=itemlist), 200
        
    elif request.method == "POST":
        item_title = request.json['title']
        item_description = request.json['description']
        item_url = request.json['url']
        item_thumbnail = request.json['thumbnail_url']
        
        item = Item(item_title, item_description, item_url, item_thumbnail, current_user.id)
        db.session.add(item)
        db.session.commit()
        flash('Item added!', 'success')
        
        items = {
                 "error": None,
                 "data": {
                    "item": {
                        "id": item.get_id(),
                        "title": item_title,
                        "description": item_description,
                        "url": item_url,
                        "thumbnail_url": item_thumbnail
                        }
                    },
                "message": "Success"
                }
        return jsonify(items=items), 201
    return render_template('wishlist.html')
        
@app.route('/api/thumbnails', methods=['GET'])
@login_required
def thumbnails():
    if request.method == "GET":
        images = getUrls()
        if not images:
            results = {
                "error" : True,
                "message" : "fail",
                "thumbnails" : []
            }
        else:
             results = {
                "error" : None,
                "message" : "success",
                "thumbnails" : getUrls()
            }
        return jsonify(results)
    return render_template('wishlist.html')
    
@app.route('/api/users/<int:user_id>/wishlist/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(user_id, item_id):
    if request.method == "DELETE":
        item = Item.query.filter_by(id=item_id).first_or_404()
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted', 'success')
    
        return jsonify(result=True)
    return render_template('wishlist.html')
    
@app.route('/api/users/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'danger')
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
    
###
# The functions below should be applicable to all Flask apps.
###

#Tweak for shaing section in part2
@app.route("/share/", methods=['GET','POST'])
@login_required
def share():
    if request.method == "POST":
        to_name = request.form['name']  
        to_email = request.form['email']
        subject = "Check out my wishlist!"
        mylink = ""
        msg = "{}".format(mylink) #format to sent link to current user wishlist
        
        send_email(to_name, to_email, subject, msg)
        
        if send_email(to_name, to_email, subject, msg):
            flash('Sent!!!')
            return redirect(url_for('homepage'))
        else:
            flash('Email was not sent')
            return redirect(url_for('homepage'))
    return render_template("share.html")

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to tell the browser not to cache the rendered page.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")

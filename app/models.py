from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    password = db.Column(db.String(80))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % (self.name)
        
    def __init__(self, name, email, age, gender, password):
        self.name = name
        self.email = email
        self.age = age
        self.gender = gender
        self.password = password
        
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(80))
    url = db.Column(db.String(255))
    thumbnail_url = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<Item %r>' % (self.title)
        
    def __init__(self, title, description, url, thumbnail_url,user_id):
        self.title = title
        self.description = description
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.user_id = user_id

# class Share(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


#     def get_id(self):
#         try:
#             return unicode(self.id)
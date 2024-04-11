from flask import Flask,render_template,request,redirect, url_for,session,flash,jsonify
from flask_pymongo import PyMongo
import  base64
from bson.objectid import ObjectId

app=Flask(__name__)

app.secret_key = 'rakeshguptakatakam'
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/sign-up')
def signuppage():
    return render_template('signup.html')

@app.route('/log-in')
def loginpage():
    return render_template('login.html')

@app.route('/logging-in',methods=['POST'])
def logging():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user = mongo.db.users.find_one({'username': username})
        # item = mongo.db.items.find({'username': username}, {'item_image': 1})
        # encoded_images = []
        # for item_image in item:
        #     encoded_image = base64.b64encode(item_image['item_image']).decode('utf-8')
        #     encoded_images.append(encoded_image)
        # items = mongo.db.items.find({'username': username})
        # l=len(encoded_images)
        if not user:
            return render_template('login.html',message="User not found")
        else:
             if user['password'] == password:
                session['username'] = username
                # profile_img = base64.b64encode(user['profile-img']).decode('utf-8')
                # return render_template('/profile.html',user=user,profile_img=profile_img,message='logged in successfully',encoded_images=encoded_images,items=items,l=l)
                return redirect(url_for('showProfile',message="Logged in successfully"))
             else:
                 return render_template('login.html',message="Invalid Credentials")
             
@app.route('/profile')
def showProfile():
    username=session.get('username')
    user = mongo.db.users.find_one({'username': username})
    item = mongo.db.items.find({'username': username}, {'item_image': 1})
    encoded_images = []
    message=request.args.get('message')
    items = mongo.db.items.find({'username': username})
    for item_image in item:
        encoded_image = base64.b64encode(item_image['item_image']).decode('utf-8')
        encoded_images.append(encoded_image)
    l=len(encoded_images)
    profile_img = base64.b64encode(user['profile-img']).decode('utf-8')
    return render_template('/profile.html',user=user,profile_img=profile_img,message=message,encoded_images=encoded_images,items=items,l=l)
    
@app.route('/signup', methods= ['POST'])
def signup():
    if request.method == 'POST':
        name=request.form['name']
        username = request.form['username']
        mobile=request.form['mobile']
        password = request.form['password']
        image = request.files['profile-img']
        imagedata=image.read()
        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user:
            return 'Username already exists!'

        new_user = {'username': username, 'password': password,'profile-img':imagedata,'mobile':mobile,'name':name}
        mongo.db.users.insert_one(new_user)
        
    
    return render_template('login.html')


@app.route('/add')
def add():
    return render_template('additem.html')
@app.route('/logout')
def logout():
    session.pop('username', None) 
 
    return redirect(url_for('loginpage'))
@app.route('/check')
def check():
    if 'username' in session:
        username = session['username']
        return f"The username '{username}' is stored in the session."
    else:
        return "No username stored in the session."
    
@app.route('/home')
def home():
    item_imgs=mongo.db.items.find({},{'item_image':1})
    items=mongo.db.items.find()
    item_mob=mongo.db.items.find()
    mobile=[]
    for item in item_mob:
        username = item['username']
        user = mongo.db.users.find_one({'username': username})
        mobile_number = user.get('mobile')  
        mobile.append(mobile_number)
    encoded_images=[]
    for img in item_imgs:
        encoded_image = base64.b64encode(img['item_image']).decode('utf-8')
        encoded_images.append(encoded_image)
    l=len(encoded_images)
    return render_template('home.html',encoded_images=encoded_images,l=l,items=items,mobile=mobile)

@app.route('/addingitem', methods= ['POST'])
def  addingitem():
    if request.method=='POST':
        itemname=request.form['item_name']
        itemcost=request.form['item_cost']
        itemimg=request.files['item_image']
        imgdata=itemimg.read()
        username = session.get('username')
        if username:
            new_item = {
                'username': username,
                'item_name': itemname,
                'item_cost': itemcost,
                'item_image': imgdata  
            }
            
            mongo.db.items.insert_one(new_item)            
            return redirect(url_for('showProfile' ,message="Item added successfully"))
        else:
            return 'User not logged in. Please log in to add items.'
@app.route('/delete-item/<item_id>', methods=['POST'])
def delete_item(item_id):
        mongo.db.items.delete_one({'_id': ObjectId(item_id)})
        return redirect(url_for('showProfile'))        

# @app.route('/profile')
# def profile():
#     username=session.get('username')
#     user = mongo.db.users.find_one({'username': username})
#     item = mongo.db.items.find({'username': username}, {'item_image': 1})
#     encoded_images = []
#     for item_image in item:
#         encoded_image = base64.b64encode(item_image['item_image']).decode('utf-8')
#         encoded_images.append(encoded_image)
#     profile_img = base64.b64encode(user['profile-img']).decode('utf-8')
#     return render_template('/profile.html',user=user,profile_img=profile_img,message='item added successfully',encoded_images=encoded_images)

if __name__ == '__main__':
    app.run(debug=True)
# A simple blog backend built using Quart (Python async framework) and MySQL. 
# Features include user authentication, password hashing, session management, and CRUD operations for blog posts.

from quart import Quart,jsonify,request,session
import mysql.connector
import bcrypt



app=Quart(__name__)
app.secret_key="secret123"


db=mysql.connector.connect(
   host="localhost",
   user="root",
   password="root",
   database="blogdb"
   
)

cursor=db.cursor()

#register 
@app.route('/register',methods=["POST"])
async def register():

    data=await request.get_json()

    username=data.get("username")
    password=data.get("password")

    hashed=bcrypt.hashpw(password.encode(),bcrypt.gensalt())

    sql="insert into users (username,password) values(%s,%s)"
    cursor.execute(sql,(username,hashed))
    db.commit()
    return jsonify({"message ":"successfully registered"})

#login
@app.route('/login',methods=["POST"])
async def login():

    data=await request.get_json()

    username=data.get("username")
    password=data.get("password")

    cursor.execute("select * from users where username=%s",(username,))
    user=cursor.fetchone()

    if user:
        if bcrypt.checkpw(password.encode(),user[2].encode()):
            session["username"]=username
            return jsonify({"message":"user login successfully"})
        else:
            return jsonify({"message":"password incorrect"})
    else:
        return jsonify({"message":"user not found"})

#create a post
@app.route('/post',methods=["POST"])
async def post():
    if "username" not in session:
        return jsonify({"error":"login required"})
    
    data=await request.get_json()

    title = data.get("title")
    content   = data.get("content")
    author = session["username"]

    sql="insert into posts (title,content,author) values(%s,%s,%s)"
    cursor.execute(sql,(title,content,author))
    db.commit()
    return jsonify({"message":"post successfully"})

#get post 
@app.route('/post',methods=["GET"])
async def get():
    cursor.execute("select * from posts")
    posts=cursor.fetchall()
    return jsonify(posts)


#update post
@app.route('/post/<int:id>',methods=["PUT"])
async def update_post(id):

    if "username" not in session:
        return jsonify({"error":"login required"})

    data=await request.get_json()
    
    title=data.get("title")
    content=data.get("content")

    sql="select author from posts where id=%s"
    cursor.execute(sql,(id,))
    post=cursor.fetchone()

    if post[0]!=session["username"]:
        return jsonify({"error":"not allowed"})
    
    
    sql="update posts set title=%s , content=%s where id=%s"
    cursor.execute(sql,(title,content,id))
    db.commit()
    return jsonify({"message":"updated successfully"})

#delete post
@app.route('/post/<int:id>',methods=["DELETE"])
async def delete_post(id):
    if "username" not in session:
        return jsonify({"message":"login required"})
    
    sql="select author from posts where id=%s"
    cursor.execute(sql,(id,))
    post=cursor.fetchone()

    if not post:
        return jsonify({"message":"post not found"})


    if post[0]!=session["username"]:
        return jsonify({"error":"not allowed"})

    sql="delete from posts where id=%s"
    cursor.execute(sql,(id,))
    db.commit()
    return jsonify({"message":"post deleted"})

#logout
@app.route('/logout')
async def logout():
    session.pop("username",None)
    return jsonify({"message":"user logout"})




if __name__=="__main__":

    app.run(debug=True)



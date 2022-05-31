from app import app, mongo
from flask import jsonify, request, make_response
import jwt
from functools import wraps
from datetime import datetime, timedelta
from bson import json_util
from bson.objectid import  ObjectId
import json
from werkzeug.security import generate_password_hash, check_password_hash

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        # return 401 if token is not passed
        if not token:
            return make_response(jsonify({'message' : 'Token is missing !!'}), 401)

        try:
            # decoding the payload to fetch the stored details
            current_user = jwt.decode(token, 'secret', algorithms=["HS256"])
        except Exception as e:
            print(e)
            return make_response(jsonify({
                'message' : 'Token is invalid !!'
            }), 401)
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return wrap

@app.route('/register', methods=['POST'])
def register():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    password = generate_password_hash(request.json['password'])
    # check if the user exits
    db_user = mongo.db.user.find_one({'email':email})
    if db_user:
        return make_response(jsonify({
        "status":"success",
        "message":"user exists",
        "data":json.loads(json_util.dumps(db_user))
    }), 200)

    # insert the data into the database
    mongo.db.user.insert_one({'first_name':first_name, 'last_name':last_name,'email':email,'password':password})
    user = mongo.db.user.find_one({'first_name':first_name})
    return make_response(jsonify({
        "status":"success",
        "message":"added successfully",
        "data":json.loads(json_util.dumps(user))
    }), 201)

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    user = mongo.db.user.find_one({'email':email})
    if user == None:
        return make_response(jsonify({
            "status":"failed",
            "message":"no user found",
        }), 404)

    if(check_password_hash(user['password'], password)):
        token = jwt.encode({"_id":str(user['_id'])}, 'secret', algorithm="HS256")
        return make_response(jsonify({
            "status":"success",
            "message":"login successful",
            "data":json.loads(json_util.dumps(user)),
            "token":token
        }), 200)
    return make_response(jsonify({
        "status":"failed",
        "message":"incorrect password",
    }), 400)

@app.route('/template', methods=['POST'])
@login_required
def create_template(current_user):
    template_name = request.json['template_name']
    subject = request.json['subject']
    body = request.json['body']
    print(current_user)
    # insert the data to the database
    mongo.db.template.insert_one({"template_name":template_name,"subject":subject,"body":body, "user_id":current_user['_id']})
    template = mongo.db.template.find_one({'template_name':template_name})
    return make_response(jsonify({
        "status":"success",
        "message":"created successfully",
        "data":json.loads(json_util.dumps(template)),
    }), 201)

@app.route('/template', methods=['GET'])
@login_required
def get_all_templates(current_user):
    user_templates = mongo.db.template.find({'user_id':current_user['_id']})
    return make_response(jsonify({
        "status":"success",
        "message":"retrieved successfully",
        "data":json.loads(json_util.dumps(user_templates)),
    }), 200)

@app.route('/template/<template_id>', methods=['GET'])
@login_required
def get_template(current_user, template_id):
    template = mongo.db.template.find_one({'_id':ObjectId(template_id),'user_id':str(current_user['_id'])})
    return make_response(jsonify({
        "status":"success",
        "message":"retrieved successfully",
        "data":json.loads(json_util.dumps(template)),
    }), 200)

@app.route('/template/<template_id>', methods=['PUT'])
@login_required
def update_template(current_user, template_id):

    template_name = request.json['template_name']
    subject = request.json['subject']
    body = request.json['body']

    db_template = mongo.db.template.find_one({'_id':ObjectId(template_id),'user_id':str(current_user['_id'])})

    if template_name == "":
        template_name = db_template['template_name']
    else:
        template_name = template_name
        
    if subject == "":
        subject = db_template['subject']
    else:
        subject = subject

    if body == "":
        body = db_template['body']
    else:
        body = body


    mongo.db.template.find_one_and_update({'_id':ObjectId(template_id)}, {"$set": {"template_name":template_name,"subject":subject,"body":body} })
    updated_template = mongo.db.template.find_one({"_id":ObjectId(template_id)})
    return make_response(jsonify({
        "status":"success",
        "message":"updated successfully",
        "data":json.loads(json_util.dumps(updated_template)),
    }), 200)

@app.route('/template/<template_id>', methods=['DELETE'])
@login_required
def delete_template(current_user, template_id):
    mongo.db.template.find_one_and_delete({'_id':ObjectId(template_id),'user_id':str(current_user['_id'])})
    return make_response(jsonify({
        "status":"success",
        "message":"deleted successfully",
    }), 200)

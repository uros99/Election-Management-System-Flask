from flask import Flask, request, Response, make_response,jsonify;
from configuration import Configuration;
from models import database, User, UserRole, Role;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from adminDecorator import roleCheck;
import re;

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

application = Flask( __name__ );
application.config.from_object(Configuration)


def checkJMBG(param):
    if(len (param) != 13):
        return False;

    if(int(param[0:2]) > 31 or  int(param[0:2]) < 1):
        return False;

    if(int(param[2:4]) > 12 or int(param[2:4]) < 1):
        return False;

    if(int(param[4:7]) > 999 or int(param[4:7]) < 0):
        return False;

    if (int(param[7:9]) < 70 or int(param[7:9]) > 99):
        return False;

    if (int(param[9:12]) > 999 or int(param[9:12]) < 0):
        return False;

    k = 11 - ((7*(int(param[0])+int(param[6])) + 6*(int(param[1])+int(param[7])) + 5*(int(param[2])+int(param[8])) + 4*(int(param[3])+int(param[9])) + 3*(int(param[4])+int(param[10])) + 2*(int(param[5])+int(param[11]))) % 11);
    if(k != int(param[12])):
        return False;

    return True;


def checkEmail(email):
    # pass the regular expression
    # and the string into the fullmatch() method
    if (re.fullmatch(regex, email)):
        return True;

    else:
        return False;

def checkPassword(param):
    if( len(param)<8 ):
        return False;

    number = False;
    upperCase = False;
    lowerCase = False;

    for element in param:
        if(element.isnumeric()):
            number = True;
        elif(element.islower()):
            lowerCase = True;
        elif(element.isupper()):
            upperCase = True;

    if(number==False or upperCase==False or lowerCase==False):
        return False;

    return True;


@application.route("/register", methods=["POST"])
def register():
    inputs = {}
    inputs["jmbg"] = request.json.get("jmbg", "");
    inputs["forename"] = request.json.get("forename", "");
    inputs["surname"] = request.json.get("surname", "");
    inputs["email"] = request.json.get("email", "");
    inputs["password"] = request.json.get("password", "");

    required = [value for value in inputs if len( inputs[value] ) == 0];
    for value in required:
        return make_response(jsonify(message="Field " + value + " is missing."), 400);

    if(checkJMBG(inputs["jmbg"]) == False):
        return make_response(jsonify(message="Invalid jmbg."), 400);

    result = checkEmail(inputs["email"])
    if(not result):
        return make_response(jsonify(message="Invalid email."), 400);

    if(checkPassword(inputs["password"])==False):
        return make_response(jsonify(message="Invalid password."), 400);

    users = User.query.all();
    for user in users:
        if(user.email==inputs["email"]):
            return make_response(jsonify(message="Email already exists."), 400);

    user = User(email = inputs["email"], password=inputs["password"], forename=inputs["forename"], lastname=inputs["surname"], jmbg=inputs["jmbg"]);
    database.session.add( user );
    database.session.commit();

    # roleId = Role.query.filter(Role.role == "user").first();

    userRole = UserRole(userId=user.id, roleId=2);
    database.session.add( userRole );
    database.session.commit();

    return Response (status=200);

jwt = JWTManager( application);


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    if ( len(email)==0 ):
        return make_response(jsonify(message="Field email is missing."), 400);
    if( len(password)==0 ):
        return make_response(jsonify(message="Field password is missing."), 400);

    result = checkEmail(email)
    if (not result):
        return make_response(jsonify(message="Invalid email."), 400);

    user = User.query.filter(and_(User.email == email, User.password == password)).first();
    if(not user):
        return make_response(jsonify(message="Invalid credentials."), 400);

    additionalClaims = {
        "jmbg": user.jmbg,
        "forename" : user.forename,
        "surname" : user.lastname,
        "roles" : [ str(role) for role in user.roles ]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims);

    return jsonify(accessToken = accessToken, refreshToken=refreshToken);

@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid"

@application.route("/refresh", methods=["POST"])
@jwt_required( refresh=True )
def refresh():
    identity = get_jwt_identity();
    refreshClaims = get_jwt();
    additionalClaims = {
        "jmbg": refreshClaims["jmbg"],
        "forename" : refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"]
    }
    accessToken = create_access_token(identity=identity, additional_claims=additionalClaims);
    return make_response(jsonify(accessToken=accessToken), 200);

@application.route("/delete", methods=["POST"])
@roleCheck(role="admin")
def delete():
    email = request.json.get("email", "");
    if(len(email)==0):
        return make_response(jsonify(message="Field email is missing."), 400);

    result = checkEmail(email)
    if (not result):
        return make_response(jsonify(message="Invalid email."), 400);

    user = User.query.filter(User.email == email).first();
    if(not user):
        return make_response(jsonify(message="Unknown user."), 400);

    database.session.delete(user);
    database.session.commit();
    return Response(status=200);

if( __name__ == "__main__"):
    database.init_app( application )
    application.run( debug=True, host="0.0.0.0", port= 5002)
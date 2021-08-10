from flask import Flask, request, Response, make_response,jsonify;
from configuration import Configuration;
from models import database, User, UserRole;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from applications.admin.adminDecorator import roleCheck;

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
    returnMessage = {
        "message": ""
    }
    inputs = {}
    inputs["email"] = request.json.get("email", "");
    inputs["password"] = request.json.get("password", "");
    inputs["forename"] = request.json.get("forename", "");
    inputs["surname"] = request.json.get("surname", "");
    inputs["jmbg"] = request.json.get("jmbg", "");

    required = [value for value in inputs if len( inputs[value] ) == 0];
    for value in required:
        returnMessage["message"] += "Field " + value + " is required";

    if(checkJMBG(inputs["jmbg"]) == False):
        returnMessage["message"] += "Invalid jmbg";

    result = parseaddr(inputs["email"])
    if( len( result[1]) == 0 ):
        returnMessage["message"] += "Invalid email";

    if(checkPassword(inputs["password"])==False):
        returnMessage["message"] += "Invalid password";

    if( len( returnMessage["message"] ) > 0):
        return make_response(jsonify(returnMessage), 400);

    user = User(email = inputs["email"], password=inputs["password"], forename=inputs["forename"], lastname=inputs["surname"], jmbg=inputs["jmbg"]);
    database.session.add( user );
    database.session.commit();

    userRole = UserRole(userId=user.id, roleId=2);
    database.session.add( userRole );
    database.session.commit();

    return Response ( "Successful registration!", status=200);

jwt = JWTManager( application);


@application.route("/login", methods=["POST"])
def login():
    returnMessage = {
        "message": ""
    }
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    if ( len(email)==0 ):
        returnMessage["message"] = "Field email is missing"
    if( len(password)==0 ):
        returnMessage["message"] = "Field password is missing"

    result = parseaddr(email)
    if (len(result[1]) == 0):
        returnMessage["message"] += "Invalid email";

    user = User.query.filter(and_(User.email == email, User.password == password)).first();
    if(not user):
        returnMessage["message"] = "Incorrect credentials"

    if (len(returnMessage["message"]) > 0):
        return make_response(jsonify(returnMessage), 400);

    additionalClaims = {
        "forename" : user.forename,
        "surname" : user.lastname,
        "jmbg" : user.jmbg,
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
        "forename" : refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"]
    }
    accessToken = create_access_token(identity=identity, additional_claims=additionalClaims);
    return make_response(jsonify(accessToken=accessToken), 200);

@application.route("/delete", methods=["POST"])
@roleCheck(role="(Admin)")
def delete():
    email = request.json.get("email", "");
    if(len(email)==0):
        return Response(jsonify(message="Email field is required"), status=400);

    result = parseaddr(email)
    if (len(result[1]) == 0):
        return Response(jsonify(message="Invalid email",status=400));

    user = User.query.filter(User.email == email).first();
    if(not user):
        return Response(jsonify(message="User does not exists"), status=400);

    database.session.delete(user);
    database.session.commit();
    return Response("Successful deleted user!", status=200);

if( __name__ == "__main__"):
    database.init_app( application )
    application.run( debug=True, port= 5002)
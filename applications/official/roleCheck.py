from functools import wraps;
from flask_jwt_extended import verify_jwt_in_request, get_jwt;
from flask import Response, make_response, jsonify;

def roleCheck(role):
    def innerRoleCheck(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request();
            claims = get_jwt();
            if(("roles" in claims) and (role in claims["roles"])):
                return function(*arguments, **keywordArguments);
            else:
                return make_response(jsonify({"msg": "Missing Authorization Header"}), 401)
        return decorator;
    return innerRoleCheck;


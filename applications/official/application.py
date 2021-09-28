from flask import Flask, request, Response, jsonify, make_response;
from roleCheck import roleCheck
from configuration import Configuration;
from flask_jwt_extended import JWTManager, get_jwt;
from models import database;
from redis import Redis;
import io;
import csv;

application = Flask( __name__ );
application.config.from_object(Configuration);

jwt = JWTManager(application);

@application.route("/vote", methods=["POST"])
@roleCheck(role="user")
def vote():
    if(len ( request.files ) == 0):
        return make_response(jsonify(message="Field file is missing."), 400);
    content = request.files["file"].stream.read().decode("utf-8");


    stream = io.StringIO(content);
    reader = csv.reader(stream);
    claims = get_jwt();
    jmbg = claims["jmbg"];

    with Redis (host= Configuration.REDIS_HOST) as redis:
        redis.rpush(Configuration.REDIS_VOTE_LIST, jmbg);
        line = 0;
        for row in reader:
            if(len (row) < 2):
                return make_response(jsonify(message="Incorrect number of values on line "+str(line) + "."), 400);
            else:
                GUID = row[0];
                pollNumber = row[1];
                if(not pollNumber.isnumeric() or (pollNumber.isnumeric() and int(pollNumber) <= 0 )):
                    return make_response(jsonify(message="Incorrect poll number on line "+str(line) + "."), 400);
                else:
                    redis.rpush(Configuration.REDIS_VOTE_LIST, GUID);
                    redis.rpush(Configuration.REDIS_VOTE_LIST, pollNumber);
                    line+=1;

        return Response(status=200);


if( __name__ == "__main__"):
    database.init_app( application )
    application.run( debug=True,host="0.0.0.0", port= 5004)
from flask import Flask, request, make_response, jsonify
from flask_jwt_extended import JWTManager

from configuration import Configuration
from models import database, Participant

application = Flask( __name__ );
application.config.from_object(Configuration);

jwt = JWTManager(application);

@application.route("/getParticipantById", methods=["GET"])
def findParticipantById():
    id = request.args.get("id");
    participant = Participant.query.filter(Participant.id == id);
    if(participant):
        chosenOne = {
            "id" : participant.id,
            "firstName" : participant.name
        }
        return make_response(jsonify(participant=chosenOne), 200);
    return make_response(400);

if( __name__ == "__main__"):
    database.init_app( application )
    application.run( debug=True, host="0.0.0.0", port= 5005)
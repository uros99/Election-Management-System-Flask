from flask import Blueprint
from applications.models import Participant

participantBlueprint = Blueprint ( "role" , __name__);

@participantBlueprint.route( "/", methods=["GET"])
def participants():
    return str( Participant.query.all() )
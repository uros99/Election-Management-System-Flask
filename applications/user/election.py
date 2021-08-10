from flask import Blueprint
from applications.models import Election

electionBlueprint = Blueprint ( "user" , __name__);

@electionBlueprint.route( "/", methods=["GET"])
def elections():
    return str( Election.query.all() )
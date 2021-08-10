from flask import Flask, request, Response, jsonify, make_response;
from applications.configuration import Configuration;
from applications.models import database, Participant, Election, Vote, Result, ParticipantElection;
from applications.user.participant import participantBlueprint;
from applications.user.election import electionBlueprint;
from flask_jwt_extended import JWTManager, get_jwt;
from applications.admin.adminDecorator import roleCheck;
from redis import Redis;
from sqlalchemy import and_;
import datetime;
import io;
import csv;

application = Flask( __name__ );
application.config.from_object(Configuration);

application.register_blueprint ( participantBlueprint, url_prefix = "/participants" );
application.register_blueprint ( electionBlueprint, url_prefix = "/elections" );

jwt = JWTManager(application);

@application.route("/createParticipant", methods=["POST"])
@roleCheck(role="Admin")
def createParticipant():
    message = "";
    name = request.json.get("name", "");
    individual = request.json.get("individual", "");

    if(len(name)==0):
        message += "Name field is required";
    if(len(individual)==0):
        message += "Individual field is required";

    if(len(message) > 0):
        return make_response(jsonify(message=message), 400);

    individual = boolToInt(individual);

    participant = Participant(name=name, individual=individual);
    database.session.add(participant);
    database.session.commit();
    return make_response(jsonify(id=participant.id), 200);

@application.route("/getParticipants", methods=["GET"])
@roleCheck(role="Admin")
def getParticipants():
    participants = Participant.query.all();
    participantsJSON = [];
    for value in participants:
        participant = {
            "id" : value.id,
            "name" : value.name,
            "individual" : value.individualString()
        }
        participantsJSON.append(participant);
    return make_response(jsonify(participants=participantsJSON), 200);

@application.route("/createElection", methods=["POST"])
@roleCheck(role="Admin")
def createElection():
    message = "";
    inputs = {}
    inputs["start"] = request.json.get("start", "");
    inputs["end"] = request.json.get("end", "");
    inputs["individual"] = request.json.get("individual", "");
    inputs["participants"] = request.json.get("participants", "");
    required = [value for value in inputs if len(inputs[value]) == 0];
    for value in required:
        message += "Field " + value + " is required";

    startBool = isISOFormat(inputs["start"]);
    endBool = isISOFormat(inputs["end"]);
    if(not startBool):
        message += "Bad format for start";
    if(not endBool):
        message += "Bad format for end";
    if(startBool==True and endBool==True):
        start = datetime.datetime.fromisoformat(inputs["start"]);
        end = datetime.datetime.fromisoformat(inputs["end"]);
        if(start > end):
            message += "Start needs to be before end";

    participants = [];
    if(len (inputs["participants"]) <= 2):
        message += "Participants number is less then 3";
    else:
        for value in inputs["participants"]:
            participant = Participant.query.filter(Participant.id == value).first();
            if(not participant):
                message += "Participant with id "+value+" does not exists";
            else:
                participants.append(participant);
                if(participant.individualString() != inputs["individual"]):
                    if(inputs["individual"]=="false"):
                        message += "Election is parliamentary";
                    else:
                        message += "Election is presidential";
                    break;

    if(len(message)>0):
        return make_response(jsonify(message=message), 400);

    inputs["individual"] = boolToInt(inputs["individual"]);

    election = Election(start=inputs["start"], end=inputs["end"], individual=inputs["individual"], participants=participants);
    database.session.add(election);
    database.session.commit();

    participantsElections = ParticipantElection.query.filter(ParticipantElection.electionId == election.id);
    pollNumber = 1;
    for value in participantsElections:
        value.pollNumber = pollNumber;
        pollNumber += 1;
        database.session.add(value);
    database.session.commit();

    return make_response(jsonify(pollNumbers=list(range(1, len(participants) + 1))), 200);

@application.route("/getElections", methods=["GET"])
@roleCheck(role="Admin")
def getElections():
    elections = Election.query.all();
    electionsJSON = [];
    for value in elections:
        election = {
            "id" : value.id,
            "start" : value.start,
            "end" : value.end,
            "individual" : value.individualString(),
            "participants" : value.getParticipantsJSON()
        }
        electionsJSON.append(election);
    return make_response(jsonify(elections=electionsJSON), 200);

@application.route("/getResults", methods=["GET"])
@roleCheck(role="Admin")
def getResults():
    message = "";
    id = request.args.get("id");
    if(len(id)==0):
        message += "Field id is missing.";
        return make_response(jsonify(message=message), 400);

    election = Election.query.filter(Election.id == int(id)).first();
    if(not election):
        message += "Election does not exist.";
        return make_response(jsonify(message=message), 400);

    todayDate = datetime.datetime.fromisoformat(datetime.datetime.now().isoformat());
    endDate = datetime.datetime.fromisoformat(election.end);
    if(todayDate < endDate):
        message += "Election is ongoing";
        return make_response(jsonify(message=message), 400);

    results = Result.query.filter(Result.electionID == election.id).all();
    votes = Vote.query.filter(Vote.electionID == election.id);
    if(not results):
        message += "Election is ongoing";
        return make_response(jsonify(message=message), 400);

    participants = [];
    invalidVotes = [];
    for result in results:
        participant = Participant.query.filter(Participant.id == result.participantID);
        participants.append({
            "pollNumber" : result.pollNumber,
            "name" : participant.name,
            "result" : result.result
        });

    for vote in votes:
        if(vote.reason != None):
            invalidVotes.append({
                "electionOfficialJmbg" : vote.electionOfficialJmbg,
                "ballotGuid" : vote.guid,
                "pollNumber" : vote.pollNumber,
                "reason" : vote.reason
            })

    return make_response(jsonify(participants=participants, invalidVotes=invalidVotes), 200);

@application.route("/vote", methods=["POST"])
@roleCheck(role="Zvanicnik")
def vote():
    message = "";
    content = request.files["vote"].stream.read().decode("utf-8");
    if(not content):
        message += "Field file is missing.";
        return make_response(jsonify(message=message), 400);

    stream = io.StringIO(content);
    reader = csv.reader(stream);
    claims = get_jwt();
    jmbg = claims["jmbg"];

    with Redis (host= Configuration.REDIS_HOST) as redis:
        redis.rpush(Configuration.REDIS_VOTE_LIST, jmbg);
        line = 0;
        for row in reader:
            if(len (row) < 2):
                message += "Incorrect number of values on line "+str(line);
            else:
                GUID = row[0];
                pollNumber = row[1];
                if(not pollNumber.isnumeric() or (pollNumber.isnumeric() and int(pollNumber) <= 0 )):
                    message += "Incorrect poll number on line "+str(line);
                else:
                    redis.rpush(Configuration.REDIS_VOTE_LIST, GUID);
                    redis.rpush(Configuration.REDIS_VOTE_LIST, pollNumber);
                    line+=1;

    if(len (message) > 0):
        return make_response(jsonify(message=message), 400);
    else:
        return Response(status=200);


def isISOFormat(param):
    try:
        datetime.datetime.fromisoformat(param);
    except:
        return False
    return True;

def boolToInt(param):
    if(param=="false"):
        return 0;
    else:
        return 1;


def ongoingElection(): #popravi sutra
    todayDate = datetime.datetime.fromisoformat(datetime.datetime.now().isoformat());
    elections = Election.query.all();
    for election in elections:
        start = datetime.datetime.fromisoformat(str(election.start));
        end = datetime.datetime.fromisoformat(str(election.end));
        if(start <= todayDate and end > todayDate):
            return election;
    return election;


if( __name__ == "__main__"):
    database.init_app( application )
    application.run( debug=True, port= 5001)

from flask import Flask, request, jsonify, make_response;
from configuration import Configuration;
from models import database, Participant, Election, Vote, Result, ParticipantElection;
from flask_jwt_extended import JWTManager;
from roleCheck import roleCheck;
import datetime;


application = Flask( __name__ );
application.config.from_object(Configuration);

jwt = JWTManager(application);

@application.route("/createParticipant", methods=["POST"])
@roleCheck(role="admin")
def createParticipant():
    name = request.json.get("name", "");
    individual = request.json.get("individual", "");

    if(len(name)==0):
        return make_response(jsonify(message="Field name is missing."), 400);
    if(individual == ""):
        return make_response(jsonify(message="Field individual is missing."), 400);

    individual = boolToInt(individual);

    participant = Participant(name=name, individual=individual);
    database.session.add(participant);
    database.session.commit();
    return make_response(jsonify(id=participant.id), 200);

@application.route("/getParticipants", methods=["GET"])
@roleCheck(role="admin")
def getParticipants():
    participants = Participant.query.all();
    participantsJSON = [];
    for value in participants:
        participant = {
            "id" : value.id,
            "name" : value.name,
            "individual" : value.individualBool()
        }
        participantsJSON.append(participant);
    return make_response(jsonify(participants=participantsJSON), 200);

@application.route("/createElection", methods=["POST"])
@roleCheck(role="admin")
def createElection():
    inputs = {}
    inputs["start"] = request.json.get("start", "");
    inputs["end"] = request.json.get("end", "");
    inputs["individual"] = request.json.get("individual", "");
    inputs["participants"] = request.json.get("participants", "");

    required = [value for value in inputs if inputs[value] == ""];
    for value in required:
        return make_response(jsonify(message="Field " + value + " is missing."), 400);

    # date check
    try:
        start = datetime.datetime.fromisoformat(inputs["start"]);
        end = datetime.datetime.fromisoformat(inputs["end"]);

        if(start > end):
            return make_response(jsonify(message="Invalid date and time."), 400);
        if(electionExists(start,end)):
            return make_response(jsonify(message="Invalid date and time."), 400);

    except Exception as ex:
        return make_response(jsonify(message="Invalid date and time."), 400);

    # participants check
    participants = [];
    if (len(inputs["participants"]) < 2):
        return make_response(jsonify(message="Invalid participants."), 400);
    else:
        for value in inputs["participants"]:
            participant = Participant.query.filter(Participant.id == value).first();
            if (not participant):
                return make_response(jsonify(message="Invalid participants."), 400);
            else:
                participants.append(participant);
                if (participant.individualBool() != inputs["individual"]):
                    return make_response(jsonify(message="Invalid participants."), 400);

    inputs["individual"] = boolToInt(inputs["individual"]);

    election = Election(start=start, end=end, individual=inputs["individual"], participants=participants);
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
@roleCheck(role="admin")
def getElections():
    elections = Election.query.all();
    electionsJSON = [];
    for value in elections:
        electionsJSON.append({
            "id" : value.id,
            "start" : str (value.start),
            "end" : str (value.end),
            "individual" :  value.individualBool(),
            "participants" : value.getParticipantsJSON()
        });
    return make_response(jsonify(elections=electionsJSON), 200);

@application.route("/getResults", methods=["GET"])
@roleCheck(role="admin")
def getResults():
    id = request.args.get("id");
    if(not id):
        return make_response(jsonify(message="Field id is missing."), 400);

    election = Election.query.filter(Election.id == int(id)).first();
    if(not election):
        return make_response(jsonify(message="Election does not exist."), 400);

    todayDate = datetime.datetime.fromisoformat(datetime.datetime.now().isoformat());
    endDate = datetime.datetime.fromisoformat(str ( election.end ) );
    startDate = datetime.datetime.fromisoformat(str( election.start ))
    if(todayDate < endDate and startDate < todayDate):
        return make_response(jsonify(message="Election is ongoing"), 400);

    results = Result.query.filter(Result.electionID == election.id).all();
    votes = Vote.query.filter(Vote.electionID == election.id);
    # if(not results):
    #     return make_response(jsonify(message="Election is ongoing"), 400);

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

def isISOFormat(param):
    try:
        date = datetime.datetime.fromisoformat(param);
    except Exception as ex:
        return False;
    return True;

def boolToInt(param):
    if(param==False):
        return 0;
    else:
        return 1;


def ongoingElection(): #popravi sutra
    todayDate = datetime.datetime.fromisoformat(datetime.datetime.now().isoformat());
    elections = Election.query.all();
    for election in elections:
        if(election.start <= todayDate and election.end > todayDate):
            return election;
    return election;

def electionExists(start, end):
    elections = Election.query.all();
    for election in elections:
        if((election.start >= start and election.start <= end) or (election.start <= start and election.end >= start)):
            return True;

    return False;

if( __name__ == "__main__"):
    database.init_app( application )
    application.run( debug=True, host="0.0.0.0", port= 5001)

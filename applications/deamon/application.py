from flask import Flask, Response, make_response, jsonify;
from configuration import Configuration;
from models import database, Vote, ParticipantElection, Election;
from redis import Redis;
import datetime;

application = Flask( __name__ );
application.config.from_object(Configuration)

def ongoingElection(): #popravi sutra
    todayDate = datetime.datetime.fromisoformat(datetime.datetime.now().isoformat());
    elections = Election.query.all();
    for election in elections:
        if(election.start <= todayDate and election.end > todayDate):
            return election;
    return None;

@application.route("/", methods=['GET', 'POST'])
def deamon():
    while(True):
        election = ongoingElection();
        if (not election):
            continue;
        with Redis(host= Configuration.REDIS_HOST) as redis:
            item = redis.lpop(Configuration.REDIS_VOTE_LIST);
            if item == None:
                continue;
            jmbg = item;
            guids = [];
            empty = False;
            while(not empty):
                GUID = redis.lpop(Configuration.REDIS_VOTE_LIST);
                if(not GUID):
                    empty = True;
                    continue;
                pollNumber = int(redis.lpop(Configuration.REDIS_VOTE_LIST));
                reason = "";
                for guid in guids:
                    if(guid == GUID):
                        reason = "Duplicate ballot.";
                else:
                    guids.append(GUID);

                participantElection = ParticipantElection.query.filter(ParticipantElection.electionId == election.id);

                exists = False;
                for value in participantElection:
                    if(value.pollNumber == pollNumber):
                        exists = True;
                if(not exists):
                    reason = "Invalid poll number.";
                if(len(reason)<1):
                    vote = Vote(guid=GUID, pollNumber=pollNumber, electionOfficialJmbg=jmbg, electionID=election.id);
                    database.session.add(vote);
                    database.session.commit();
                else:
                    vote = Vote(guid=GUID, pollNumber=pollNumber, electionOfficialJmbg=jmbg, reason=reason, electionID=election.id);
                    database.session.add(vote);
                    database.session.commit();



if( __name__ == "__main__"):
    database.init_app( application )
    application.run( debug=True, host="0.0.0.0", port= 5003)


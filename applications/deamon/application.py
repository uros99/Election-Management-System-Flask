from flask import Flask, Response, make_response, jsonify;
from applications.configuration import Configuration;
from applications.models import database, Vote, ParticipantElection;
from redis import Redis;
from applications.admin.application import ongoingElection;

application = Flask( __name__ );
application.config.from_object(Configuration)


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
                if(GUID in guids):
                    reason = "Duplicate ballot";
                else:
                    guids.append(GUID);
                participantElection = ParticipantElection.query.filter(ParticipantElection.electionId == election.id);

                exists = False;
                for value in participantElection:
                    if(value.pollNumber == pollNumber):
                        exists = True;
                if(not exists):
                    reason = "Invalid poll number";
                if(len(reason)==0):
                    vote = Vote(guid=GUID, pollNumber=pollNumber, electionOfficialJmbg=jmbg, electionID=election.id);
                else:
                    vote = Vote(guid=GUID, pollNumber=pollNumber, electionOfficialJmbg=jmbg, reason=reason, electionID=election.id);
                database.session.add(vote);
                database.session.commit();


if( __name__ == "__main__"):
    database.init_app( application )
    application.run( debug=True, port= 5003)


from flask import Flask;
from configuration import Configuration;
from flask_migrate import Migrate, init, migrate, upgrade;
from models import database, Election, Participant, ParticipantElection, Vote, Result;
from sqlalchemy_utils import database_exists, create_database;

application = Flask ( __name__ );
application.config.from_object(Configuration);

migrateObject = Migrate ( application, database);

if(not database_exists(application.config["SQLALCHEMY_DATABASE_URI"])):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"]);

database.init_app(application);

with application.app_context() as context:
        init();
        migrate( message="Production migrate");
        upgrade();

        elections = Election.query.all();
        participants = Participant.query.all();
        participantsElections = ParticipantElection.query.all();
        votes = Vote.query.all();
        results = Result.query.all();

        for election in elections:
            database.session.add(election);
        for participant in participants:
            database.session.add(participant);
        for participantElection in participantsElections:
            database.session.add(participantElection);
        for vote in votes:
            database.session.add(vote);
        for result in results:
            database.session.add(result);

        database.session.commit();










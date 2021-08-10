from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy();


class ParticipantElection ( database.Model ):
    __tablename__ = "participantelection";
    id = database.Column(database.Integer, primary_key=True);
    participantId = database.Column(database.Integer, database.ForeignKey("participant.id"), nullable=False);
    electionId = database.Column(database.Integer, database.ForeignKey("election.id"), nullable=False);
    pollNumber = database.Column(database.Integer, nullable=True);

class Participant (database.Model):
    __tablename__ = "participant";
    id = database.Column(database.Integer, primary_key = True);
    name = database.Column(database.String(256), nullable=False);
    individual = database.Column(database.Integer, nullable=False);
    elections = database.relationship("Election", secondary=ParticipantElection.__table__, back_populates="participants")

    def individualString(self):
        if(self.individual==0):
            return "false";
        return "true";

    def __repr__(self):
        return "id:{}, name:{}, individual:{}".format(self.id,self.name,self.individualString());


class Election (database.Model):
    __tablename__ = "election";
    id = database.Column(database.Integer, primary_key=True);
    start = database.Column(database.String(45), nullable=False);
    end = database.Column(database.String(45), nullable=False);
    individual = database.Column(database.Integer, nullable=False);
    participants = database.relationship("Participant", secondary=ParticipantElection.__table__, back_populates="elections")

    def individualString(self):
        if(self.individual==0):
            return "false";
        return "true";

    def getParticipantsJSON(self):
        participantsJSON = [];
        for value in self.participants:
            participant = {
                "id" : value.id,
                "name" : value.name
            }
            participantsJSON.append(participant);
        return participantsJSON;

    def __repr__(self):
        return "id:{}, start:{}, end:{}, individual:{}".format(self.id,self.start, self.end, self.individualString())


class Result(database.Model):
    __tablename__ = "result";
    id = database.Column(database.Integer, primary_key=True);
    pollNumber = database.Column(database.Integer);
    result = database.Column(database.Integer, nullable=True);
    participantID = database.Column(database.Integer, database.ForeignKey("participant.id"), nullable=False);
    electionID = database.Column(database.Integer, database.ForeignKey("election.id"), nullable=False);

    def __repr__(self):
        return "id:{}, pollNumber:{}, result:{}, participant:{}".format(self.id,self.pollNumber,self.result,self.participantID);

class Vote (database.Model):
    __tablename__ = "vote";
    id = database.Column(database.Integer, primary_key=True);
    guid = database.Column(database.Integer, nullable=False);
    pollNumber = database.Column(database.Integer, nullable=False);
    reason = database.Column(database.String (256), nullable=True);
    electionID = database.Column(database.Integer, database.ForeignKey("election.id"), nullable=False);
    electionOfficialJmbg = database.Column(database.String(13), nullable=False);

    def __repr__(self):
        return "guid:{}, pollNumber:{}".format(self.guid,self.pollNumber);
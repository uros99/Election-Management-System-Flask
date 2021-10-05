from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy();

class UserRole( database.Model ):
    __tablename__ = "userrole";
    id = database.Column(database.Integer, primary_key = True);
    userId = database.Column( database.Integer, database.ForeignKey("user.id"), nullable=False );
    roleId = database.Column(database.Integer, database.ForeignKey("role.id"), nullable=False);


class User (database.Model):
    __tablename__ = "user";
    id = database.Column(database.Integer, primary_key = True);
    email = database.Column(database.String (45), nullable= False, unique=True);
    password = database.Column(database.String(45), nullable=False);
    forename = database.Column(database.String(45), nullable=False);
    lastname = database.Column(database.String(45), nullable=False);
    jmbg = database.Column( database.String(13), nullable=False, unique=True);
    roles = database.relationship("Role", secondary=UserRole.__table__, back_populates="users");

    def __repr__(self):
        return "({} {})".format(self.forename, self.lastname)


class Role ( database.Model ):
    __tablename__ = "role";
    id = database.Column(database.Integer, primary_key=True);
    role = database.Column(database.String ( 45 ), nullable=False);

    users = database.relationship("User", secondary=UserRole.__table__, back_populates="roles");

    def __repr__(self):
        return "{}".format(self.role);

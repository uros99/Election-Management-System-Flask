from flask import Flask;
from configuration import Configuration;
from flask_migrate import Migrate, init, migrate, upgrade;
from models import database, User, Role, UserRole;
from sqlalchemy_utils import database_exists, create_database;

application = Flask ( __name__ );
application.config.from_object(Configuration);

migrateObject = Migrate ( application, database);
done = False;

while(not done):
    try:
        if(not database_exists(application.config["SQLALCHEMY_DATABASE_URI"])):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"]);

        database.init_app(application);

        with application.app_context() as context:
            init();
            migrate( message="Production migrate");
            upgrade();

            adminRole = Role(role="admin");
            userRole = Role(role="user");

            database.session.add(adminRole);
            database.session.add(userRole);
            database.session.commit();

            admin = User(
                lastname="admin",
                forename="admin",
                email="admin@admin.com",
                password="1",
                jmbg="0000000000000"
            )

            database.session.add(admin);
            database.session.commit();

            userRole = UserRole(
                userId=admin.id,
                roleId=adminRole.id
            )

            database.session.add(userRole);
            database.session.commit();

        done = True;
    except Exception as exception:
        print(exception)
class Configuration:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/election";
    JWT_SECRET_KEY = "JWT_SECRET_KEY";
    REDIS_HOST = "localhost";
    REDIS_VOTE_LIST = "votes"
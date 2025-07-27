class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://cis440summer2025team2:cis440summer2025team2@107.180.1.16:3306/cis440summer2025team2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'cis440summer2025team2'

    # <-- add this
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,     # ping before using a pooled connection
        "pool_recycle": 280,       # recycle connections before MySQL kills them (seconds)
        "pool_size": 5,
        "max_overflow": 10
    }
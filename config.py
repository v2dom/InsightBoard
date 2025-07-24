class Config:
    # Basic configuration for the Flask application
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://<username>:<password>@<ip of db>:<port>/<schema>'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '<a word or phrase used to encrypt>'  # You should replace this with a stronger key in production
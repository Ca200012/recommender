from sqlalchemy import create_engine

def get_db_engine():
    return create_engine('mysql+pymysql://root:@localhost/licenta-back')
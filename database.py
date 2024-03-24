from sqlalchemy import create_engine, MetaData, Table, Column, JSON, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dotenv
import os
import sqlalchemy

dotenv.load_dotenv()
Base = declarative_base()


class AmoCRM(Base):
    __tablename__ = 'amocrm'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    host = Column(String)
    widget_id = Column(String)

    def __repr__(self):
        return f"<AmoCRM(id={self.id}, email='{self.email}', password='{self.password}', host='{self.host}')>"


class AmoCRMSession(Base):
    __tablename__ = 'amocrm_sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)

    host = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    amojo_id = Column(String)
    chat_token = Column(String)
    headers = Column(JSON)


class WidgetAmo(Base):
    __tablename__ = 'home_widgetamo'
    id = Column(Integer, primary_key=True)

    client_id = Column(String)
    cleint_secret = Column(String)
    state = Column(String)


def read_accounts():
    site_engine = sqlalchemy.create_engine(
        f'postgresql://{os.getenv("SITE_DB_USER")}:{os.getenv("SITE_DB_PASSWORD")}'
        f'@{os.getenv("SITE_DB_HOST")}:5432/{os.getenv("SITE_DB_NAME")}',
        pool_pre_ping=True
    )
    metadata = MetaData()

    metadata.reflect(bind=site_engine)

    Session = sessionmaker(bind=site_engine)
    session = Session()
    session.expire_all()

    accounts = session.query(AmoCRM).all()
    response = []
    for account in accounts:
        client_id = ''
        client_secret = ''
        if account.widget_id is not None:
            widget = session.query(WidgetAmo).filter_by(client_id=account.widget_id).first()
            client_id = widget.client_id
            client_secret = widget.cleint_secret
        response.append({'client_id': client_id, 'client_secret': client_secret, 'host': account.host, 'email': account.email, 'password': account.password})

    session.close()
    return response


def update_session(account: AmoCRM, session_data):
    api_engine = sqlalchemy.create_engine(
        f'postgresql://{os.getenv("API_DB_USER")}:{os.getenv("API_DB_PASSWORD")}'
        f'@{os.getenv("API_DB_HOST")}:5432/{os.getenv("API_DB_NAME")}',
        pool_pre_ping=True
    )

    Session = sessionmaker(bind=api_engine)
    session = Session()

    # Assuming 'account' contains an identifier for the session
    db_session = session.query(AmoCRMSession).filter(AmoCRMSession.host == account['host']).first()

    if db_session:
        # Update existing session
        db_session.access_token = session_data['access_token']
        db_session.refresh_token = session_data['refresh_token']
        db_session.host = account['host']
        db_session.amojo_id = session_data['amojo_id']
        db_session.chat_token = session_data['chat_token']
        db_session.headers = session_data['headers']
    else:
        # Create new session entry
        new_session = AmoCRMSession(
            access_token=session_data['access_token'],
            refresh_token=session_data['refresh_token'],
            host=account['host'],
            amojo_id=session_data['amojo_id'],
            chat_token=session_data['chat_token'],
            headers=session_data['headers']
        )
        session.add(new_session)

    session.commit()
    session.close()

from config import DB_URI, DB_SCHEMA, EVENT_TABLE_NAME, EVENT_INFO_TABLE_NAME
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, sessionmaker

engine = sa.create_engine(DB_URI)
Session = sessionmaker(engine)
meta = sa.MetaData(schema=DB_SCHEMA)
Base = declarative_base(engine, meta)


class EventModel(Base):
    __tablename__ = EVENT_TABLE_NAME

    id = sa.Column(sa.Integer, primary_key=True)
    inner_id = sa.Column(sa.String)
    lang = sa.Column(sa.String)
    publication_date = sa.Column(sa.Date)
    event_date = sa.Column(sa.String)
    event_time = sa.Column(sa.String)
    price = sa.Column(sa.String)
    title = sa.Column(sa.String)
    location = sa.Column(sa.String)
    description = sa.Column(sa.String)
    buy_link = sa.Column(sa.String)
    source_link = sa.Column(sa.String)
    site_link = sa.Column(sa.String)
    founded_timestamp = sa.Column(sa.DateTime(timezone=True), default=func.current_timestamp())

    @classmethod
    def save_insert(cls, data, check_keys):
        check_data = {k: data[k] for k in check_keys}
        with Session.begin() as session:
            if not session.query(cls).filter_by(**check_data).scalar():
                i = cls(**data)
                session.add(i)


with Session.begin() as session:
    session.execute(f'CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}')
Base.metadata.create_all()

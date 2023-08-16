import os
import sys
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from utils.log.main import log

DATABASE_PATH = "./data/.db/dashboard/dashboard.db"
if not os.path.exists(os.path.dirname(DATABASE_PATH)):
    os.makedirs(os.path.dirname(DATABASE_PATH))

# Define a base class for declarative models
Base = declarative_base()


class Dashboard(Base):
    __tablename__ = 'dashboard'
    id = Column(Integer, primary_key=True)
    download_or_upload = Column(String)  # 'Download' or 'Upload'
    name = Column(String)
    unique_id = Column(String)
    lazy_file_hash = Column(String)
    table_name = Column(String)
    percentage = Column(Integer)
    Size = Column(Integer)
    file_location = Column(String)

    def __str__(self):
        return f"ID: {self.id}, Download or Upload: {self.download_or_upload}, Name: {self.name}, Unique ID: {self.unique_id}, Lazy File Hash: {self.lazy_file_hash}, Table Name: {self.table_name}, Percentage: {self.percentage}, Size: {self.Size}, File Location: {self.file_location}"


def create_database():
    # Create db if not exists
    database = f"sqlite:///{DATABASE_PATH}"
    engine = create_engine(database)
    Base.metadata.create_all(engine)


def update_dashboard_db(download_or_upload, name, unique_id, lazy_file_hash, table_name, percentage, Size, file_location):
    create_database()
    database = f"sqlite:///{DATABASE_PATH}"
    engine = create_engine(database)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Check if a record exists
    existing_record = session.query(Dashboard).filter(
        Dashboard.lazy_file_hash == lazy_file_hash, Dashboard.download_or_upload == download_or_upload).first()

    if existing_record:
        existing_record.percentage = min(
            100, max(percentage, existing_record.percentage))
        existing_record.Size = max(Size, existing_record.Size)
        log(f"Updating dashboard entry: {download_or_upload}, {name}, {unique_id}, {lazy_file_hash}, {table_name}, {min(100,max(percentage, existing_record.percentage))},{max(Size, existing_record.Size)} {file_location}")
    else:
        new_entry = Dashboard(download_or_upload=download_or_upload, name=name, unique_id=unique_id, lazy_file_hash=lazy_file_hash,
                              table_name=table_name, percentage=min(100, percentage), Size=Size, file_location=file_location)
        session.add(new_entry)
        log(f"Adding dashboard entry: {download_or_upload}, {name}, {unique_id}, {lazy_file_hash}, {table_name}, {min(100,percentage)},{Size}, {file_location}")

    session.commit()
    session.close()

def search_dashboard_db(search_bys, searchs):
    create_database()
    database = f"sqlite:///{DATABASE_PATH}"
    engine = create_engine(database)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Check if a record exists
    query_filters = [getattr(Dashboard, search_by) == search for search_by, search in zip(search_bys, searchs)]
    existing_record = session.query(Dashboard).filter(*query_filters).all()
    return [{"id": entry.id, "download_or_upload": entry.download_or_upload, "name": entry.name, "unique_id": entry.unique_id,
                "lazy_file_hash": entry.lazy_file_hash, "table_name": entry.table_name,
                "percentage": entry.percentage, "Size": entry.Size,
                "file_location": entry.file_location} for entry in existing_record]

def delete_row_dashboard_db(download_or_upload, lazy_file_hash):
    create_database()
    database = f"sqlite:///{DATABASE_PATH}"
    engine = create_engine(database)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Check if a record exists
    existing_record = session.query(Dashboard).filter(
        Dashboard.lazy_file_hash == lazy_file_hash, Dashboard.download_or_upload == download_or_upload).first()

    if existing_record:
        session.delete(existing_record)
        log(f"Deleting dashboard entry: {download_or_upload}, {lazy_file_hash}")
    else:
        log(f"Dashboard entry not found for row_deletion: {download_or_upload}, {lazy_file_hash}",2)

    session.commit()
    session.close()


def fetch_all_entries():
    create_database()
    database = f"sqlite:///{DATABASE_PATH}"
    engine = create_engine(database)

    Session = sessionmaker(bind=engine)
    session = Session()

    entries = session.query(Dashboard).all()
    session.close()

    results = [{"id": entry.id, "download_or_upload": entry.download_or_upload, "name": entry.name, "unique_id": entry.unique_id,
                "lazy_file_hash": entry.lazy_file_hash, "table_name": entry.table_name,
                "percentage": entry.percentage, "Size": entry.Size,
                "file_location": entry.file_location} for entry in entries]

    log(f"Fetching dashboard entries of len {len(results)}")
    return results


if __name__ == "__main__":
    update_dashboard_db("Upload", "Game", "unique_id3",
                        "lazy_file_hash2", "table_name", 54, 100, "file_location")
    log(fetch_all_entries())
    delete_row_dashboard_db("Upload", "lazy_file_hash2")
    log(search_dashboard_db(["download_or_upload", "lazy_file_hash"], ["Upload", "lazy_file_hash2"]))
    log(search_dashboard_db(["download_or_upload", "lazy_file_hash"], ["Download", "7453adedd3a1c5dded3b51ff7aaf085a"]))
    delete_row_dashboard_db("Download", "7453adedd3a1c5dded3b51ff7aaf085a")
    log(search_dashboard_db(["download_or_upload", "lazy_file_hash"], ["Download", "7453adedd3a1c5dded3b51ff7aaf085a"]))


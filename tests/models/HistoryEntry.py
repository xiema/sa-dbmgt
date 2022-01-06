from sqlalchemy import Column, Integer, String, Boolean
from .Metadata import Metadata


class HistoryEntry(Metadata):
    __tablename__ = 'history'
    id = Column(String, primary_key=True)
    column_name = Column(String, nullable=False)
    info_old = Column(String, nullable=False)
    info_new = Column(String, nullable=False)
    timestamp_old = Column(String, nullable=False)
    timestamp_new = Column(String, nullable=False)

    def __repr__(self):
        return f"<History Entry {self.id}: {self.column_name} {self.info_old} -> {self.info_new}>"

from sqlalchemy import Column, Integer, String, Boolean
from .Metadata import Metadata


class YouTubeVideo(Metadata):
    __tablename__ = 'video_info'
    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    author = Column(String)
    channel_id = Column(String)
    title = Column(String)
    description = Column(String)
    length = Column(String)
    publish_date = Column(String)
    upload_date = Column(String)
    live_content = Column(String)
    views = Column(String)
    family_safe = Column(String)
    keywords = Column(String)
    chapters = Column(String)
    likes = Column(String)
    dislikes = Column(String)
    unlisted = Column(String)
    category = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    timestamp = Column(String)
    last_checked = Column(String)
    chat_available = Column(String)
    average_rating = Column(String)
    __reprstr__ = "<YouTube Video {id}: {title}>"

    # def __repr__(self):
    #     return f"<YouTube Video {self.id}: {self.title}>"

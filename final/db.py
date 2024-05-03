import os
import time
import pymysql
from pymysql.cursors import DictCursor
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
# from dotenv import load_dotenv
from datetime import datetime


# todo:后续改为调用.env
# load_dotenv()
# db_host = os.getenv('DB_HOST')
# db_port = int(os.getenv('DB_PORT'))
# db_user = os.getenv('DB_USER')
# db_password = os.getenv('DB_PASSWORD')
# db_name = os.getenv('DB_NAME')

class DatabaseConnection:
    def __init__(self):
        self.con = pymysql.connect(
            host='xrj-warehouse.c524wq86ghc0.us-west-2.rds.amazonaws.com',
            port=3306,
            user='xrj_warehouse',
            password='dsfx1711',
            database='warehouse',
        )
        self.cur = self.con.cursor(DictCursor)  # 使用 DictCursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.con.close()


@dataclass
class SentenceData:
    id: int = 0
    interview_id: int = 0
    role: str = ''
    origin_sentence: str = ''
    ai_sentence: str = ''
    label: str = ''
    duration: int = 0
    create_time: datetime = field(default_factory=datetime.now)
    update_time: datetime = field(default_factory=datetime.now)


@dataclass
class InterviewData:
    id: int = 0
    summary: str = ''
    duration: int = 0
    create_time: datetime = field(default_factory=datetime.now)
    update_time: datetime = field(default_factory=datetime.now)
    sentences: List[SentenceData] = field(default_factory=list)


def insert_interview(summary: str, duration: int) -> int:
    with DatabaseConnection() as db:
        query = "INSERT INTO interview (summary, duration) VALUES (%s, %s)"
        db.cur.execute(query, (summary, duration))
        interview_id = db.con.insert_id()
        db.con.commit()
        return interview_id


def update_interview(interview_id: int, summary: str, duration: int) -> None:
    with DatabaseConnection() as db:
        query = "UPDATE interview SET summary = %s, duration = %s WHERE id = %s"
        db.cur.execute(query, (summary, duration, interview_id))
        db.con.commit()


def insert_sentence(sentence: SentenceData) -> int:
    with DatabaseConnection() as db:
        query = """
        INSERT INTO sentence (interview_id, role, origin_sentence, ai_sentence, label, duration, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            sentence.interview_id, sentence.role, sentence.origin_sentence, sentence.ai_sentence, sentence.label,
            sentence.duration,
            sentence.create_time, sentence.update_time)
        db.cur.execute(query, params)
        sentence_id = db.con.insert_id()
        db.con.commit()
        return sentence_id


def get_all_interview() -> List[InterviewData]:
    with DatabaseConnection() as db:
        db.cur.execute("SELECT * FROM interview")
        interviews = []
        for v in db.cur.fetchall():
            interview = InterviewData(
                id=v['id'],
                summary=v['summary'],
                duration=v['duration'],
                create_time=v['create_time'],
                update_time=v['update_time']
            )
            interviews.append(interview)
        return interviews


def get_sentence_by_interview(interview_id: int) -> List[SentenceData]:
    with DatabaseConnection() as db:
        db.cur.execute("SELECT * FROM sentence WHERE interview_id = %s", (interview_id,))
        sentences = []
        for sentence_data in db.cur.fetchall():
            sentence = SentenceData(
                id=sentence_data['id'],
                interview_id=sentence_data['interview_id'],
                role=sentence_data['role'],
                origin_sentence=sentence_data['origin_sentence'],
                ai_sentence=sentence_data['ai_sentence'],
                label=sentence_data['label'],
                duration=sentence_data['duration'],
                create_time=sentence_data['create_time'],
                update_time=sentence_data['update_time']
            )
            sentences.append(sentence)
        return sentences


def get_all_data() -> List[InterviewData]:
    interviews = get_all_interview()
    for interview in interviews:
        sentences = get_sentence_by_interview(interview.id)
        interview.sentences.extend(sentences)
    return interviews

import os
import time
import pymysql
from pymysql.cursors import DictCursor
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class DatabaseConnection:
    def __init__(self):
        self.con = pymysql.connect(
            host=os.getenv('host'),
            port=int(os.getenv('port')),
            user=os.getenv('user'),
            password=os.getenv('password'),
            database=os.getenv('database'),
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
    project_id: int = 0
    summary: str = ''
    duration: int = 0
    create_time: datetime = field(default_factory=datetime.now)
    update_time: datetime = field(default_factory=datetime.now)
    sentences: List[SentenceData] = field(default_factory=list)


def insert_interview(project_id: int, summary: str, duration: int) -> int:
    with DatabaseConnection() as db:
        query = "INSERT INTO interview (project_id, summary, duration) VALUES (%s, %s, %s)"
        db.cur.execute(query, (project_id, summary, duration))
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


def get_all_interview(project_id: int) -> List[InterviewData]:
    with DatabaseConnection() as db:
        db.cur.execute("SELECT * FROM interview WHERE project_id = %s ORDER BY create_time DESC", (project_id,))
        interviews = []
        for v in db.cur.fetchall():
            interview = InterviewData(
                id=v['id'],
                project_id=v['project_id'],
                summary=v['summary'],
                duration=v['duration'],
                create_time=v['create_time'],
                update_time=v['update_time']
            )
            interviews.append(interview)
        return interviews


def get_interview(interview_id: int) -> InterviewData:
    with DatabaseConnection() as db:
        db.cur.execute("SELECT * FROM interview WHERE id = %s", (interview_id,))
        for v in db.cur.fetchall():
            interview = InterviewData(
                id=v['id'],
                project_id=v['project_id'],
                summary=v['summary'],
                duration=v['duration'],
                create_time=v['create_time'],
                update_time=v['update_time']
            )
            return interview


def get_sentence_by_interview(interview_id: int) -> List[SentenceData]:
    with DatabaseConnection() as db:
        db.cur.execute("SELECT * FROM sentence WHERE interview_id = %s ORDER BY create_time ASC", (interview_id,))
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


def get_interview_data(interview_id: int) -> InterviewData:
    interview = get_interview(interview_id)
    sentences = get_sentence_by_interview(interview.id)
    interview.sentences.extend(sentences)
    return interview


def get_project_data(project_id: int) -> List[InterviewData]:
    interviews = get_all_interview(project_id)
    for interview in interviews:
        sentences = get_sentence_by_interview(interview.id)
        interview.sentences.extend(sentences)
    return interviews


def get_all_projects():
    with DatabaseConnection() as db:
        db.cur.execute(
            "SELECT DISTINCT project_id, MIN(create_time) as create_time FROM interview GROUP BY project_id ORDER BY create_time DESC")
        projects = db.cur.fetchall()
        return projects

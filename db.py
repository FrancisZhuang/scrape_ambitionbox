"""db set up"""
import logging
import sqlite3
import os
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class Storage:
    """db class"""

    def __init__(self):
        self.current_path = os.getcwd()
        self.__db_file = os.path.join(self.current_path, 'LinkHumansTest.db')
        self.__ensure_db()

    def __ensure_db(self):
        flag_file = os.path.join(self.current_path, 'db_inited.flag')
        if os.path.exists(flag_file):
            return
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        with conn:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS AmbitionBox (
                    review_id text PRIMARY KEY,
                    company_name text,
                    date text,
                    job_title text,
                    location text,
                    pros text,
                    cons,
                    url_comment text,
                    job_status text
                );
            ''')
            Path(flag_file).touch()

        logger.info('AmbitionBox database inited')

    def add_comment_data(self, review_id, company, post_date, job_title, location, pros, cons,
                         comment_url, job_status) -> None:
        """Add user's data"""
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        with conn:
            cursor.execute('INSERT INTO AmbitionBox VALUES (:review_id, :company, :post_date, '
                           ':job_title, :location, :pros, :cons, :comment_url, :job_status);',
                           {'review_id': review_id,
                            'company': company,
                            'post_date': post_date,
                            'job_title': job_title,
                            'location': location,
                            'pros': pros,
                            'cons': cons,
                            'comment_url': comment_url,
                            'job_status': job_status})

    def has_review_id(self, review_id) -> bool:
        """Check if user id exist"""
        conn = sqlite3.connect(self.__db_file)
        cursor = conn.cursor()
        with conn:
            cursor.execute('SELECT COUNT(*) FROM AmbitionBox WHERE review_id = :review_id', {'review_id': review_id})
            return cursor.fetchone()[0]

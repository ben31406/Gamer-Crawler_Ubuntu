"""This file is a DAG definition file.

This file contains two tasks, the first task is to crawl all target boards whose hot value is greater than or equal to HOT_VALUE,
and the second task is to crawl all article information of the target boards.
"""


import pendulum
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator


local_tz = pendulum.timezone("Asia/Taipei")

default_args = {
    'owner': 'Ben',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}   
       
dag = DAG(
    dag_id='gamer-crawler',
    start_date=datetime(2021,8,28,15,0, tzinfo=local_tz),
    schedule_interval='@hourly',
    default_args=default_args
)

craw_target_board = BashOperator(
            task_id='crawl_target_board',
            bash_command='cd /app/gamer_crawler && scrapy crawl Target_board',
            dag=dag)

craw_board_info = BashOperator(
            task_id='crawl_board_info',
            bash_command='cd /app/gamer_crawler/gamer_crawler && python3 multiprocess_board_crawler.py',
            dag=dag)


craw_target_board >> craw_board_info

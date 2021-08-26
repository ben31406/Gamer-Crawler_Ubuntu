from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
import pendulum

local_tz = pendulum.timezone("Asia/Taipei")

default_args = {
    'owner': 'Ben',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}   
    
   
dag = DAG(
    dag_id='gamer-crawler',
    start_date=datetime(2021,8,26,22,52, tzinfo=local_tz),
    schedule_interval='@once',
    default_args=default_args,
    catchup=False,
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

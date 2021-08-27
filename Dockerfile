FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update \
  && apt-get install sudo \
  && sudo apt-get install -y python3 python3-dev python3-pip \
  && sudo apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev 
EXPOSE 8080
WORKDIR /app
ENV AIRFLOW_HOME=/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt 
COPY . .
WORKDIR /app/gamer_crawler
CMD airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin && airflow db init && airflow webserver -p 8080



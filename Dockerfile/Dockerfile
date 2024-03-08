
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

EXPOSE 5000

RUN apt-get update && \
    apt-get install -y python3  python3-pip

COPY requirements.txt ./
RUN python3 -m pip install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    apt-get clean

COPY . /work
COPY SimHei.ttf /usr/share/fonts/

ENV PYTHONPATH=/work

WORKDIR /work

CMD ["python3", "flasktrytry/app.py"]
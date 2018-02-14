FROM python:2.7 
RUN apt-get update
RUN apt-get --assume-yes install python-setuptools 
RUN virtualenv ../venv
RUN git clone https://fi241c@codecloud.web.att.com/scm/st_cloudqos/conductor.git
WORKDIR ./conductor
RUN pip install . 
RUN pwd

RUN echo "Starting conductor-data"
CMD ["python","/usr/local/bin/conductor-data", "--config-file=/usr/local/bin/conductor.conf"]

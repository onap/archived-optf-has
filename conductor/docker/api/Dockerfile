FROM python:2.7 
RUN apt-get update
RUN apt-get --assume-yes install python-setuptools 
RUN git clone https://fi241c@codecloud.web.att.com/scm/st_cloudqos/conductor.git
WORKDIR ./conductor
RUN pip install . 
COPY ./conductor.conf conductor.conf
COPY ./api_paste.ini api_paste.ini
RUN ls -ltr /usr/local/bin/conductor-api
CMD ["sh","-c", "python /usr/local/bin/conductor-api --port=8091 -- --config-file=conductor.conf"]

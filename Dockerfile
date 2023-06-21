FROM immauss/openvas:latest
WORKDIR /run/bsoskaner

RUN pip install pytz
RUN pip install icalendar
RUN pip install flask
RUN pip install flask-session

RUN apt-get update
RUN apt-get install -y mailutils
RUN mkdir /etc/bsoskaner
RUN touch /etc/bsoskaner/scanner.log
RUN mkdir /etc/bsoskaner/reports
ENV RUNNING_IN_DOCKER=1
ENV FLASK_APP=/run/bsoskaner/src/app.py

COPY . .

RUN mv single.sh /scripts
RUN mv config/template /etc/bsoskaner
RUN mv config/password /etc/bsoskaner
RUN mv config/mailutils/* /etc
RUN mv config/postfix/* /etc/postfix
RUN mv config/default.cfg config/config.cfg
RUN postmap /etc/postfix/sasl_passwd
RUN postmap /etc/postfix/header_checks

EXPOSE 8080
EXPOSE 9390
EXPOSE 5000

ENTRYPOINT ["/scripts/start.sh"]
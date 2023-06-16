FROM immauss/openvas:latest
WORKDIR /run/bsoskaner
COPY . .

RUN apt-get update
RUN apt-get install -y mailutils
RUN pip install pytz
RUN pip install icalendar
RUN postconf maillog_file=/var/log/mail
RUN service postfix start
RUN mkdir /etc/bsoskaner
RUN mv config/template /etc/bsoskaner
RUN mv config/mailutils/* /etc
RUN mv config/postfix/* /etc/postfix
RUN postmap /etc/postfix/sasl_passwd
RUN postmap /etc/postfix/header_checks
RUN touch /etc/bsoskaner/scanner.log
RUN mkdir /etc/bsoskaner/reports
ENV RUNNING_IN_DOCKER=1

EXPOSE 8080
EXPOSE 9390
EXPOSE 5000

ENTRYPOINT ["start.sh"]
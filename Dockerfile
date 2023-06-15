FROM immauss/openvas:latest
WORKDIR /run/bsoskaner
COPY . .

RUN pip install pytz
RUN pip install icalendar
RUN mv bsoskaner /etc
RUN mv config/mailutils.conf /etc
RUN mv config/main.cf /etc/postfix
RUN mv config/sasl_passwd /etc/postfix
RUN postmap /etc/postfix/sasl_passwd
RUN touch /etc/bsoskaner/scanner.log
RUN mkdir /etc/bsoskaner/reports

EXPOSE 8080
EXPOSE 9390
EXPOSE 5000

WORKDIR /run/bsoskaner/src

ENTRYPOINT ["/scripts/start.sh", "&", "python3", "main.py"]
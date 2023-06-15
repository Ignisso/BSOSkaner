FROM immauss/openvas:latest
WORKDIR /run/bsoskaner
COPY . .

RUN pip install pytz
RUN pip install icalendar
RUN mv bsoskaner /etc
RUN touch /etc/bsoskaner/scanner.log
RUN mkdir /etc/bsoskaner/reports

EXPOSE 8080
EXPOSE 9390
EXPOSE 5000

WORKDIR /run/bsoskaner/src
ENTRYPOINT ["python3", "main.py"]
ENTRYPOINT ["bash"]
import os
import pytz
import dateutil.parser
from datetime import datetime, timedelta
from time import sleep
from openvaslib import OpenVAS as openvas
from os import environ

OpenVAS = None
if (environ.get('RUNNING_IN_DOCKER') is not None):
	OpenVAS = openvas("localhost", 9390, "admin", "admin")
else:
	OpenVAS = openvas("localhost", 9390, "admin", "admin")

if __name__ == "__main__":
	while True:
		if not OpenVAS.is_connected():
			OpenVAS.reconnect()
		reports = OpenVAS.get_reports()

		for report in reports[:-4]:
			id = report.find("report").get("id")
			name = report.find("name").text
			status = report.find("report").find("scan_run_status").text

			if status == "Done" and dateutil.parser.parse(name) + timedelta(minutes=2) >= datetime.now(tz=pytz.utc):
				OpenVAS.send_report(id)
			else:
				print("No reports found ", datetime.now(pytz.utc))
		sleep(10)
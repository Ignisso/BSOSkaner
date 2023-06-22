import os
import pytz
import dateutil.parser
from datetime import datetime, timedelta
from time import sleep
from openvaslib import OpenVAS as openvas
from os import environ

OpenVAS = openvas("localhost", 9390, "admin", "admin")
send_report = []

if __name__ == "__main__":
	while True:
		if not OpenVAS.is_connected():
			OpenVAS.reconnect()
		reports = OpenVAS.get_reports()

		for report in reports[:-4]:
			id = report.find("report").get("id")
			name = report.find("name").text
			status = report.find("report").find("scan_run_status").text

			if status == "Running" and id not in send_report:
				send_report.append(id)
				print(f"Waiting for report {id} to finish")
			if status == "Done" and id in send_report:
				OpenVAS.send_report(id)
				send_report.remove(id)
				print(f"Report {id} has been sent")
			else:
				print("No reports found ", datetime.now(pytz.utc))
		sleep(1)
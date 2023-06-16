import os
import pytz
import dateutil.parser
from datetime import datetime, timedelta
from time import sleep
from openvaslib import OpenVAS

OpenVAS = OpenVAS("192.168.0.227", 9390, "admin", "admin")

if __name__ == "__main__":
	while True:
		if not OpenVAS.is_connected():
			OpenVAS.reconnect()
		reports = OpenVAS.get_reports()

		for report in reports[:-4]: 
			id = report.find("report").get("id")
			name = report.find("name").text
			status = report.find("report").find("scan_run_status").text

			if status == "Done" and dateutil.parser.parse(name) + timedelta(minutes=6) >= datetime.now(tz=pytz.utc):
				OpenVAS.send_report(id)
		sleep(5 * 3600)
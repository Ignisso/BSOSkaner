import pytz

from base64 import b64decode
from config import Configuration
from datetime import datetime
from icalendar import Calendar, Event
from os import system

from gvm.connections import TLSConnection
from gvm.errors import GvmError
from gvm.protocols.gmpv224 import Gmp, ReportFormatType
from gvm.transforms import EtreeCheckCommandTransform
from gvm.xml import pretty_print as xml_print

class OpenVAS:

	def __init__(self, hostname, port, username, password):
		connection = TLSConnection(hostname=hostname, port=port)
		transform = EtreeCheckCommandTransform()
		
		self.config = Configuration()
		self.gmp = Gmp(connection=connection, transform=transform)
		self.gmp.authenticate(username, password)
			
		self.__update_all()

	def __xml_to_dict(self, xml): # What happens if count = 0
		dictionary = {}
		if len(xml) == 0 :
			return dictionary

		for val in xml:
			name = val.find("name").text
			id = val.get("id")
			dictionary[name] = id
		return dictionary

	def __update_all(self):
		self.__update_port_lists()
		self.__update_scan_configs()
		self.__update_scanners()
		self.__update_schedules()
		self.__update_targets()
		self.__update_tasks()
	
	def get_reports(self):
		return self.gmp.get_reports()

	def send_report(self, report_id):
		try:
			report = self.gmp.get_report(report_id, report_format_id = ReportFormatType.PDF)
			b64 = report.getchildren()[0].getchildren()[8].tail
			pdfdata = b64decode(b64)
			path = self.config.get_report_path()
			with open(path, "xb") as file:
				file.write(pdfdata)
				self.config.writeLog("Created new report: " + path)
			taskname = "XYZ" # task name
			tasktime = datetime.now()
			
			message = self.config.get_report_message(tasktime)
			subject = self.config.get_report_subject(taskname)
			mail = self.config.get_value("SendTo")
			system(f"echo \"{message}\" | mail -s \"{subject}\" -A \"{path}\" {mail}")
		except Exception as e:
			print(f"[ERR] An error occured while creating report {report_id}")
			print(e)

	def __update_port_lists(self):
		self.port_lists = self.__xml_to_dict(self.gmp.get_port_lists().getchildren()[:-4]) #UNTESTED
	def __update_scan_configs(self):
		self.scan_configs = self.__xml_to_dict(self.gmp.get_scan_configs().getchildren()[:-4])
	def __update_scanners(self):
		self.scanners = self.__xml_to_dict(self.gmp.get_scanners().getchildren()[:-4])
	def __update_schedules(self):
		self.tasks = self.__xml_to_dict(self.gmp.get_schedules().getchildren()[:-4]) #UNTESTED
	def __update_targets(self):
		self.targets = self.__xml_to_dict(self.gmp.get_targets().getchildren()[:-4])
	def __update_tasks(self):
		self.tasks = self.__xml_to_dict(self.gmp.get_tasks().getchildren()[1:-4])

	def create_port_list(self, name, port_range):
		try:
			self.gmp.create_port_list(name, port_range)
			self.__update_port_lists()
		except Exception as e:
			print("[ERR] An error occured while creating a port list")
			print(e)

	def get_port_lists(self):
		return self.gmp.get_port_lists()
	
	def delete_port_list(self, port_list_id):
		try:
			self.gmp.delete_port_list(port_list_id)
			self.__update_port_lists()
		except Exception as e:
			print(f"[ERR] An error occured while deleting port list {port_list_id}")
			print(e)
	
	def get_scan_configs(self):
		return self.gmp.get_scan_configs()
	
	def get_scanners(self):
		return self.gmp.get_scanners()

	def create_schedule(self, name, datetime_str, frequency=None, count=None, interval=None):
		try:
			cal = Calendar()
			cal.add("prodid", "-//Calendar//")
			cal.add("version", "2.0")
			event = Event()
			event.add("dtstamp", datetime.now(tz=pytz.timezone("Europe/Warsaw")))
			event.add("dtstart", datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S"))

			cal.add_component(event)

			self.gmp.create_schedule(name, cal.to_ical(), timezone="Europe/Warsaw")
			self.__update_schedules()
		except Exception as e:
			print(f"[ERR] An error occured while creating a schedule {name}")
			print(e)

	def delete_schedule(self, schedule_id):
		try:
			self.gmp.delete_schedule(schedule_id)
			self.__update_schedules()
		except Exception as e:
			print(f"[ERR] An error occured while deleting schedule {schedule_id}")
			print(e)

	def get_schedules(self):
		return self.gmp.get_schedules()

	def get_targets(self):
		return self.gmp.get_targets()
	
	def create_target(self, name, hosts, port_list_id):
		try:
			self.gmp.create_target(name, hosts=hosts, port_list_id=port_list_id)
			self.__update_targets()
		except Exception as e:
			print(f"[ERR] An error occured while creating a target {name}")
			print(e)

	def delete_target(self, target_id):
		try:
			self.gmp.delete_target(target_id)
			self.__update_targets()
		except Exception as e:
			print(f"[ERR] An error occured while deleting target {target_id}")
			print(e)

	def create_task(self, name, config_id, target_id, scanner_id):
		try:
			if name in self.tasks.keys():
				raise Exception("Error: Task already exists")
			self.gmp.create_task(name, config_id, target_id, scanner_id, schedule_id=schedule_id)
			self.__update_tasks()
		except Exception as e:
			print(f"[ERR] An error occured while creating a task {name}")
			print(e)
	
	def delete_task(self, task_id):
		try:
			self.gmp.delete_task(task_id)
			self.__update_tasks()
		except Exception as e:
			print(f"[ERR] An error occured while deleting task {task_id}")
			print(e)

	def get_tasks(self):
		return self.gmp.get_tasks()

	def start_task(self, task_id):
		self.gmp.start_task(task_id)

	def resume_task(self, task_id):
		self.gmp.resume_task(task_id)

	def stop_task(self, task_id):
		self.gmp.stop_task(task_id)

	def get_version(self):
		return self.gmp.get_version()

import json
from bcrypt import checkpw
from time import strftime
from datetime import datetime
from os import environ

CONFIG_FILE =  "/run/bsoskaner/config/config.cfg"
DEFAULT_CONFIG_FILE = "/run/bsoskaner/config/default.cfg"

class Configuration:
	def __init__(self):
		if (environ.get('RUNNING_IN_DOCKER') is not None):
			self.restore_defaults()
		with open(CONFIG_FILE, "r") as file:
			self.data = json.load(file)
		self.writeLog("Service started")
	
	def get_value(self, key):
		return self.data.get(key)

	def set_value(self, key, value):
		self.data[key] = value
		with open(CONFIG_FILE, "w") as file:
			json.dump(self.data, file, indent = 2)
		self.writeLog("Set " + key + " to " + value)

	def restore_defaults(self):
		with open(DEFAULT_CONFIG_FILE, "r") as file:
			self.data = json.load(file)
		with open(CONFIG_FILE, "w") as file:
			json.dump(self.data, file, indent = 2)
		self.writeLog("Restored default configuration")

	def login(self, password):
		with open(self.data["Password"], "rb") as file:
			if checkpw(password.encode("utf-8"), file.read()):
				self.writeLog("Successfully logged in")
				return True
		self.writeLog("Login failed")
		return False

	def get_report_path(self):
		filename = "Security Scan Report " + strftime("%y-%m-%d %H-%M-%S") + ".pdf"
		path = self.get_value("Reports") + filename
		return path

	def get_report_subject(self, task_name):
		return f"[BSOSKANER] Task {task_name} has been completed"

	def get_report_message(self, task_time):
		with open(self.get_value("MailTemplate"), "r") as file:
			message = file.read()
			
			for word in (("{MAIL}", self.get_value("SendFrom")),
			("{USERNAME}", self.get_value("Username")),
			("{MAIL}", self.get_value("SendFrom")),
			("{SCAN_CONFIG}", self.get_value("ScanType")),
			("{DATETIME}", str(task_time)),
			("{DURATION}", str(datetime.now() - task_time))):
				message = message.replace(*word)
			return message
	def writeLog(self, message):
		print(message)
		with open(self.data["Logfile"], "a") as file:
			file.write(strftime("%d.%m.%y %H:%M") + "\t" + message + "\n")

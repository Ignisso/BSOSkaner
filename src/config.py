import json
import os
from os import environ
from bcrypt import checkpw
from time import strftime
from datetime import datetime

CONFIG_FILE =  "/run/bsoskaner/config/config.cfg"
DEFAULT_CONFIG_FILE = "/run/bsoskaner/config/default.cfg"

DEBUG_CONFIG_FILE = "../config/debug.cfg"
DEBUG_DEFAULT_CONFIG_FILE = "../config/default.cfg"

if os.name == 'nt':
	CONFIG_FILE = DEBUG_CONFIG_FILE
	DEFAULT_CONFIG_FILE = DEBUG_DEFAULT_CONFIG_FILE

class Configuration:
	def __init__(self):
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
			
			duration = datetime.now() - datetime.strptime(task_time, "%Y-%m-%dT%H:%M:%SZ")
			text = ""
			if duration.days > 0:
				text = f"{duration.days}d {int(duration.seconds / 3600)}h {int(duration.seconds - int(duration.seconds / 3600) / 60)}m {duration.seconds % 60}s"
			elif duration.seconds > 3600:
				text = f"{duration.seconds / 3600}h {int(duration.seconds / 3600)}h {int(duration.seconds - int(duration.seconds / 3600) / 60)}m {duration.seconds % 60}"
			elif duration.seconds > 60:
				text = f"{int(duration.seconds - int(duration.seconds / 3600) / 60)}m {duration.seconds % 60}"
			else:
				text = f"{duration.seconds % 60}s"
			
			for word in (("{MAIL}", self.get_value("SendFrom")),
			("{USERNAME}", self.get_value("Username")),
			("{MAIL}", self.get_value("SendFrom")),
			("{DATETIME}", str(task_time).replace("T", " ")[:-1]),
			("{DURATION}", text)):
				message = message.replace(*word)
			return message

	def writeLog(self, message):
		print(message)
		with open(self.data["Logfile"], "a") as file:
			file.write(strftime("%d.%m.%y %H:%M") + "\t" + message + "\n")

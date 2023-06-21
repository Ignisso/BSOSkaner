from flask import *
from flask_session import *
from openvaslib import OpenVAS as openvas
from gvm.xml import pretty_print as xml_print
from datetime import datetime, timedelta
from os import environ
from config import Configuration
import bcrypt

app = Flask(__name__)
app.config["SESSION_PERMAMENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
config = Configuration()
OpenVAS = None
if (environ.get('RUNNING_IN_DOCKER') is not None):
    OpenVAS = openvas("localhost", 9390, "admin", "admin")
    if (environ.get('RUNNING_IN_DOCKER') is '1'):
        config.restore_defaults()
        environ['RUNNING_IN_DOCKER'] = '0'
else:
    OpenVAS = openvas("localhost", 9390, "admin", "admin")

@app.before_request
def before_request_func():
    if not OpenVAS.is_connected():
        OpenVAS.reconnect() 

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods = ["GET"])
def login_get():
    if session.get("username") != config.get_value("Username"):
        return render_template("login.html")
    else:
        return redirect("/tasks")

@app.route("/login", methods = ["POST"])
def login_post():
    if request.form["username"] == config.get_value("Username"):
        if config.login(request.form["password"]):
            session["username"] = config.get_value("Username")
            return redirect("/tasks")

    return render_template("login.html", error_text="No account found with the given credentials")

@app.route("/logout", methods = ["POST"])
def logout():
    session["username"] = None
    return redirect("/")

@app.route("/stoptask/<task_id>", methods = ["POST"])
def stoptask(task_id):
    if task_id in list(OpenVAS.tasks.values()):
        OpenVAS.stop_task(task_id)
    return redirect("/tasks")

@app.route("/starttask/<task_id>", methods = ["POST"])
def starttask(task_id):
    if task_id in list(OpenVAS.tasks.values()):
        OpenVAS.start_task(task_id)
    return redirect("/tasks")

@app.route("/resumetask/<task_id>", methods = ["POST"])
def resumetask(task_id):
    if task_id in list(OpenVAS.tasks.values()):
        OpenVAS.resume_task(task_id)
    return redirect("/tasks")

@app.route("/createtask", methods = ["POST"])
def createtask():
    OpenVAS.create_task(request.form["name"], request.form["config_id"], request.form["target_id"], request.form["scanner_id"], schedule_id=request.form["schedule_id"])
    return redirect("/tasks")

@app.route("/deletetask/<task_id>", methods = ["POST"])
def deletetask(task_id):
    if task_id in list(OpenVAS.tasks.values()):
        OpenVAS.delete_task(task_id)
    return redirect("/tasks")

@app.route("/tasks")
def tasks():
    if not session.get("username"):
        return redirect("/login")
    tasks = OpenVAS.get_tasks()

    tasksDTO = []
    for task in tasks[1:-4]: 
        id = task.get("id")
        name = task.find("name").text
        in_use = task.find("in_use").text
        status = task.find("status").text
        progress = task.find("progress").text
        report_count = task.getchildren()[16].text
        config = task.find("config").find("name").text
        target = task.find("target").find("name").text
        scanner = task.find("scanner").find("name").text
        schedule = task.find("schedule").find("name").text

        last_report = ""
        severity = ""
        warning = ""
        if(task.getchildren()[-3].tag == "last_report"):
            last_report = task.getchildren()[-3].getchildren()[0].getchildren()[0].text
            severity = task.getchildren()[-3].getchildren()[0].find("severity").text
            warning = task.getchildren()[-3].getchildren()[0].getchildren()[-2].find("warning").text
        tasksDTO.append({"id": id, "name": name, "in_use": in_use, "status": status, "progress": progress, "config": config, "target": target, "scanner": scanner, "schedule": schedule, "reports": report_count, "last_report": last_report, "severity": severity, "warning": warning})

    return render_template("tasks.html", tasks=tasksDTO, scan_configs=OpenVAS.scan_configs, targets=OpenVAS.targets, scanners=OpenVAS.scanners, schedules=OpenVAS.schedules)

@app.route("/createtarget", methods = ["POST"])
def createtarget():
    OpenVAS.create_target(request.form["name"], request.form["hosts"].split(";"), request.form["portlist_id"])
    return redirect("/targets")

@app.route("/deletetarget/<target_id>", methods = ["POST"])
def deletetarget(target_id):
    if target_id in list(OpenVAS.targets.values()):
        OpenVAS.delete_target(target_id)
    return redirect("/targets")

@app.route("/targets")
def targets():
    if not session.get("username"):
        return redirect("/login")
    targets = OpenVAS.get_targets()

    targetsDTO = []
    for target in targets[:-4]: 
        id = target.get("id")
        name = target.find("name").text
        in_use = target.find("in_use").text
        hosts = target.find("hosts").text
        max_hosts = target.find("max_hosts").text
        port_list = target.find("port_list").find("name").text

        targetsDTO.append({"id": id, "name": name, "in_use": in_use, "hosts": hosts, "max_hosts": max_hosts, "port_list": port_list})

    return render_template("targets.html", targets=targetsDTO, port_lists=OpenVAS.port_lists)

@app.route("/createportlist", methods = ["POST"])
def createportlist():
    print(request.form)
    ports = ""
    if "tcp" in request.form:
        if request.form["tcp"] != "":
            ports = ports + f'T:{request.form["tcp"]}'

    if "udp" in request.form:
        if request.form["udp"] != "":
            ports = ports + f'U:{request.form["udp"]}'

    print(ports)
    OpenVAS.create_port_list(request.form["name"], ports)
    return redirect("/portlists")

@app.route("/deleteportlist/<portlist_id>", methods = ["POST"])
def deleteportlist(portlist_id):
    if portlist_id in list(OpenVAS.port_lists.values()):
        OpenVAS.delete_port_list(portlist_id)
    return redirect("/portlists")

@app.route("/portlists")
def portlists():
    if not session.get("username"):
        return redirect("/login")
    port_lists = OpenVAS.get_port_lists()

    port_listsDTO = []
    for port_list in port_lists[:-4]: 
        id = port_list.get("id")
        name = port_list.find("name").text
        in_use = port_list.find("in_use").text
        tcp = port_list.find("port_count").getchildren()[1].text
        udp = port_list.find("port_count").getchildren()[2].text
        port_listsDTO.append({"id": id, "name": name, "in_use": in_use, "all": str(int(tcp)+int(udp)), "tcp": tcp, "udp": udp})

    return render_template("portlists.html", port_lists=port_listsDTO)

@app.route("/deletereport/<report_id>", methods = ["POST"])
def deletereport(report_id):
    OpenVAS.delete_report(report_id)
    return redirect("/reports")

@app.route("/downloadreport/<report_id>", methods = ["POST"])
def downloadreport(report_id):
    def stream_data(data):
        return OpenVAS.export_report(report_id)

    return stream_data(report_id), {"Content-Type": "file/pdf", "Content-Disposition": f"attachment; filename=\"Report-{report_id}.pdf\""}

@app.route("/deletehost/<host_id>", methods = ["POST"])
def deletehost(host_id):
    OpenVAS.delete_host(host_id)
    return redirect("/hosts")

@app.route("/hosts")
def hosts():
    if not session.get("username"):
        return redirect("/login")
    hosts = OpenVAS.get_hosts()

    nodes = []
    node_names = []
    edges = []
    hostsDTO = []
    for host in hosts[:-4]:
        id = host.get("id")
        name = host.find("name").text
        in_use = host.find("in_use").text
        severity = host.find("host").find("severity").find("value").text
        if severity == "" or severity is None:
            severity = "0.0"
        color = "grey"
        if float(severity) >= 7.0:
            color = "red"
        elif float(severity)  >= 4.0:
            color = "orange"
        elif float(severity) > 0.0:
            color = "blue"
        nodes.append({"id": host.find("name").text, "group": color})
        node_names.append(host.find("name").text)
        traceroute = ""
        if len(host.find("host").findall("detail")) > 0:
            traceroute = host.find("host").findall("detail")[-1].find("value").text
            for neighbour in traceroute.split(","):
                if neighbour not in node_names:
                    nodes.append({"id": neighbour, "group": "white"})
                
                edges.append({ "from": host.find("name").text, "to": neighbour})

                print({ "from": host.find("name").text, "to": neighbour}, flush=True)
        hostsDTO.append({"id": id, "name": name, "in_use": in_use, "traceroute": traceroute, "severity": severity})

    return render_template("hosts.html", hosts=hostsDTO, json={"nodes": nodes, "edges": edges})

@app.route("/reports")
def reports():
    if not session.get("username"):
        return redirect("/login")
    reports = OpenVAS.get_reports(filter_string="sort-reverse=date")

    reportsDTO = []
    for report in reports[:-4]:
        id = report.find("report").get("id")
        name = report.find("name").text
        task_name = report.find("task").find("name").text
        in_use = report.find("in_use").text
        status = report.find("report").find("scan_run_status").text
        progress = report.find("report").find("task").find("progress").text
        severity = report.find("report").find("severity").find("full").text
        reportsDTO.append({"id": id, "name": name, "in_use": in_use, "task_name": task_name, "status": status, "progress": progress, "severity": severity})

    return render_template("reports.html", reports=reportsDTO)


@app.route("/deleteschedule/<schedule_id>", methods = ["POST"])
def deleteschedule(schedule_id):
    OpenVAS.delete_schedule(schedule_id)
    return redirect("/schedules")

@app.route("/schedules")
def schedules():
    if not session.get("username"):
        return redirect("/login")
    schedules = OpenVAS.get_schedules()

    schedulesDTO = []
    for schedule in schedules[:-4]:
        id = schedule.get("id")
        name = schedule.find("name").text
        in_use = schedule.find("in_use").text
        dtstart = ""
        freq = ""
        interval = "1"
        icalendar = schedule.find("icalendar").text.split("\n")
        for prop in icalendar:
            if " 20" in prop:
                dtstart = datetime.strptime(prop[1:16], "%Y%m%dT%H%M%S") + timedelta(hours=2)
            if "DTSTART" in prop and "DTSTART;" not in prop:
                dtstart = datetime.strptime(prop[8:23], "%Y%m%dT%H%M%S") + timedelta(hours=2)
            if "RRULE" in prop:
                rrule = prop
                rrule = rrule.split(":")[1].split(";")
                for rule in rrule:
                    if "FREQ" in rule:
                        freq = rule[5:]
                    if "INTERVAL" in rule:
                        interval = rule[9:]
            if "DURATION:PT0S" in prop:
                freq = ""
        repeat = ""
        if not (freq == "" or interval == ""):
            if freq == "DAILY":
                if interval == "1":
                    repeat = f"Every {interval} DAY"
                else:
                    repeat = f"Every {interval} DAYS"
                    
            elif interval == "1":
                repeat = f"Every {interval} {freq[:-2]}"
            else:
                repeat = f"Every {interval} {freq[:-2]}S"
        schedulesDTO.append({"id": id, "name": name, "in_use": in_use, "dtstart": dtstart, "repeat": repeat})

    return render_template("schedules.html", schedules=schedulesDTO)


@app.route("/createschedule", methods = ["POST"])
def createschedule():
    frequency = "ONCE"
    interval=0
    until=None
    if "recurrence" in request.form:
        frequency = request.form["recurrence"]
    if "interval" in request.form and frequency != "ONCE":
        interval = int(request.form["interval"])
    if "end" in request.form:
        until = request.form["end"]
    print(request.form, until)
    OpenVAS.create_schedule(request.form["name"], request.form["start"], frequency=frequency, interval=interval, until=until)
    return redirect("/schedules")

@app.route("/settings")
def settings():
    if not session.get("username"):
        return redirect("/login")

    MailTemplate = None   
    with open(config.get_value("MailTemplate"), "r") as file:
        MailTemplate = file.read()
     
    return render_template("settings.html", SendTo=config.get_value("SendTo"), Username=config.get_value("Username"), MailTemplate=MailTemplate)

@app.route("/savesettings", methods = ["POST"])
def savesettings():
    SendTo = None
    if "SendTo" in request.form:
        if request.form["SendTo"] != config.get_value("SendTo"):
            config.set_value("SendTo", request.form["SendTo"])
    
    if "Username" in request.form:
        if request.form["Username"] != config.get_value("Username"):
            config.set_value("Username", request.form["Username"])

    if "MailTemplate" in request.form:
        fileContent = None
        with open(config.get_value("MailTemplate"), "r") as file:
            fileContent = file.read()

        if fileContent != request.form["MailTemplate"]:
            print(request.form["MailTemplate"])
            with open(config.get_value("MailTemplate"), "wb") as file:
                file.write(request.form["MailTemplate"].encode("utf-8"))

    if "Password" in request.form:
        if request.form["Password"] != "":
            with open(config.get_value("Password"), "wb") as file:
                file.write(bcrypt.hashpw(request.form["Password"].encode("utf-8"), bcrypt.gensalt()))

    return redirect("/schedules")


if __name__ == "__main__":
    if os.name == 'nt':
        app.run(debug=True, port=5001)
    else:
        app.run(debug=False, port=5000)
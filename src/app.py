from flask import *
from flask_session import *
from openvaslib import OpenVAS
from gvm.xml import pretty_print as xml_print

app = Flask(__name__)
app.config["SESSION_PERMAMENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
OpenVAS = OpenVAS("192.168.0.227", 9390, "admin", "admin")    

@app.before_request
def before_request_func():
    if not OpenVAS.is_connected():
        OpenVAS.reconnect() 
        
@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods = ["GET"])
def login_get():
    if not session.get("username"):
        return render_template("login.html")
    else:
        return redirect("/tasks")

@app.route("/login", methods = ["POST"])
def login_post():
    if request.form["username"] == "admin" and request.form["password"] == "admin":
        session["username"] = "admin"
        return redirect("/tasks")
    else:
        return render_template("login.html", error_text="No account found with the given credentials")

@app.route("/logout", methods = ["POST"])
def logout():
    session["username"] = None
    return redirect("/tasks")

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
    OpenVAS.create_task(request.form["name"], request.form["config_id"], request.form["target_id"], request.form["scanner_id"])
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
        last_report = ""
        severity = ""
        warning = ""
        if(task.getchildren()[-3].tag == "last_report"):
            last_report = task.getchildren()[-3].getchildren()[0].getchildren()[0].text
            severity = task.getchildren()[-3].getchildren()[0].find("severity").text
            warning = task.getchildren()[-3].getchildren()[0].getchildren()[-2].find("warning").text
        tasksDTO.append({"id": id, "name": name, "in_use": in_use, "status": status, "progress": progress, "reports": report_count, "last_report": last_report, "severity": severity, "warning": warning})

    return render_template("tasks.html", tasks=tasksDTO, scan_configs=OpenVAS.scan_configs, targets=OpenVAS.targets, scanners=OpenVAS.scanners)

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

        targetsDTO.append({"id": id, "name": name, "in_use": in_use, "hosts": hosts, "max_hosts": max_hosts})

    return render_template("targets.html", targets=targetsDTO, port_lists=OpenVAS.port_lists)

@app.route("/createportlist", methods = ["POST"])
def createportlist():
    OpenVAS.create_port_list(request.form["name"], request.form["ports"])
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

    hostsDTO = []
    for host in hosts[:-4]:
        id = host.get("id")
        name = host.find("name").text
        in_use = host.find("in_use").text
        severity = host.find("host").find("severity").find("value").text
        traceroute = ""
        if len(host.find("host").findall("detail")) > 0:
            traceroute = host.find("host").findall("detail")[-1].find("value").text
        hostsDTO.append({"id": id, "name": name, "in_use": in_use, "traceroute": traceroute, "severity": severity})

    return render_template("hosts.html", hosts=hostsDTO)

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

@app.route("/settings")
def settings():
    if not session.get("username"):
        return redirect("/login")

    return render_template("settings.html")



if __name__ == "__main__":
    app.run(debug=True)
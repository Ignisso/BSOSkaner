from datetime import datetime
from openvaslib import OpenVAS
from gvm.xml import pretty_print as xml_print

OpenVAS = OpenVAS("localhost", 9390, "admin", "admin")
#OpenVAS.create_port_list("TCP&UDP 1024 Ports", "T: 1-1024, U: 1-1024")
#OpenVAS.create_target("Localhost", ["192.168.0.227"], OpenVAS.port_lists["TCP&UDP 1024 Ports"])
#OpenVAS.create_task("Localhost Scan", OpenVAS.scan_configs["Base"], OpenVAS.targets["Localhost"], OpenVAS.scanners["OpenVAS Default"])
#OpenVAS.start_task(OpenVAS.tasks["Localhost Scan"])

for schedule in OpenVAS.get_schedules()[:-4]: 
    print(schedule.get("id"))
    icalendar = schedule.find("icalendar").text.split("\n")
    print(icalendar)
    for property in icalendar:
        if "DTSTART" in property:
            print(property)
        if "RRULE" in property:
            print(property)

from openvaslib import OpenVAS
from gvm.xml import pretty_print as xml_print

OpenVAS = OpenVAS("192.168.0.227", 9390, "admin", "admin")
#OpenVAS.create_port_list("TCP&UDP 1024 Ports", "T: 1-1024, U: 1-1024")
#OpenVAS.create_target("Localhost", ["192.168.0.227"], OpenVAS.port_lists["TCP&UDP 1024 Ports"])
#OpenVAS.create_task("Localhost Scan", OpenVAS.scan_configs["Base"], OpenVAS.targets["Localhost"], OpenVAS.scanners["OpenVAS Default"])
#OpenVAS.start_task(OpenVAS.tasks["Localhost Scan"])
#xml_print(OpenVAS.get_schedules())
OpenVAS.send_report("8f2e22ac-d94b-4883-a531-b2c4ccb7c010")

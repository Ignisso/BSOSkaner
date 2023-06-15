from openvaslib import OpenVAS
from gvm.xml import pretty_print as xml_print

OpenVAS = OpenVAS("192.168.0.227", 9390, "admin", "admin")
#OpenVAS.create_port_list("TCP&UDP 1024 Ports", "T: 1-1024, U: 1-1024")
#OpenVAS.create_target("Localhost", ["192.168.0.227"], OpenVAS.port_lists["TCP&UDP 1024 Ports"])
#OpenVAS.create_task("Localhost Scan", OpenVAS.scan_configs["Base"], OpenVAS.targets["Localhost"], OpenVAS.scanners["OpenVAS Default"])
#OpenVAS.start_task(OpenVAS.tasks["Localhost Scan"])

#OpenVAS.create_schedule("Test", "2023-06-14 21:15:00")
for c in OpenVAS.get_tasks().getchildren()[1:-4]:
	print(c.getchildren()[-3].tag)

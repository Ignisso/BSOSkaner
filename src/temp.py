from openvaslib import OpenVAS
from gvm.xml import pretty_print as xml_print

OpenVAS = OpenVAS("192.168.0.227", 9390, "admin", "admin")
#OpenVAS.create_port_list("TCP&UDP 1024 Ports", "T: 1-1024, U: 1-1024")
#OpenVAS.create_target("Localhost", ["192.168.0.227"], OpenVAS.port_lists["TCP&UDP 1024 Ports"])
#OpenVAS.create_task("Localhost Scan", OpenVAS.scan_configs["Base"], OpenVAS.targets["Localhost"], OpenVAS.scanners["OpenVAS Default"])
#OpenVAS.start_task(OpenVAS.tasks["Localhost Scan"])
hosts = OpenVAS.get_hosts()

for host in hosts[:-4]:
    print(host.get("id"))
    print(host.find("name").text)
    print(host.find("in_use").text)
    print(host.find("host").find("severity").find("value").text)
    xml_print(host.find("host").findall("detail"))
import xml.etree.ElementTree as ET


class ExperimentSettings:
    def __init__(self):
        self.name = ""
        self.pcap = ""
        self.out_dir = ""
        self.client_capture_if = ""
        self.server_capture_if = ""
        self.display_mininet_cli = False
        self.tcpdump_start_delay = 0
        self.tcpdump_stop_delay = 0
        self.verbose = False
        self.log_file = ""

    @staticmethod
    def from_xml(xml_file):
        experiments_settings = []

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for experiment_elem in root.findall("experiment"):
                experiment_settings = ExperimentSettings()
                experiment_settings.name = experiment_elem.find("name").text
                experiment_settings.pcap = experiment_elem.find("pcap").text
                experiment_settings.out_dir = experiment_elem.find("out_dir").text
                experiment_settings.client_capture_if = experiment_elem.find("client_capture_if").text
                experiment_settings.server_capture_if = experiment_elem.find("server_capture_if").text
                experiment_settings.display_mininet_cli = experiment_elem.find("display_mininet_cli").text.lower() == "true"
                experiment_settings.tcpdump_start_delay = int(experiment_elem.find("tcpdump_start_delay").text)
                experiment_settings.tcpdump_stop_delay = int(experiment_elem.find("tcpdump_stop_delay").text)
                experiment_settings.verbose = experiment_elem.find("verbose").text.lower() == "true"
                experiment_settings.log_file = experiment_elem.find("log_file").text

                experiments_settings.append(experiment_settings)

        except Exception as e:
            print(f"Error parsing XML: {e}")

        return experiments_settings


if __name__ == '__main__':
    experiments_settings = ExperimentSettings.from_xml("sample.xml")
    for exp_sett in experiments_settings:
        print(f"Experiment Name: {exp_sett.name}")
        print(f"Verbose: {exp_sett.verbose}")


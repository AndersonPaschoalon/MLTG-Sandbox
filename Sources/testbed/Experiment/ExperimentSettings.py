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
        self.network_loss = 0.01
        self.network_delay = '20ms'
        self.run_capture = True
        self.run_jitter = True

    def run(self):
        print("TODO")

    @staticmethod
    def run_all(experiment_list):
        print("TODO")

    @staticmethod
    def from_xml(xml_file):
        experiment_list = ExperimentSettings()

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for experiment_elem in root.findall("experiment"):
                experiment = ExperimentSettings()
                # Experiment Configuration
                experiment.name = experiment_elem.find("name").text
                experiment.pcap = experiment_elem.find("pcap").text
                experiment.out_dir = experiment_elem.find("out_dir").text
                experiment.display_mininet_cli = experiment_elem.find("display_mininet_cli").text.lower() == "true"
                experiment.verbose = experiment_elem.find("verbose").text.lower() == "true"
                experiment.log_file = experiment_elem.find("log_file").text
                # Network configuration
                experiment.tcpdump_start_delay = int(experiment_elem.find("tcpdump_start_delay").text)
                experiment.tcpdump_stop_delay = int(experiment_elem.find("tcpdump_stop_delay").text)
                experiment.client_capture_if = experiment_elem.find("client_capture_if").text
                experiment.server_capture_if = experiment_elem.find("server_capture_if").text
                experiment.network_loss = int(experiment_elem.find("network_loss").text)
                experiment.network_delay = experiment_elem.find("network_delay").text
                # Tests configuration
                experiment.run_capture = experiment_elem.find("run_capture").text.lower() == "true"
                experiment.run_jitter = experiment_elem.find("run_jitter").text.lower() == "true"

                experiment_list.append(experiment)

        except Exception as e:
            print(f"Error parsing XML: {e}")

        return experiment_list


if __name__ == '__main__':
    experiments_settings = ExperimentSettings.from_xml("sample.xml")
    for exp_sett in experiments_settings:
        print(f"Experiment Name: {exp_sett.name}")
        print(f"Verbose: {exp_sett.verbose}")


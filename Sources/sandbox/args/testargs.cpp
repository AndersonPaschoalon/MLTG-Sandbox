#include <unistd.h>
#include <getopt.h>
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    std::string type = "live";
    std::string src = "";
    int timeout = -1;
    int maxpackets = -1;
    std::string lib = "libpcap";
    std::string name = "";
    bool show = false;
    bool version = false;
    bool help = false;
	bool unitytests = false;

    // Define the options
    struct option long_options[] = {
        {"type", required_argument, 0, 'y'},
        {"src", required_argument, 0, 's'},
        {"timeout", required_argument, 0, 't'},
        {"maxpackets", required_argument, 0, 'm'},
        {"lib", required_argument, 0, 'l'},
        {"name", required_argument, 0, 'n'},
        {"show", no_argument, 0, 'w'},
        {"version", no_argument, 0, 'v'},
        {"help", no_argument, 0, 'h'},
		{"unitytests", no_argument, 0, 'u'},
        {0, 0, 0, 0}
    };

    // Parse the options
    int option_index = 0;
    int c;
    while ((c = getopt_long(argc, argv, "y:s:t:m:l:n:wvhu", long_options, &option_index)) != -1) {
        switch (c) {
            case 'y':
                type = optarg;
                break;
            case 's':
                src = optarg;
                break;
            case 't':
                timeout = std::stoi(optarg);
                break;
            case 'm':
                maxpackets = std::stoi(optarg);
                break;
            case 'l':
                lib = optarg;
                break;
            case 'n':
                name = optarg;
                break;
            case 'w':
				show = true;
            case 'u':
				unitytests = true;				
                break;
            case 'v':
                version = true;
                break;
            case 'h':
                help = true;
                break;
            default:
                std::cerr << "Invalid option: " << optarg << std::endl;
                return 1;
        }
    }

    // Print the values of the variables
    std::cout << "type = " << type << std::endl;
    std::cout << "src = " << src << std::endl;
    std::cout << "timeout = " << timeout << std::endl;
    std::cout << "maxpackets = " << maxpackets << std::endl;
    std::cout << "lib = " << lib << std::endl;
    std::cout << "name = " << name << std::endl;
    std::cout << "show = " << std::boolalpha << show << std::endl;
    std::cout << "version = " << std::boolalpha << version << std::endl;
    std::cout << "help = " << std::boolalpha << help << std::endl;
	std::cout << "unitytests = " << std::boolalpha << unitytests << std::endl;

    return 0;
}
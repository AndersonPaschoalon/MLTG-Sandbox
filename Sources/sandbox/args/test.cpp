#include <iostream>
#include <fstream>
#include <cstdlib>
#include <filesystem>



int main()
{
    std::filesystem::current_path(std::filesystem::temp_directory_path());
    std::filesystem::create_directories("sandbox/1/2/a");
    std::filesystem::create_directory("sandbox/1/2/b");
    std::filesystem::permissions("sandbox/1/2/b", fs::perms::others_all, fs::perm_options::remove);
    std::filesystem::create_directory("sandbox/1/2/c", "sandbox/1/2/b");
    std::system("ls -l sandbox/1/2");
    std::system("tree sandbox");
    std::filesystem::remove_all("sandbox");
}


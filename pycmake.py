import os
import shutil
import subprocess
from typing import List, Dict, Any

class CMakeConfig:
    def __init__(self, cmake_version: str, module_name: str, build_type: str = 'DEBUG'):
        self.cmake_version = cmake_version
        self.module_name = module_name
        self.build_type = build_type
        
        self.config = {
            "CMAKE_CXX_STANDARD": "17",
            "CMAKE_CXX_STANDARD_REQUIRED": "ON",
            "CMAKE_C_STANDARD": "17",
            "CMAKE_C_STANDARD_REQUIRED": "ON",
            "CMAKE_POSITION_INDEPENDENT_CODE": "ON",
            "CMAKE_CURRENT_BINARY_DIR": "../build",
            "CMAKE_CURRENT_SOURCE_DIR": "../src",
            "CMAKE_LIBRARY_PATH": "lib",
            "EXECUTABLE_OUTPUT_PATH": "../build/output/bin",
            "LIBRARY_OUTPUT_PATH": "../build/output/lib",
            "CMAKE_BUILD_TYPE": build_type,
            "CMAKE_INSTALL_PREFIX": "../build",
            # "CMAKE_C_FLAGS": '',
            # "CMAKE_CXX_FLAGS": ''
            }
        
        build_lv = '-O0 '
        if self.build_type == 'RELEASE':
            build_lv = '-O2 '
        
        gnu_warn_str_ = "-Werror -Wall -Wextra -Wshadow -Wno-unused-parameter -Wno-unused-variable -Wno-unused-but-set-variable "
        gnu_f_str_ = "-fPIC -pthread -fno-strict-aliasing -fno-delete-null-pointer-checks -fno-strict-overflow -fsigned-char "
        self.gnu_c_str_ = '-std=gnu17 -ggdb3 ' + build_lv + gnu_warn_str_ + gnu_f_str_
        self.gnu_cpp_str_ = '-std=gnu++17 -ggdb3 ' + build_lv + gnu_warn_str_ + gnu_f_str_
        
        msvc_warn_str_ = "/W4 /WX "
        msvc_f_str_ = "/MD /EHsc /GR "
        self.msvc_c_str_ = '/std:c17 /Zi ' + msvc_warn_str_ + msvc_f_str_
        self.msvc_cpp_str_ = '/std:c++17 /Zi ' + msvc_warn_str_ + msvc_f_str_
        
        # self.config['CMAKE_C_FLAGS'] = msvc_c_str_
        # self.config['CMAKE_CXX_FLAGS'] = msvc_cpp_str_

    def generate_compile_config(self):
        """Generate CMake commands for compile configurations."""
        return f"""
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {self.gnu_cpp_str_}")
    set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} {self.gnu_c_str_}")
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {self.msvc_cpp_str_}")
    set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} {self.msvc_c_str_}")
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {self.msvc_cpp_str_}")
    set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} {self.msvc_c_str_}")
endif()
        """

    def get_cmake_cmd_list(self) -> List[str]:
        """Generate a list of CMake commands from the configuration."""
        cmd_list = [
            f"cmake_minimum_required(VERSION {self.cmake_version})",
            f"project({self.module_name})"
        ]
        cmd_list.extend(self._generate_set_commands())
        return cmd_list

    def _generate_set_commands(self) -> List[str]:
        """Generate 'set' commands for all configuration variables."""
        return [f"set({key} {value})" for key, value in self.config.items()]

    def update_config(self, key: str, value: Any):
        """Update a configuration variable."""
        self.config[key] = value

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration dictionary."""
        return self.config

def get_lib_paths(base_directory: str):
    """
    Get lists of include paths and library paths under the given base directory.
    """
    include_paths = []
    lib_paths = []
    for root, dirs, files in os.walk(base_directory):
        if os.path.basename(root) == 'include':
            include_paths.append(root.replace("\\", "/"))
        elif os.path.basename(root) == 'lib':
            for file in files:
                if file.endswith(('.a', '.lib', '.so', '.dll')):
                    lib_paths.append(os.path.join(root, os.path.splitext(file)[0]).replace("\\", "/"))
    return include_paths, lib_paths

def generate_compile_target(target_name: str, target_type: str, library_list: List[str], library_dir: str, extend_src: List[str]) -> List[str]:
    """Generate CMake commands for a compile target."""
    cmd_list = []
    cmd_list.append(f"link_directories({library_dir})")
    target_type_cmd = {
        "bin": "add_executable",
        "slib": "add_library",
        "dlib": "add_library"
    }
    target_cmd = target_type_cmd.get(target_type, "add_executable")
    target_str = f"{target_name} {'SHARED' if target_type == 'dlib' else ''} {' '.join(extend_src)} ${{src_list}}"
    cmd_list.append(f"{target_cmd}({target_str})")
    if library_list:
        cmd_list.append(f"target_link_libraries({target_name} {' '.join(library_list)})")
    return cmd_list

def get_cpp_files(directory: str) -> List[str]:
    """Get a list of C++ files in the given directory."""
    cpp_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.cpp'):
                cpp_files.append(os.path.join(root, file))
    cpp_files = [src.replace("\\", "/") for src in cpp_files]
    return cpp_files


def generate_targets_from_test_dir(test_dir: str, src_str:str, include_str:str, lib_str:str) -> List[str]:
    """Generate CMake targets for each subdirectory in the test directory."""
    targets = []
    for subdir in os.listdir(test_dir):
        subdir_path = os.path.join(test_dir, subdir)
        if os.path.isdir(subdir_path):
            target_name = f"test_{subdir}"
            test_files = get_cpp_files(subdir_path)
            test_files_str = " ".join([src.replace("\\", "/") for src in test_files])
            targets.append(f"add_executable({target_name} {test_files_str} {src_str})")
            targets.append(f"target_include_directories({target_name} PRIVATE {include_str})")
            targets.append(f"target_link_libraries({target_name} PRIVATE {lib_str})")
    return targets


def generate_cmakelist(build_type: str, cmake_version: str, module_name: str, module_type: str, with_test = True) -> str:
    """Generate the CMakeLists.txt content."""
    library_dir = "../lib"
    extend_src = get_cpp_files("../src")
    extend_src = [src.replace("\\", "/") for src in extend_src]
    
    library_pair = get_lib_paths(library_dir)
    # print(library_pair)
    include_paths = library_pair[0]
    library_list = library_pair[1]

    cmake_config = CMakeConfig(cmake_version, module_name, build_type)
    cmake_settings = cmake_config.get_cmake_cmd_list() + [cmake_config.generate_compile_config()]
    target_settings = generate_compile_target(module_name, module_type, library_list, library_dir, extend_src)
    
    if with_test:
        extend_test = generate_targets_from_test_dir("../test", ' '.join(extend_src), ''.join(include_paths), ''.join(library_list))
        return "\n".join(cmake_settings + ["\n"] + target_settings + ["\n"] + extend_test)
    else:
        return "\n".join(cmake_settings + ["\n"] + target_settings + ["\n"])

def mk_parse_key_value(content):
    data_dict = {}
    content = content.replace('\\\n', '')
    # content = content.replace('    ', ' ')
    content = content.replace('\t', ' ')
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if ':=' in line:
            key, value = line.split(':=', 1)
            data_dict[key.strip()] = value.strip()
    return data_dict

def cmake_build(build_type = "DEBUG", with_test = True):
    proj_dict = {}
    with open('project_defs.mk', 'r') as file:
        print("----- Start Parse Project Settings -----")
        content = file.read()
        proj_dict = mk_parse_key_value(content)

    if not os.path.exists("build/"):
        os.makedirs("build/")
    os.chdir("build/")
    
    cmakelist_str = generate_cmakelist(build_type, proj_dict["CMAKE_VERSION"], proj_dict["MODULE_NAME"], proj_dict["MODULE_TYPE"], with_test)
    with open("CMakeLists.txt", "w") as file:
        file.write(cmakelist_str)

    print("----- Start CMake Build -----")
    subprocess.run(["cmake", "-B ."], check=True)
    subprocess.run(["cmake", "--build", "."], check=True)

def auto_test(directory_path = "/output/bin"):
    test_results = []
    print("----- Start Auto Test -----")
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                if not file_path.lower().endswith('.pdb'):
                    try:
                        print(f"----- Test: {file_path} -----")
                        result = subprocess.run(file_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        output_str = result.stdout.decode('utf-8')
                        print(output_str)
                        test_results.append((file_path, output_str))
                    except subprocess.CalledProcessError as err:
                        print(f"Error running {file_path}: {err}")
                    except Exception as e:
                        print(f"Unexpected error running {file_path}: {e}")

    return test_results

if __name__ == "__main__":
    cmake_build("release", True)
    auto_test("output/bin")
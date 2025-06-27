import os
import shutil
import subprocess
import sys
from typing import List, Dict, Any
import configparser

class CMakeConfig:
    class MyConfigParser(configparser.ConfigParser):
        def optionxform(self, optionstr: str) -> str:
            return optionstr  # 保持大小写
    def __init__(self, config_file_path: str, build_type: str = 'DEBUG'):
        config = self.MyConfigParser()
        config.read(config_file_path)

        self.cmake_version = config.get('project_config', 'CMAKE_VERSION')
        self.module_name = config.get('project_config', 'MODULE_NAME')
        self.module_type = config.get('project_config', 'MODULE_TYPE')
        self.build_type = build_type

        self.config = dict(config.items('cmake_config'))
        self.config['CMAKE_BUILD_TYPE'] = self.build_type

        build_lv = config.get('cmake_compile_flags', self.build_type.upper()) + ' '

        c_compile_str = config.get('cmake_compile_flags', 'c_compile_str') + ' '
        cpp_compile_str = config.get('cmake_compile_flags', 'cpp_compile_str') + ' '
        gnu_warn_str_ = config.get('cmake_compile_flags', 'warn_str') + ' '
        gnu_f_str_ = config.get('cmake_compile_flags', 'f_str') + ' '

        self.c_str_ = c_compile_str + build_lv + gnu_warn_str_ + gnu_f_str_
        self.cpp_str_ = cpp_compile_str + build_lv + gnu_warn_str_ + gnu_f_str_
        self.test_str_ = config.get('cmake_compile_flags', 'test_path_str')


    def generate_compile_config(self):
        return f"""
set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {self.cpp_str_}")
set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} {self.c_str_}")
    """
#         """Generate CMake commands for compile configurations."""
#         return f"""
# if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
#     set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {self.gnu_cpp_str_}")
#     set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} {self.gnu_c_str_}")
# elseif(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
#     set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {self.msvc_cpp_str_}")
#     set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} {self.msvc_c_str_}")
# elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
#     set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {self.msvc_cpp_str_}")
#     set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} {self.msvc_c_str_}")
# endif()
#         """

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
                if file.endswith(('.lib', '.dll')):
                    lib_paths.append(os.path.join(root, os.path.splitext(file)[0]).replace("\\", "/"))
                elif file.endswith(('.a', '.so')):
                    lib_paths.append(os.path.join(root, file).replace("\\", "/"))
    return include_paths, lib_paths

def generate_compile_target(target_name: str, target_type: str, library_list: List[str], library_dir: str, extend_src: List[str]) -> List[str]:
    """Generate CMake commands for a compile target."""
    cmd_list = []
    cmd_list.append(f"link_directories(${{CMAKE_SOURCE_DIR}}/{library_dir})")
    target_type_cmd = {
        "bin": "add_executable",
        "slib": "add_library",
        "dlib": "add_library"
    }
    target_cmd = target_type_cmd.get(target_type, "add_executable")
    target_str = f"{target_name} {'SHARED' if target_type == 'dlib' else ''} {' '.join(extend_src)} ${{src_list}}"
    cmd_list.append(f"{target_cmd}({target_str})")
    if library_list:
        cmd_list.append(f"target_link_libraries({target_name} ${{CMAKE_SOURCE_DIR}}/{' ${CMAKE_SOURCE_DIR}/'.join(library_list)})")
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


def generate_cmakelist(config_file_path: str, build_type: str, with_test = True) -> str:
    """Generate the CMakeLists.txt content."""
    cmake_config = CMakeConfig(config_file_path, build_type)
    library_dir = cmake_config.get_config().get('CMAKE_LIBRARY_PATH', '../lib')
    extend_src = get_cpp_files(cmake_config.get_config().get('CMAKE_CURRENT_SOURCE_DIR', '../src'))
    extend_src = [src.replace("\\", "/") for src in extend_src]
    library_pair = get_lib_paths(library_dir)
    include_paths = library_pair[0]
    library_list = library_pair[1]

    cmake_settings = cmake_config.get_cmake_cmd_list() + [cmake_config.generate_compile_config()]
    target_settings = generate_compile_target(cmake_config.module_name, cmake_config.module_type, library_list, library_dir, extend_src)
    
    if with_test:
        extend_test = generate_targets_from_test_dir(cmake_config.test_str_, ' '.join(extend_src), 
                                                     '${CMAKE_SOURCE_DIR}/'+' ${CMAKE_SOURCE_DIR}/'.join(include_paths), 
                                                     '${CMAKE_SOURCE_DIR}/'+' ${CMAKE_SOURCE_DIR}/'.join(library_list))
        return "\n".join(cmake_settings + ["\n"] + target_settings + ["\n"] + extend_test)
    else:
        return "\n".join(cmake_settings + ["\n"] + target_settings + ["\n"])


def cmake_build(config_file_path, build_type = "DEBUG", with_test = True):

    if not os.path.exists("build/"):
        os.makedirs("build/")
    os.chdir("build/")
    
    cmakelist_str = generate_cmakelist("../"+config_file_path, build_type, with_test)
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

def parse_flag():
    build_type_flags = ['DEBUG', 'RELEASE', 'RELWITHDEBINFO', 'MINSIZEREL']
    stage = ['BUILD', 'TEST']
    if len(sys.argv) >= 2 and sys.argv[1].upper() == "CLEAN":
        if os.path.exists("build/"):
            shutil.rmtree("build/")
        print("----- clean build -----")
        exit()
    if len(sys.argv) == 3:
        if sys.argv[1].upper() in build_type_flags and sys.argv[2].upper() in stage:
            return sys.argv[1].upper(), sys.argv[2].upper()
        else:
            print("err: build_type/stage not found!")
            exit()
    return 'DEBUG', 'TEST'

if __name__ == "__main__":
    config_file_path = "pycmake_config.ini"
    if not os.path.exists(config_file_path):
        print(f"Configuration file '{config_file_path}' not found.")
        exit(1)
    flags = parse_flag()
    build_type_f = flags[0]
    if flags[1] != "TEST":
        cmake_build(config_file_path, build_type_f, False)
    else:
        cmake_build(config_file_path, build_type_f, True)
        auto_test("output/bin")
import os
import subprocess
import sys
import shutil

import cmake_py.pre_process
import cmake_py.post_process
import cmake_py.pycmake
import cmake_py.compile_settings


def parse_key_value(content):
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

def parse_flag():
    build_type_flags = ['DEBUG', 'RELEASE', 'RELWITHDEBINFO', 'MINSIZEREL']
    if len(sys.argv) == 2:
        if sys.argv[1].upper() == "CLEAN":
             if os.path.exists("build/"):
                shutil.rmtree("build/")
                print("----- clean build -----")
                exit()
        elif sys.argv[1].upper() in build_type_flags:
            return sys.argv[1].upper()
        else:
            print("err: build_type not found!")
            exit()
    return 'DEBUG'


if __name__ == "__main__":

    print("***----- Start Cmake Python -----***")
    build_type_f = parse_flag()

    # prepare process
    cmake_py.pre_process.run()

    # init
    cmake_lines_project = []
    project_defs_dict = {}
    lib_list = []

    if not os.path.exists("build/"):
        os.makedirs("build/")
    if not os.path.exists("build/lib/"):
        shutil.copytree("lib", "build/lib/")

    # make lines of CMakeLists

    ### read project_defs.mk
    with open('project_defs.mk', 'r') as file:
        print("----- Start Parse Project Settings -----")
        content = file.read()
        project_defs_dict = parse_key_value(content)
        lib_list = project_defs_dict["MODULE_DEPEND_LIB"].split()

        for key,value in project_defs_dict.items():
            print("    " + str(key) + ": " + str(value))
        if not project_defs_dict["MODULE_TYPE"] in ["bin", "slib", "dlib"]:
            print("ERR: MODULE_TYPE is invalid!")
            exit()

    os.chdir("build/")

    ### make proj_env
    proj_env = cmake_py.pycmake.project_env(project_defs_dict["CMAKE_VERSION"], project_defs_dict["MODULE_NAME"])
    cmake_lines_project.extend(proj_env.get_cmake_cmd_list())
    cmake_lines_project.append('')

    ### make cmake_settings
    cmake_settings = cmake_py.compile_settings.generate_compile_settings(build_type_f)
    cmake_lines_project.extend(cmake_settings)
    cmake_lines_project.append('')

    ### make dir_env
    dir_env = cmake_py.pycmake.directory_env(lib_list)
    cmake_lines_project.extend(dir_env.get_cmake_cmd_list())
    cmake_lines_project.append('')

    ### set make target
    make_target = cmake_py.pycmake.compile_target(\
                    project_defs_dict["MODULE_NAME"], project_defs_dict["MODULE_TYPE"], \
                    lib_list, dir_env.library_path, '')
    cmake_lines_project.extend(make_target.get_cmake_cmd_list())
    cmake_lines_project.append('')

    ### set testcases
    if project_defs_dict["MODULE_TYPE"] in ["slib", "dlib"]:
        cmake_lines_project.append('set(EXECUTABLE_OUTPUT_PATH "../build/output/test")\n')
        test_files = cmake_py.pycmake.get_cpp_files("../test/")
        for test_file in test_files:
            test_file = test_file.replace('\\','/')
            test_name = "test_" + test_file.split("/")[2]
            make_target_test = cmake_py.pycmake.compile_target(test_name, 'bin', \
                    [], '', test_file)
            cmake_lines_project.extend(make_target_test.get_cmake_cmd_list())
        cmake_lines_project.append('')

    ### set install target
    # install_path = 'output/' + project_defs_dict["MODULE_TYPE"]
    # cmake_lines_project.append("install(TARGETS {} DESTINATION {})".format(project_defs_dict["MODULE_NAME"], install_path))


    # write CMakeLists
    with open('CMakeLists.txt', 'w') as file:
        print("----- Start Writting CMakeLists -----")
        for line in cmake_lines_project:
            line = line.replace('\\', '/')
            file.write(line + "\n")

    # post process
    cmake_py.post_process.run(project_defs_dict)

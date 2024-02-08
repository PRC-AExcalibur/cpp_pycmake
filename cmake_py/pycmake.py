import copy
import os
from typing import Set

def cmake_cmd_var(cmd, key, value):
    if isinstance(value, list):
        list_str = ''
        for var_str in value:
            list_str += '"{}" '.format(var_str)
        if list_str == '':
            return '{}({})'.format(cmd, key)
        return '{}({} {})'.format(cmd, key, list_str)
    return '{}({} "{}")'.format(cmd, key, value)

def cmake_cmd_lines(cmd, cmake_vars):
    res = []
    for k,v in cmake_vars.items():
        if v !='':
            res.append(cmake_cmd_var(cmd, k, v))
    return res

def get_cpp_files(directory):
    cpp_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.cpp'):
                cpp_files.append(os.path.join(root, file))  
    return cpp_files 


class pycmake_interface():
    __BuildType__ = {'DEBUG':'', 'RELEASE':'', 'RELWITHDEBINFO':'', 'MINSIZEREL':''}
    def get_cmake_vars(self):
        pass
    def get_cmake_cmd_list(self):
        pass

class project_env(pycmake_interface):
    def __init__(self, cmake_vers, mod_name):
        self.cmake_version = cmake_vers
        self.module_name = mod_name

    def get_cmake_vars(self):
        variables = {}
        return variables

    def get_cmake_cmd_list(self):
        cmd_list = []
        cmd_list.append("cmake_minimum_required(VERSION {})".format(self.cmake_version))
        cmd_list.append("project({})".format(self.module_name))
        return cmd_list

class directory_env(pycmake_interface):
    def __init__(self, lib_list):
        self.current_binary_dir = '../build'
        self.current_source_dir = '../src'
        self.library_path = 'lib'
        self.exec_out_path = "../build/output/bin"
        self.lib_out_path = "../build/output/lib"

        self.library_list = lib_list
        self.cpp_list = get_cpp_files(self.current_source_dir)

    def get_cmake_vars(self):
        variables = {}
        variables['CMAKE_CURRENT_BINARY_DIR'] = self.current_binary_dir
        variables['CMAKE_CURRENT_SOURCE_DIR'] = self.current_source_dir
        variables['CMAKE_LIBRARY_PATH'] = self.library_path
        variables['EXECUTABLE_OUTPUT_PATH'] = self.exec_out_path
        variables['LIBRARY_OUTPUT_PATH'] = self.lib_out_path
        return variables
    
    def get_cmake_cmd_list(self):
        cmd_list = cmake_cmd_lines("set", self.get_cmake_vars())
        cmd_list.append(cmake_cmd_var("set", 'src_list', self.cpp_list))
        for lib_name in self.library_list:
            cmd = cmake_cmd_lines("include_directories", self.library_path + "/{}/include".format(lib_name))
            cmd_list.append(cmd)
        return cmd_list

class cmake_env(pycmake_interface):
    def __init__(self):
        self.ar = ''
        self.build_type = ''
        self.dlltool = ''
        self.linker = ''
        self.make_program = ''
        self.install_prefix = ''
        self.ranlib = ''
        self.readelf = ''

    def get_cmake_vars(self):
        variables = {}
        for attr in vars(self):
            if isinstance(getattr(self, attr), str):
                attr_cmake = 'CMAKE_' + attr.upper()
                variables[attr_cmake] = getattr(self, attr)
        return variables

    def get_cmake_cmd_list(self):
        return cmake_cmd_lines("set", self.get_cmake_vars())

class link_env(pycmake_interface):
    def __init__(self, target_set:Set[str]):
        self.target_type_set = target_set # EXE MODULE SHARED STATIC

        self.linker_flags = ''
        self.linker_build_type = copy.deepcopy(pycmake_interface.__BuildType__)

    def get_cmake_vars(self):
        variables = {}
        for target_type in self.target_type_set:
            if target_type in ['EXE', 'MODULE','SHARED', 'STATIC']:
                for attr in vars(self):
                    if isinstance(getattr(self, attr), str):
                        attr_cmake = 'CMAKE_' + target_type + '_' + attr.upper()
                        variables[attr_cmake] = getattr(self, attr)
                for flags_key, flags_value in self.linker_build_type.items():
                    variables['CMAKE_{}_LINKER_FLAGS_'.format(target_type) + flags_key] = flags_value
        return variables

    def get_cmake_cmd_list(self):
        return cmake_cmd_lines("set", self.get_cmake_vars())

class compile_env(pycmake_interface):
    def __init__(self, language_set:Set[str]):
        self.language = language_set # C CXX

        self.compiler = ''
        self.compiler_ar = ''
        self.compiler_ranlib = ''
        self.flags = ''
        self.flags_build_type = copy.deepcopy(pycmake_interface.__BuildType__)

    def get_cmake_vars(self):
        variables = {}
        for c_type in self.language:
            if c_type in ['C', 'CXX']:
                for attr in vars(self):
                    if isinstance(getattr(self, attr), str):
                        attr_cmake = 'CMAKE_' + c_type + '_' + attr.upper()
                        variables[attr_cmake] = getattr(self, attr)
                for flags_key, flags_value in self.flags_build_type.items():
                    variables['CMAKE_{}_FLAGS_'.format(c_type) + flags_key] = flags_value
        return variables

    def get_cmake_cmd_list(self):
        return cmake_cmd_lines("set", self.get_cmake_vars())


class compile_target(pycmake_interface):
    __TargetTypeCmd__ = {"bin":"add_executable", "slib":"add_library", "dlib":"add_library"}
    def __init__(self, t_name, t_type, lib_list, lib_dir, ex_src):
        self.target_name = t_name
        self.target_type = t_type
        self.library_list = lib_list
        self.library_dir = lib_dir
        self.extend_src = ex_src
    def get_cmake_cmd_list(self):
        cmd_list = []
        cmd = ''
        for lib_name in self.library_list:
            cmd = cmake_cmd_var("link_directories", self.library_dir + '/{}/lib'.format(lib_name), [])
            cmd_list.append(cmd)

        make_target = "{} ".format(self.target_name)
        if self.target_type == "dlib":
            make_target += "SHARED "
        cmd = cmake_cmd_var(self.__TargetTypeCmd__[self.target_type], \
                          make_target + "{}".format(self.extend_src) + " ${src_list}", [])
        cmd_list.append(cmd)

        lib_str = ''
        for lib_name in self.library_list:
            lib_str += lib_name + " "
        if lib_str != '':
            cmd = cmake_cmd_var("target_link_libraries", "{} ".format(self.target_name), lib_str)
            cmd_list.append(cmd)

        return cmd_list
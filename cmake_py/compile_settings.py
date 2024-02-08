from . import pycmake



def generate_compile_settings(build_type = 'DEBUG'):

    env_list = []

    # set cmake_env
    env_base = pycmake.cmake_env()
    env_base.build_type = build_type
    env_base.install_prefix = "../build/"
    env_list.append(env_base)

    # set c_compile_env
    warn_str = '-Werror -Wall -Wextra -Wshadow -Wno-unused-parameter -Wno-unused-variable -Wno-unused-but-set-variable '
    f_str = '-fPIC -pthread -fno-strict-aliasing -fno-delete-null-pointer-checks -fno-strict-overflow -fsigned-char '

    compile_c_str = '-std=gnu17 -ggdb3 ' + warn_str + f_str
    env_compile_c = pycmake.compile_env({'C'})
    env_compile_c.flags = compile_c_str
    env_compile_c.flags_build_type['DEBUG'] = '-O0 ' +  compile_c_str
    env_compile_c.flags_build_type['RELEASE'] = '-O2 ' + compile_c_str
    # env_compile_c.flags_build_type['RELWITHDEBINFO']
    # env_compile_c.flags_build_type['MINSIZEREL']
    env_list.append(env_compile_c)

    # set cpp_compile_env
    compile_cpp_str = '-std=gnu++17 -ggdb3 ' + warn_str + f_str
    env_compile_cpp = pycmake.compile_env({'CXX'})
    env_compile_cpp.flags = compile_cpp_str
    env_compile_cpp.flags_build_type['DEBUG'] = '-O0 ' + compile_cpp_str
    env_compile_cpp.flags_build_type['RELEASE'] = '-O2 ' + compile_cpp_str
    env_list.append(env_compile_cpp)

    # set link_env
    env_link = pycmake.link_env({'EXE', 'MODULE','SHARED', 'STATIC'})
    env_list.append(env_link)

    res = []
    for i in env_list:
        res.extend(i.get_cmake_cmd_list())
    return res
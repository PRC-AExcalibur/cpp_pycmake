# will execute function "run()" before "cmake.py" build "CMakeLists.txt"


'''
A python script that executes the run() function before building cmake.
Typically used to configure the environment, log messages, auto-generate code, etc.

'''


def run():
    print("----- Start Cmake Prepare -----")
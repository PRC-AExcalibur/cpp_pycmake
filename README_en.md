# PyCMake C++ Project Framework Documentation
# PyCMake C++ 项目框架文档(中文版详见README.md)

### introduction
C++PyCMake is a simple C++ project framework that you don't need to write cmake or makefile yourself. Run `pycmake.py` will automatically generate the `CMakeLists.txt` cmake file and can automatically execute a customized compilation (test) process.

### File Structure and Organization

The project framework follows a predefined file structure to organize the various components of the project. 
(The example files in the include,src,lib,test directory can be deleted.)
The root directory contains the following folders:

- build: Contains the CMakeLists for the build and the compiled c++ files, which are created/deleted by cmake.py
- include: Contains all the header files (.h) that are shared across different source files
- src: Contains all the source files (.cpp) implementing the functionalities defined in the header files
- lib: Contains libaries or dependencies that the project depends on.(Already compiled .a .so .dll etc.)
- test: Contains test cases for the project (when project is slib/dlib)

### Project customizable properties
`pycmake_config.ini` defines some project properties that can be extended as needed.

The following are the main configuration items in this file (the parameter examples are in a usable state and can also be modified):

#### [project_config]
- CMake version requirement: `CMAKE_VERSION = 3.0`
- Module name: `MODULE_NAME = pycmake`
- Module type (dlib/slib/bin): `MODULE_TYPE = slib`

#### [cmake_config]
- C++ standard version: `CMAKE_CXX_STANDARD = 17`
- Whether to enforce the C++ standard: `CMAKE_CXX_STANDARD_REQUIRED = ON`
- C standard version: `CMAKE_C_STANDARD = 17`
- Whether to enforce the C standard: `CMAKE_C_STANDARD_REQUIRED = ON`
- Whether to generate position-independent code: `CMAKE_POSITION_INDEPENDENT_CODE = ON`
- All paths are relative to `/build`:
  - Current binary directory: `CMAKE_CURRENT_BINARY_DIR = ../build/output`
  - Current source directory: `CMAKE_CURRENT_SOURCE_DIR = ../src`
  - Library search path: `CMAKE_LIBRARY_PATH = ../lib`
  - Executable output path: `EXECUTABLE_OUTPUT_PATH = ../build/output/bin`
  - Library output path: `LIBRARY_OUTPUT_PATH = ../build/output/lib`
  - Installation prefix: `CMAKE_INSTALL_PREFIX = ../build`

#### [cmake_compile_flags]
- Debug mode compilation flags: `DEBUG = -O0`
- Release mode compilation flags: `RELEASE = -O2`
- Release mode with debug information compilation flags: `RELWITHDEBINFO = -O2 -g`
- Minimum size release mode compilation flags: `MINSIZEREL = -Os`
- C language compilation string: `c_compile_str = -std=gnu17 -ggdb3`
- C++ language compilation string: `cpp_compile_str = -std=gnu++17 -ggdb3`
- Warning-related compilation string: `warn_str = -Werror -Wall -Wextra -Wshadow -Wno-unused-parameter -Wno-unused-variable -Wno-unused-but-set-variable`
- Other compilation flag string: `f_str = -fPIC -pthread -fno-strict-aliasing -fno-delete-null-pointer-checks -fno-strict-overflow -fsigned-char`
- Test file path: `test_path_str = ../test`
  
#### Commented sections (Choose according to the compiler)
- GNU compiler warning-related compilation string (commented): `gnu_warn_str = -Werror -Wall -Wextra -Wshadow -Wno-unused-parameter -Wno-unused-variable -Wno-unused-but-set-variable`
- GNU compiler other compilation flag string (commented): `gnu_f_str = -fPIC -pthread -fno-strict-aliasing -fno-delete-null-pointer-checks -fno-strict-overflow -fsigned-char`
- MSVC compiler warning-related compilation string (commented): `msvc_warn_str = /W4 /WX`
- MSVC compiler other compilation flag string (commented): `msvc_f_str = /MD /EHsc /GR`

### Compile and run
Run `pycmake.py` in the project root directory to generate `CMakeLists.txt`, then automatically compile and run tests.

#### Automated Compilation/Testing
`pycmake.py` accepts two input parameters:
- `build_type`: Compilation type (default: `DEBUG`)
  - `DEBUG`: Compilation flag `O0`
  - `RELEASE`: Compilation flag `O2`
  - `CLEAN`: Clean the `build` directory
- `stage`: Compilation phase (default: `TEST`). Compiled files will be placed in `build/output/`
  - `BUILD`: Only compile source files (`src/*`), ignoring test files (`test/*`)
  - `TEST`: Compile all files and sequentially execute test cases in `build/output/bin` directory

#### Manual Compilation
1. Modify the `main` function in `pycmake.py` to disable auto-compilation
2. Run `cmake` to generate Makefile (Linux) or other build files (Windows, etc.)
3. Run `make` or `cmake --build .` to compile the project
4. Retrieve compiled files from `build/output/`

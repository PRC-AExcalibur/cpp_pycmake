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
`project_defs.mk` defines a number of attributes that can be extended, currently only `:=` assignments are allowed.

- CMAKE version requirements: `CMAKE_VERSION := 3.0`.
- Module name: `MODULE_NAME := pycmake`.
- Module type (dlib/slib/bin): `MODULE_TYPE := slib`

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

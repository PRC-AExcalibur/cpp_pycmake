# PyCMake C++ Project Framework Documentation
# PyCMake C++ 项目框架文档(中文版详见README.md)

### introduction
C++PyCMake is a simple C++ project framework that you don't need to write cmake or makefile yourself. Run `cmake.py` will automatically generate the `CMakeLists.txt` cmake file and can automatically execute a customized compilation (test) process.

### File Structure and Organization

The project framework follows a predefined file structure to organize the various components of the project. 
(The example files in the include,src,lib,test directory can be deleted.)
The root directory contains the following folders:

- build: Contains the CMakeLists for the build and the compiled c++ files, which are created/deleted by cmake.py
- cmake_py: Contains pre_process.py and post_process.py, customizable to modify

- include: Contains all the header files (.h) that are shared across different source files
- src: Contains all the source files (.cpp) implementing the functionalities defined in the header files
- lib: Contains libaries or dependencies that the project depends on.(Already compiled .a .so .dll etc.)
- test: Contains test cases for the project (when project is slib/dlib)

### Project customizable properties
`project_defs.mk` defines a number of attributes that can be extended, currently only `:=` assignments are allowed.

- CMAKE version requirements: `CMAKE_VERSION := 3.0`.
- Module name: `MODULE_NAME := pycmake`.
- Module type (dlib/slib/bin): `MODULE_TYPE := slib`
- Dependent library names: `MODULE_DEPEND_LIB := lib1 lib2`

### Compile and run
Run `cmake.py` in the project root directory to generate `CMakeLists.txt`;

##### Compile automatically
Under the `cmake_py` path, the post-processing script `post_process.py` has been written to automatically compile;
Run `cmake.py` directly to get the compiled file under `build/output/`.

##### Automated testing
Under the `cmake_py` path, the post-processing script `post_process.py` has been written to automate the tests;
now the automatic build-to-execute test process is adapted to linux, and windows needs to replace the `make` command;
Running `cmake.py` directly will execute the testcases in the test directory in order.

##### Manual compilation
Modify `post_process.py.run()` to cancel the automatic compilation;
Run `cmake` to generate Makefile (Linux) or other files (windows...) ;
Run `make` to compile the project;
Get the compiled file under `build/output/`.
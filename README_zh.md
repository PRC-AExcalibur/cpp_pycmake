# PyCMake C++ 项目框架文档

### 简介
C++PyCMake 是一个简单的 C++ 项目框架，你不需要自己编写 cmake 或 makefile 等文件。运行 `cmake.py` 将自动生成 `CMakeLists.txt` 的cmake文件，并可以自动执行自定义编译（测试）流程。

### 文件结构和组织
项目框架采用预定义的文件结构来组织项目的各个组成部分。
（include,src,lib,test目录下的示例文件可删除）
项目根目录包含以下文件夹：

- build: 包含构建的CMakeLists和编译c++后的文件，由cmake.py控制创建/删除
- cmake_py: 包含预处理和后处理的python脚本，可自定义修改

- include： 包含不同源文件共享的所有头文件（.h）
- src： 包含实现头文件中定义的功能的所有源文件（.cpp）
- lib： 包含项目所依赖的库或依赖项(已经编译好的.a .so .dll等)
- test：测试： 包含项目的测试用例(当项目为静态库/动态库)

### 项目自定义属性
`project_defs.mk`定义了一些属性，可以自行扩展， 目前只允许`:=`赋值

- CMAKE的版本要求： `CMAKE_VERSION := 3.0`
- 模块名： `MODULE_NAME := pycmake`
- 模块类型（dlib/slib/bin）： `MODULE_TYPE := slib`
- 依赖的库名： `MODULE_DEPEND_LIB := lib1 lib2 `

### 编译和运行
在项目根目录下运行 `cmake.py` 生成 `CMakeLists.txt`；

##### 自动编译
在`cmake_py`路径下，后处理脚本`post_process.py`已经写好自动编译的脚本；
直接运行 `cmake.py` 在`build/output/`下获取编译文件。

##### 自动测试
在`cmake_py`路径下，后处理脚本`post_process.py`已经写好自动测试的脚本；
目前自动构建到执行测试流程适配linux,windows需自行替换`make`命令；
直接运行 `cmake.py` 会直接按顺序执行test目录下的测试用例。

##### 手动编译
重写`post_process.py.run()`，取消自动编译；
运行 `cmake` 生成 Makefile（Linux）或其他文件（windows...）；
运行`make`编译项目；
在`build/output/`下获取编译文件。
# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.30

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/src

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build

# Include any dependencies generated for this target.
include lib/CMakeFiles/IRAnalyzerStatic.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include lib/CMakeFiles/IRAnalyzerStatic.dir/compiler_depend.make

# Include the progress variables for this target.
include lib/CMakeFiles/IRAnalyzerStatic.dir/progress.make

# Include the compile flags for this target's objects.
include lib/CMakeFiles/IRAnalyzerStatic.dir/flags.make

# Object files for target IRAnalyzerStatic
IRAnalyzerStatic_OBJECTS =

# External object files for target IRAnalyzerStatic
IRAnalyzerStatic_EXTERNAL_OBJECTS = \
"/home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build/lib/CMakeFiles/IRAnalyzerObj.dir/IRAnalyzer.cpp.o"

lib/libIRAnalyzerStatic.a: lib/CMakeFiles/IRAnalyzerObj.dir/IRAnalyzer.cpp.o
lib/libIRAnalyzerStatic.a: lib/CMakeFiles/IRAnalyzerStatic.dir/build.make
lib/libIRAnalyzerStatic.a: lib/CMakeFiles/IRAnalyzerStatic.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --bold --progress-dir=/home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Linking CXX static library libIRAnalyzerStatic.a"
	cd /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build/lib && $(CMAKE_COMMAND) -P CMakeFiles/IRAnalyzerStatic.dir/cmake_clean_target.cmake
	cd /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build/lib && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/IRAnalyzerStatic.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
lib/CMakeFiles/IRAnalyzerStatic.dir/build: lib/libIRAnalyzerStatic.a
.PHONY : lib/CMakeFiles/IRAnalyzerStatic.dir/build

lib/CMakeFiles/IRAnalyzerStatic.dir/clean:
	cd /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build/lib && $(CMAKE_COMMAND) -P CMakeFiles/IRAnalyzerStatic.dir/cmake_clean.cmake
.PHONY : lib/CMakeFiles/IRAnalyzerStatic.dir/clean

lib/CMakeFiles/IRAnalyzerStatic.dir/depend:
	cd /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/src /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/src/lib /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build/lib /home/masami/projects/linux-kernel-fuzzing/IRAnalyzer/build/lib/CMakeFiles/IRAnalyzerStatic.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : lib/CMakeFiles/IRAnalyzerStatic.dir/depend

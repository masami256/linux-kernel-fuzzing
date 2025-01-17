set (IRAnalyzerSourceCodes
	IRAnalyzer.h
	IRAnalyzer.cpp
	)

#file(COPY configs/ DESTINATION configs)

set(CMAKE_MACOSX_RPATH 0)

# Build libraries.
add_library (IRAnalyzerObj OBJECT ${IRAnalyzerSourceCodes})
add_library (IRAnalyzer SHARED $<TARGET_OBJECTS:IRAnalyzerObj>)
add_library (IRAnalyzerStatic STATIC $<TARGET_OBJECTS:IRAnalyzerObj>)

# Build executable.
set (EXECUTABLE_OUTPUT_PATH ${IRANALYZER_BINARY_DIR})
link_directories (${IRANALYZER_BINARY_DIR}/lib)
add_executable(iranalyzer ${IRAnalyzerSourceCodes})
target_link_libraries(iranalyzer 
	LLVMAsmParser 
	LLVMSupport 
	LLVMCore 
	LLVMAnalysis
	LLVMIRReader
	IRAnalyzerStatic
	)

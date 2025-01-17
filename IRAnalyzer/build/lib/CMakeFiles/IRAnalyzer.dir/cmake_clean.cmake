file(REMOVE_RECURSE
  "libIRAnalyzer.pdb"
  "libIRAnalyzer.so"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/IRAnalyzer.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()

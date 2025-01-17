file(REMOVE_RECURSE
  "libIRAnalyzerStatic.a"
  "libIRAnalyzerStatic.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/IRAnalyzerStatic.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()

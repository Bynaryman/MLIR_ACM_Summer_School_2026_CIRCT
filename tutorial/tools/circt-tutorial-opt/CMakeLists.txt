set(LLVM_LINK_COMPONENTS
  Support
)

add_llvm_executable(circt-tutorial-opt
  circt-tutorial-opt.cpp
)

llvm_update_compile_flags(circt-tutorial-opt)

target_link_libraries(circt-tutorial-opt
  PRIVATE
  TutorialTransforms
  CIRCTComb
  CIRCTHW
  CIRCTTransforms
  MLIRArithDialect
  MLIRFuncDialect
  MLIRIR
  MLIROptLib
  MLIRParser
  MLIRSupport
  MLIRTransforms
)

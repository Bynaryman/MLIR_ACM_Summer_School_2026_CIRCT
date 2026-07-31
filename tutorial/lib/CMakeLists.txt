add_mlir_library(TutorialTransforms
  FuncToHWModule.cpp
  LowerE4M3FNToComb.cpp
  Passes.cpp

  LINK_LIBS PUBLIC
  CIRCTComb
  CIRCTHW
  MLIRArithDialect
  MLIRFuncDialect
  MLIRFuncTransforms
  MLIRIR
  MLIRPass
  MLIRTransforms
)

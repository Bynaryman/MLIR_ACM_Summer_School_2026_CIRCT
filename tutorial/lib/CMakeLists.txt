add_mlir_library(TutorialTransforms
  FuncToHWModule.cpp
  Passes.cpp

  LINK_LIBS PUBLIC
  CIRCTHW
  MLIRFuncDialect
  MLIRIR
  MLIRPass
)

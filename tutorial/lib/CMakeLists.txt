add_mlir_library(TutorialTransforms
  LowerE4M3FNToComb.cpp

  LINK_LIBS PUBLIC
  CIRCTComb
  CIRCTHW
  MLIRArithDialect
  MLIRIR
  MLIRPass
  MLIRTransforms
)

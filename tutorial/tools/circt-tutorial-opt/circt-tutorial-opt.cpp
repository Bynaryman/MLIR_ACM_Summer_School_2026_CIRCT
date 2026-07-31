#include "Tutorial/Passes.h"

#include "circt/Dialect/Comb/CombOps.h"
#include "circt/Dialect/HW/HWDialect.h"
#include "mlir/Dialect/Arith/IR/Arith.h"
#include "mlir/Dialect/Func/IR/FuncOps.h"
#include "mlir/Pass/PassRegistry.h"
#include "mlir/Tools/mlir-opt/MlirOptMain.h"
#include "mlir/Transforms/Passes.h"

int main(int argc, char **argv) {
  mlir::DialectRegistry registry;
  registry.insert<mlir::arith::ArithDialect, mlir::func::FuncDialect,
                  circt::comb::CombDialect, circt::hw::HWDialect>();

  tutorial::registerPasses();
  mlir::registerCanonicalizerPass();
  mlir::registerCSEPass();

  return mlir::failed(mlir::MlirOptMain(
      argc, argv, "MLIR Summer School CIRCT optimizer", registry));
}

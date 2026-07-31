#include "circt/Dialect/HW/HWOps.h"
#include "mlir/Dialect/Func/IR/FuncOps.h"
#include "mlir/IR/IRMapping.h"
#include "mlir/Pass/Pass.h"
#include "llvm/ADT/STLExtras.h"

using namespace mlir;

namespace tutorial {
namespace {

class FuncToHWModulePass
    : public PassWrapper<FuncToHWModulePass, OperationPass<ModuleOp>> {
public:
  MLIR_DEFINE_EXPLICIT_INTERNAL_INLINE_TYPE_ID(FuncToHWModulePass)

  StringRef getArgument() const final { return "tutorial-func-to-hw"; }

  StringRef getDescription() const final {
    return "Convert single-block functions to HW modules with matching ports";
  }

  void getDependentDialects(DialectRegistry &registry) const override {
    registry.insert<func::FuncDialect, circt::hw::HWDialect>();
  }

  void runOnOperation() override {
    SmallVector<func::FuncOp> functions;
    getOperation().walk(
        [&](func::FuncOp function) { functions.push_back(function); });

    for (func::FuncOp function : functions) {
      if (!function.getBody().hasOneBlock()) {
        function.emitError("expected a single-block function");
        signalPassFailure();
        return;
      }

      OpBuilder builder(function);
      SmallVector<circt::hw::PortInfo> inputs;
      SmallVector<circt::hw::PortInfo> outputs;

      auto makePortName = [&](StringRef prefix, unsigned index) {
        return builder.getStringAttr((prefix + Twine(index)).str());
      };

      for (auto [index, argument] :
           llvm::enumerate(function.getArguments())) {
        StringAttr name =
            function.getArgAttrOfType<StringAttr>(index, "hw.name");
        if (!name)
          name = makePortName("arg", index);
        inputs.push_back(
            {{name, argument.getType(),
              circt::hw::ModulePort::Direction::Input},
             static_cast<size_t>(index), function.getArgAttrDict(index),
             nullptr});
      }

      for (auto [index, type] :
           llvm::enumerate(function.getResultTypes())) {
        StringAttr name =
            function.getResultAttrOfType<StringAttr>(index, "hw.name");
        if (!name)
          name = makePortName("result", index);
        outputs.push_back(
            {{name, type, circt::hw::ModulePort::Direction::Output},
             static_cast<size_t>(index), function.getResultAttrDict(index),
             nullptr});
      }

      circt::hw::ModulePortInfo portInfo(inputs, outputs);
      auto hwModule = circt::hw::HWModuleOp::create(
          builder, function.getLoc(), function.getSymNameAttr(), portInfo);

      if (Attribute visibility = function->getAttr("sym_visibility"))
        hwModule->setAttr("sym_visibility", visibility);

      Block &source = function.getBody().front();
      Block &destination = *hwModule.getBodyBlock();
      destination.getTerminator()->erase();

      IRMapping mapping;
      for (auto [index, argument] : llvm::enumerate(source.getArguments()))
        mapping.map(argument, destination.getArgument(index));

      builder.setInsertionPointToStart(&destination);
      for (Operation &operation : source) {
        if (auto returnOp = dyn_cast<func::ReturnOp>(operation)) {
          SmallVector<Value> results;
          for (Value operand : returnOp.getOperands())
            results.push_back(mapping.lookup(operand));
          circt::hw::OutputOp::create(builder, returnOp.getLoc(), results);
          continue;
        }
        builder.clone(operation, mapping);
      }

      function.erase();
    }
  }
};

} // namespace

void registerFuncToHWModulePass() {
  static PassRegistration<FuncToHWModulePass> registration;
  (void)registration;
}

} // namespace tutorial

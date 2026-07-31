#include "Tutorial/Passes.h"

#include "circt/Dialect/Comb/CombOps.h"
#include "circt/Dialect/HW/HWOps.h"
#include "mlir/Dialect/Arith/IR/Arith.h"
#include "mlir/Dialect/Func/IR/FuncOps.h"
#include "mlir/Dialect/Func/Transforms/FuncConversions.h"
#include "mlir/IR/BuiltinTypes.h"
#include "mlir/Pass/Pass.h"
#include "mlir/Transforms/DialectConversion.h"
#include "llvm/ADT/APInt.h"

using namespace mlir;

namespace tutorial {
namespace {

/// Build the combinational E4M3FN multiplier.
///
/// This starter implementation only computes the result sign and sets the
/// exponent and fraction to zero. Students should replace the zero payload with
/// exponent addition, significand multiplication, normalization, rounding, and
/// special-case handling.
static Value buildE4M3FNMultiplier(PatternRewriter &rewriter, Location loc,
                                   Value lhsBits, Value rhsBits) {
  auto lhsSign = circt::comb::ExtractOp::create(rewriter, loc, lhsBits,
                                                /*lowBit=*/7,
                                                /*bitWidth=*/1);
  auto rhsSign = circt::comb::ExtractOp::create(rewriter, loc, rhsBits,
                                                /*lowBit=*/7,
                                                /*bitWidth=*/1);
  auto resultSign = circt::comb::XorOp::create(
      rewriter, loc, lhsSign.getResult(), rhsSign.getResult());

  // TODO: Replace this placeholder with the seven payload bits {exp, frac}.
  auto zeroPayload = circt::hw::ConstantOp::create(
      rewriter, loc, llvm::APInt(/*numBits=*/7, /*value=*/0));

  return circt::comb::ConcatOp::create(rewriter, loc, resultSign.getResult(),
                                       zeroPayload.getResult())
      .getResult();
}

/// The type converter turns each E4M3FN SSA value into its eight wire bits.
/// Students only implement the datapath built by this pattern; function
/// signature and return conversion are supplied pass infrastructure.
class LowerE4M3FNMulPattern : public OpConversionPattern<arith::MulFOp> {
public:
  using OpConversionPattern::OpConversionPattern;

  LogicalResult
  matchAndRewrite(arith::MulFOp mul, OpAdaptor adaptor,
                  ConversionPatternRewriter &rewriter) const override {
    if (!isa<Float8E4M3FNType>(mul.getType()))
      return failure();

    if (!adaptor.getLhs().getType().isInteger(8) ||
        !adaptor.getRhs().getType().isInteger(8))
      return failure();

    Value result = buildE4M3FNMultiplier(rewriter, mul.getLoc(),
                                         adaptor.getLhs(), adaptor.getRhs());
    rewriter.replaceOp(mul, result);
    return success();
  }
};

class LowerE4M3FNToCombPass
    : public PassWrapper<LowerE4M3FNToCombPass, OperationPass<ModuleOp>> {
public:
  MLIR_DEFINE_EXPLICIT_INTERNAL_INLINE_TYPE_ID(LowerE4M3FNToCombPass)

  StringRef getArgument() const final { return "lower-e4m3fn-to-comb"; }

  StringRef getDescription() const final {
    return "Lower E4M3FN arith.mulf operations to CIRCT comb logic";
  }

  void getDependentDialects(DialectRegistry &registry) const override {
    registry.insert<arith::ArithDialect, circt::comb::CombDialect,
                    circt::hw::HWDialect, func::FuncDialect>();
  }

  void runOnOperation() override {
    MLIRContext *context = &getContext();

    TypeConverter typeConverter;
    typeConverter.addConversion([](Type type) { return type; });
    typeConverter.addConversion([context](Float8E4M3FNType) -> Type {
      return IntegerType::get(context, 8);
    });

    ConversionTarget target(*context);
    target.addLegalOp<ModuleOp>();
    target.addLegalDialect<circt::comb::CombDialect, circt::hw::HWDialect>();
    target.addDynamicallyLegalOp<func::FuncOp>([&](func::FuncOp function) {
      return typeConverter.isSignatureLegal(function.getFunctionType()) &&
             typeConverter.isLegal(&function.getBody());
    });
    target.addDynamicallyLegalOp<func::ReturnOp>([&](func::ReturnOp op) {
      return typeConverter.isLegal(op.getOperandTypes());
    });
    target.addDynamicallyLegalOp<arith::MulFOp>([](arith::MulFOp mul) {
      return !isa<Float8E4M3FNType>(mul.getType());
    });

    RewritePatternSet patterns(context);
    patterns.add<LowerE4M3FNMulPattern>(typeConverter, context);
    populateFunctionOpInterfaceTypeConversionPattern<func::FuncOp>(
        patterns, typeConverter);
    populateReturnOpTypeConversionPattern(patterns, typeConverter);

    if (failed(applyPartialConversion(getOperation(), target,
                                      std::move(patterns))))
      signalPassFailure();
  }
};

} // namespace

void registerLowerE4M3FNToCombPass() {
  static PassRegistration<LowerE4M3FNToCombPass> registration;
  (void)registration;
}

} // namespace tutorial

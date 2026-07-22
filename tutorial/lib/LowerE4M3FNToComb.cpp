#include "Tutorial/Passes.h"

#include "circt/Dialect/Comb/CombOps.h"
#include "circt/Dialect/HW/HWOps.h"
#include "mlir/Dialect/Arith/IR/Arith.h"
#include "mlir/IR/BuiltinTypes.h"
#include "mlir/Pass/Pass.h"
#include "mlir/Transforms/GreedyPatternRewriteDriver.h"
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

  return circt::comb::ConcatOp::create(
             rewriter, loc, resultSign.getResult(), zeroPayload.getResult())
      .getResult();
}

/// Match this deliberately constrained tutorial shape:
///
///   i8 -> arith.bitcast -> f8E4M3FN
///                              \
///                               arith.mulf -> arith.bitcast -> i8
///                              /
///   i8 -> arith.bitcast -> f8E4M3FN
///
/// Matching the outer bitcast allows the floating-point subgraph to be replaced
/// directly by an i8 comb network without introducing a general type converter.
class LowerE4M3FNMulPattern : public OpRewritePattern<arith::BitcastOp> {
public:
  using OpRewritePattern::OpRewritePattern;

  LogicalResult matchAndRewrite(arith::BitcastOp outputCast,
                                PatternRewriter &rewriter) const override {
    auto outputType = dyn_cast<IntegerType>(outputCast.getType());
    if (!outputType || outputType.getWidth() != 8)
      return failure();

    auto mul = outputCast.getIn().getDefiningOp<arith::MulFOp>();
    if (!mul || !isa<Float8E4M3FNType>(mul.getType()))
      return failure();

    auto lhsCast = mul.getLhs().getDefiningOp<arith::BitcastOp>();
    auto rhsCast = mul.getRhs().getDefiningOp<arith::BitcastOp>();
    if (!lhsCast || !rhsCast)
      return failure();

    auto lhsType = dyn_cast<IntegerType>(lhsCast.getIn().getType());
    auto rhsType = dyn_cast<IntegerType>(rhsCast.getIn().getType());
    if (!lhsType || !rhsType || lhsType.getWidth() != 8 ||
        rhsType.getWidth() != 8)
      return failure();

    Value result = buildE4M3FNMultiplier(
        rewriter, outputCast.getLoc(), lhsCast.getIn(), rhsCast.getIn());

    rewriter.replaceOp(outputCast, result);

    // Remove the now-dead floating-point operations explicitly so that the
    // result of this pass contains only integer, HW, and comb operations.
    if (mul->use_empty())
      rewriter.eraseOp(mul);

    // Both operands may originate from the same bitcast (for example, x * x).
    // In that case, erase the shared producer only once.
    if (lhsCast == rhsCast) {
      if (lhsCast->use_empty())
        rewriter.eraseOp(lhsCast);
    } else {
      if (lhsCast->use_empty())
        rewriter.eraseOp(lhsCast);
      if (rhsCast->use_empty())
        rewriter.eraseOp(rhsCast);
    }

    return success();
  }
};

class LowerE4M3FNToCombPass
    : public PassWrapper<LowerE4M3FNToCombPass,
                         OperationPass<ModuleOp>> {
public:
  MLIR_DEFINE_EXPLICIT_INTERNAL_INLINE_TYPE_ID(LowerE4M3FNToCombPass)

  StringRef getArgument() const final { return "lower-e4m3fn-to-comb"; }

  StringRef getDescription() const final {
    return "Lower E4M3FN arith.mulf operations to CIRCT comb logic";
  }

  void getDependentDialects(DialectRegistry &registry) const override {
    registry.insert<arith::ArithDialect, circt::comb::CombDialect,
                    circt::hw::HWDialect>();
  }

  void runOnOperation() override {
    RewritePatternSet patterns(&getContext());
    patterns.add<LowerE4M3FNMulPattern>(&getContext());

    if (failed(applyPatternsGreedily(getOperation(), std::move(patterns))))
      signalPassFailure();
  }
};

} // namespace

void registerPasses() {
  static PassRegistration<LowerE4M3FNToCombPass> registration;
  (void)registration;
}

} // namespace tutorial

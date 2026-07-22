module {
  hw.module @e4m3fn_mul(
      in %lhs : i8,
      in %rhs : i8,
      out result : i8) {
    %lhsFloat = arith.bitcast %lhs : i8 to f8E4M3FN
    %rhsFloat = arith.bitcast %rhs : i8 to f8E4M3FN
    %product = arith.mulf %lhsFloat, %rhsFloat : f8E4M3FN
    %result = arith.bitcast %product : f8E4M3FN to i8
    hw.output %result : i8
  }

  // Exercise the case where both multiply operands share one input bitcast.
  hw.module @e4m3fn_square(in %value : i8, out result : i8) {
    %asFloat = arith.bitcast %value : i8 to f8E4M3FN
    %product = arith.mulf %asFloat, %asFloat : f8E4M3FN
    %result = arith.bitcast %product : f8E4M3FN to i8
    hw.output %result : i8
  }
}

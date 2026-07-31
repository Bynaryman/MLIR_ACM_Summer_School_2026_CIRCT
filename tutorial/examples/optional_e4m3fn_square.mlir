module {
  // Exercise: recognize that both operands are the same SSA value, then emit
  // a dedicated squarer instead of lowering this as a generic multiplier.
  hw.module @e4m3fn_square(in %value : i8, out result : i8) {
    %asFloat = arith.bitcast %value : i8 to f8E4M3FN
    %product = arith.mulf %asFloat, %asFloat : f8E4M3FN
    %result = arith.bitcast %product : f8E4M3FN to i8
    hw.output %result : i8
  }
}

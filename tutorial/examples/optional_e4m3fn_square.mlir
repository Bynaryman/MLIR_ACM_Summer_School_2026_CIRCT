module {
  // Exercise: recognize that both operands are the same SSA value, then emit
  // a dedicated squarer instead of lowering this as a generic multiplier.
  func.func @e4m3fn_square(%value : f8E4M3FN) -> f8E4M3FN {
    %product = arith.mulf %value, %value : f8E4M3FN
    return %product : f8E4M3FN
  }
}

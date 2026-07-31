module {
  func.func @ex6_float_mul(
      %lhs : f8E4M3FN,
      %rhs : f8E4M3FN) -> f8E4M3FN {
    %product = arith.mulf %lhs, %rhs : f8E4M3FN
    return %product : f8E4M3FN
  }
}

module {
  func.func @ex6_float_mul(
      %lhs : f8E4M3FN {hw.name = "lhs"},
      %rhs : f8E4M3FN {hw.name = "rhs"})
      -> (f8E4M3FN {hw.name = "product"}) {
    %product = arith.mulf %lhs, %rhs : f8E4M3FN
    return %product : f8E4M3FN
  }
}

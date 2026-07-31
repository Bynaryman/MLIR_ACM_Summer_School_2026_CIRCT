module {
  func.func @e4m3fn_mul(
      %lhs : i8 {hw.name = "lhs"},
      %rhs : i8 {hw.name = "rhs"})
      -> (i8 {hw.name = "result"}) {
    %lhsFloat = arith.bitcast %lhs : i8 to f8E4M3FN
    %rhsFloat = arith.bitcast %rhs : i8 to f8E4M3FN
    %product = arith.mulf %lhsFloat, %rhsFloat : f8E4M3FN
    %result = arith.bitcast %product : f8E4M3FN to i8
    return %result : i8
  }
}

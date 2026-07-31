module {
  func.func @ex6_integer_mul(
      %lhs : i8 {hw.name = "lhs"},
      %rhs : i8 {hw.name = "rhs"})
      -> (i8 {hw.name = "product"}) {
    %product = arith.muli %lhs, %rhs : i8
    return %product : i8
  }
}

module {
  func.func @ex6_integer_mul(
      %lhs : i8,
      %rhs : i8) -> i8 {
    %product = arith.muli %lhs, %rhs : i8
    return %product : i8
  }
}

module {
  func.func @ex6_mul(%a : i8, %b : i8) -> i8 {
    %r = arith.muli %a, %b : i8
    return %r : i8
  }
}

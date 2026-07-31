module {
  func.func @e4m3fn_mul(%a : f8E4M3FN, %b : f8E4M3FN)
      -> f8E4M3FN {
    %r = arith.mulf %a, %b : f8E4M3FN
    return %r : f8E4M3FN
  }
}

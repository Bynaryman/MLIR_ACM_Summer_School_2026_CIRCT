module {
  func.func @e4m3fn_square(%value : f8E4M3FN) -> f8E4M3FN {
    %product = arith.mulf %value, %value : f8E4M3FN
    return %product : f8E4M3FN
  }
}

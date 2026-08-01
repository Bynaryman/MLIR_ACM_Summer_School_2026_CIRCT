module {
  func.func @e4m3fn_square(%value : i8) -> i8 {
    %as_float = arith.bitcast %value : i8 to f8E4M3FN
    %product = arith.mulf %as_float, %as_float : f8E4M3FN
    %result = arith.bitcast %product : f8E4M3FN to i8
    return %result : i8
  }
}

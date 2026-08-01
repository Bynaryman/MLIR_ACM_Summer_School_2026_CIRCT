module {
  func.func @e4m3fn_mul(%a : i8, %b : i8) -> i8 {
    %af = arith.bitcast %a : i8 to f8E4M3FN
    %bf = arith.bitcast %b : i8 to f8E4M3FN
    %product = arith.mulf %af, %bf : f8E4M3FN
    %result = arith.bitcast %product : f8E4M3FN to i8
    return %result : i8
  }
}

module e4m3_mul_parts(
  input  logic [7:0] lhs,
  input  logic [7:0] rhs,
  output logic       result_sign,
  output logic [4:0] exponent_sum,
  output logic [7:0] significand_product
);
  // This teaching schematic covers normal operands only.
  assign result_sign = lhs[7] ^ rhs[7];
  assign exponent_sum = {1'b0, lhs[6:3]} + {1'b0, rhs[6:3]};
  assign significand_product =
      {4'b0, 1'b1, lhs[2:0]} * {4'b0, 1'b1, rhs[2:0]};
endmodule

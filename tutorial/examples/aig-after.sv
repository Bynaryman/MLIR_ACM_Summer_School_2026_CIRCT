module factor (
  input  wire [3:0] a,
  input  wire [3:0] b,
  input  wire [3:0] c,
  output wire [8:0] y
);
  wire [4:0] sum = {1'b0, b} + {1'b0, c};
  assign y = a * sum;
endmodule

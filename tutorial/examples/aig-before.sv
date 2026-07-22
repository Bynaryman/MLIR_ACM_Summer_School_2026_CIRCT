module factor (
  input  wire [3:0] a,
  input  wire [3:0] b,
  input  wire [3:0] c,
  output wire [8:0] y
);
  assign y = a * b + a * c;
endmodule

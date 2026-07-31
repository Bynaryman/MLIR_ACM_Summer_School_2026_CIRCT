module ex1_fma (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire [3:0] c,
    output wire [8:0] d
);
    assign d = (a * b) + (c * 1'd1);

endmodule

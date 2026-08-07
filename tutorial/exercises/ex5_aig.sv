module ex5_aig (
    input  logic       a,
    input  logic       b,
    input  logic [7:0] x,
    output logic [7:0] out
);

always_comb begin
    out = a   ? (b ? -x       : -(x + 8'd1))
              : (b ? x + 8'd1 :           x);
end

endmodule

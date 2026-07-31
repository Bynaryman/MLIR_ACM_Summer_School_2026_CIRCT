module ex5_aig (
    input  logic       a,
    input  logic       b,
    input  logic [7:0] x,
    output logic [7:0] out
);
    assign out = (x ^ {8{a}}) + b;
endmodule

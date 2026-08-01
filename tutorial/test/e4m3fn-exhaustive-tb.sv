`timescale 1ns/1ps

module e4m3fn_exhaustive_tb;
  reg  [7:0] lhs;
  reg  [7:0] rhs;
  wire [7:0] result;

  integer vector_file;
  integer scan_status;
  integer lhs_value;
  integer rhs_value;
  integer expected_value;
  integer checked;
  integer expected_count;
  integer errors;
  reg [1023:0] vector_path;

  e4m3fn_mul dut (lhs, rhs, result);

  initial begin
    if (!$value$plusargs("VECTORS=%s", vector_path))
      $fatal(1, "missing +VECTORS=<path>");
    if (!$value$plusargs("COUNT=%d", expected_count))
      expected_count = 65536;

    vector_file = $fopen(vector_path, "r");
    if (vector_file == 0)
      $fatal(1, "cannot open vector file");

    checked = 0;
    errors = 0;
    while (!$feof(vector_file)) begin
      scan_status = $fscanf(
        vector_file, "%x %x %x\n", lhs_value, rhs_value, expected_value
      );
      if (scan_status == 3) begin
        lhs = lhs_value[7:0];
        rhs = rhs_value[7:0];
        #1;
        checked = checked + 1;
        if (result !== expected_value[7:0]) begin
          if (errors < 20)
            $display(
              "mismatch lhs=%02x rhs=%02x expected=%02x actual=%02x",
              lhs, rhs, expected_value[7:0], result
            );
          errors = errors + 1;
        end
      end
    end
    $fclose(vector_file);

    if (checked != expected_count)
      $fatal(1, "read %0d vectors instead of %0d", checked, expected_count);
    if (errors != 0)
      $fatal(1, "%0d of %0d E4M3 products differ", errors, checked);

    $display("PASS: all %0d E4M3 products match MLIR", checked);
    $finish;
  end
endmodule

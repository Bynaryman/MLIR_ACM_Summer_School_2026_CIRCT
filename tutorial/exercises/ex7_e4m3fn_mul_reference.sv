module e4m3fn_mul (
  input  logic [7:0] lhs,
  input  logic [7:0] rhs,
  output logic [7:0] result
);
  logic result_sign;
  logic lhs_nan;
  logic rhs_nan;
  logic lhs_zero;
  logic rhs_zero;
  logic [3:0] lhs_exp;
  logic [3:0] rhs_exp;
  logic [2:0] lhs_frac;
  logic [2:0] rhs_frac;
  logic [3:0] lhs_sig;
  logic [3:0] rhs_sig;
  logic [7:0] sig_product;

  logic signed [5:0] lhs_scale;
  logic signed [5:0] rhs_scale;
  logic signed [5:0] product_scale;
  logic signed [5:0] unbiased_exp;
  logic signed [5:0] rounded_exp;
  logic signed [5:0] subnormal_scale;

  logic [2:0] leading_bit;
  logic [3:0] normal_sig;
  logic [4:0] rounded_normal_sig;
  logic [3:0] final_normal_sig;
  logic normal_guard;
  logic normal_sticky;
  logic [3:0] biased_exp;
  logic [8:0] rounded_subnormal;

  // Round an eight-bit unsigned integer right by a constant amount. The
  // returned value uses round-to-nearest, ties-to-even.
  function automatic logic [8:0] round_right_rne(
      input logic [7:0] value,
      input logic [3:0] amount
  );
    logic [8:0] truncated;
    logic guard_bit;
    logic sticky_bit;
    begin
      truncated = 9'd0;
      guard_bit = 1'b0;
      sticky_bit = 1'b0;
      case (amount)
        4'd1: begin
          truncated = {2'b00, value[7:1]};
          guard_bit = value[0];
        end
        4'd2: begin
          truncated = {3'b000, value[7:2]};
          guard_bit = value[1];
          sticky_bit = value[0];
        end
        4'd3: begin
          truncated = {4'b0000, value[7:3]};
          guard_bit = value[2];
          sticky_bit = |value[1:0];
        end
        4'd4: begin
          truncated = {5'b00000, value[7:4]};
          guard_bit = value[3];
          sticky_bit = |value[2:0];
        end
        4'd5: begin
          truncated = {6'b000000, value[7:5]};
          guard_bit = value[4];
          sticky_bit = |value[3:0];
        end
        4'd6: begin
          truncated = {7'b0000000, value[7:6]};
          guard_bit = value[5];
          sticky_bit = |value[4:0];
        end
        4'd7: begin
          truncated = {8'b00000000, value[7]};
          guard_bit = value[6];
          sticky_bit = |value[5:0];
        end
        4'd8: begin
          guard_bit = value[7];
          sticky_bit = |value[6:0];
        end
        default: begin
          // A four-bit significand product is smaller than the halfway point
          // when shifted right by nine or more places.
        end
      endcase
      round_right_rne = truncated
          + (guard_bit && (sticky_bit || truncated[0]));
    end
  endfunction

  always_comb begin
    lhs_exp = lhs[6:3];
    rhs_exp = rhs[6:3];
    lhs_frac = lhs[2:0];
    rhs_frac = rhs[2:0];

    result_sign = lhs[7] ^ rhs[7];
    lhs_nan = (lhs_exp == 4'hf) && (lhs_frac == 3'h7);
    rhs_nan = (rhs_exp == 4'hf) && (rhs_frac == 3'h7);
    lhs_zero = (lhs_exp == 4'h0) && (lhs_frac == 3'h0);
    rhs_zero = (rhs_exp == 4'h0) && (rhs_frac == 3'h0);

    // value = significand * 2^scale
    lhs_sig = (lhs_exp == 4'h0) ? {1'b0, lhs_frac}
                                : {1'b1, lhs_frac};
    rhs_sig = (rhs_exp == 4'h0) ? {1'b0, rhs_frac}
                                : {1'b1, rhs_frac};
    lhs_scale = (lhs_exp == 4'h0)
        ? -6'sd9 : $signed({2'b00, lhs_exp}) - 6'sd10;
    rhs_scale = (rhs_exp == 4'h0)
        ? -6'sd9 : $signed({2'b00, rhs_exp}) - 6'sd10;
    product_scale = lhs_scale + rhs_scale;
    sig_product = lhs_sig * rhs_sig;

    casez (sig_product)
      8'b1???????: leading_bit = 3'd7;
      8'b01??????: leading_bit = 3'd6;
      8'b001?????: leading_bit = 3'd5;
      8'b0001????: leading_bit = 3'd4;
      8'b00001???: leading_bit = 3'd3;
      8'b000001??: leading_bit = 3'd2;
      8'b0000001?: leading_bit = 3'd1;
      default:     leading_bit = 3'd0;
    endcase
    unbiased_exp = product_scale + $signed({3'b000, leading_bit});

    normal_sig = 4'd0;
    normal_guard = 1'b0;
    normal_sticky = 1'b0;
    case (leading_bit)
      3'd0: normal_sig = {sig_product[0], 3'b000};
      3'd1: normal_sig = {sig_product[1:0], 2'b00};
      3'd2: normal_sig = {sig_product[2:0], 1'b0};
      3'd3: normal_sig = sig_product[3:0];
      3'd4: begin
        normal_sig = sig_product[4:1];
        normal_guard = sig_product[0];
      end
      3'd5: begin
        normal_sig = sig_product[5:2];
        normal_guard = sig_product[1];
        normal_sticky = sig_product[0];
      end
      3'd6: begin
        normal_sig = sig_product[6:3];
        normal_guard = sig_product[2];
        normal_sticky = |sig_product[1:0];
      end
      default: begin
        normal_sig = sig_product[7:4];
        normal_guard = sig_product[3];
        normal_sticky = |sig_product[2:0];
      end
    endcase

    rounded_normal_sig = {1'b0, normal_sig}
        + (normal_guard && (normal_sticky || normal_sig[0]));
    rounded_exp = unbiased_exp;
    if (rounded_normal_sig[4]) begin
      final_normal_sig = 4'b1000;
      rounded_exp = unbiased_exp + 6'sd1;
    end else begin
      final_normal_sig = rounded_normal_sig[3:0];
    end
    biased_exp = rounded_exp + 6'sd7;

    subnormal_scale = product_scale + 6'sd9;
    case (subnormal_scale)
      6'sd2:  rounded_subnormal = {1'b0, sig_product} << 2;
      6'sd1:  rounded_subnormal = {1'b0, sig_product} << 1;
      6'sd0:  rounded_subnormal = {1'b0, sig_product};
      -6'sd1: rounded_subnormal = round_right_rne(sig_product, 4'd1);
      -6'sd2: rounded_subnormal = round_right_rne(sig_product, 4'd2);
      -6'sd3: rounded_subnormal = round_right_rne(sig_product, 4'd3);
      -6'sd4: rounded_subnormal = round_right_rne(sig_product, 4'd4);
      -6'sd5: rounded_subnormal = round_right_rne(sig_product, 4'd5);
      -6'sd6: rounded_subnormal = round_right_rne(sig_product, 4'd6);
      -6'sd7: rounded_subnormal = round_right_rne(sig_product, 4'd7);
      -6'sd8: rounded_subnormal = round_right_rne(sig_product, 4'd8);
      default: rounded_subnormal = 9'd0;
    endcase

    if (lhs_nan) begin
      // APFloat propagates the first NaN operand, including its sign.
      result = {lhs[7], 7'h7f};
    end else if (rhs_nan) begin
      result = {rhs[7], 7'h7f};
    end else if (lhs_zero || rhs_zero) begin
      result = {result_sign, 7'h00};
    end else if (unbiased_exp < -6'sd6) begin
      if (rounded_subnormal == 9'd0)
        result = {result_sign, 7'h00};
      else if (rounded_subnormal >= 9'd8)
        result = {result_sign, 4'h1, 3'h0};
      else
        result = {result_sign, 4'h0, rounded_subnormal[2:0]};
    end else if ((rounded_exp > 6'sd8)
                 || ((rounded_exp == 6'sd8)
                     && (final_normal_sig > 4'd14))) begin
      // E4M3FN has no infinity. Overflow produces its signed NaN encoding.
      result = {result_sign, 7'h7f};
    end else begin
      result = {result_sign, biased_exp, final_normal_sig[2:0]};
    end
  end
endmodule

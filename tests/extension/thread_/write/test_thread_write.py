from __future__ import absolute_import
from __future__ import print_function
import veriloggen
import thread_write

expected_verilog = """
module test;

  reg CLK;
  reg RST;
  wire [8-1:0] LED;

  blinkled
  uut
  (
    .CLK(CLK),
    .RST(RST),
    .LED(LED)
  );


  initial begin
    CLK = 0;
    forever begin
      #5 CLK = !CLK;
    end
  end


  initial begin
    RST = 0;
    #100;
    RST = 1;
    #100;
    RST = 0;
    #10000;
    $finish;
  end


endmodule



module blinkled
(
  input CLK,
  input RST,
  output reg [8-1:0] LED
);

  reg [32-1:0] th_blink;
  localparam th_blink_init = 0;
  reg [32-1:0] _th_blink_times_0;
  reg [32-1:0] _th_blink_inc_1;
  reg [32-1:0] _th_blink_i_2;
  localparam th_blink_1 = 1;
  localparam th_blink_2 = 2;
  localparam th_blink_3 = 3;
  localparam th_blink_4 = 4;
  localparam th_blink_5 = 5;
  localparam th_blink_6 = 6;
  localparam th_blink_7 = 7;

  always @(posedge CLK) begin
    if(RST) begin
      th_blink <= th_blink_init;
      _th_blink_times_0 <= 0;
      _th_blink_inc_1 <= 0;
      LED <= 0;
      _th_blink_i_2 <= 0;
    end else begin
      case(th_blink)
        th_blink_init: begin
          _th_blink_times_0 <= 10;
          _th_blink_inc_1 <= 10;
          th_blink <= th_blink_1;
        end
        th_blink_1: begin
          LED <= 0;
          th_blink <= th_blink_2;
        end
        th_blink_2: begin
          _th_blink_i_2 <= 0;
          th_blink <= th_blink_3;
        end
        th_blink_3: begin
          if(_th_blink_i_2 < _th_blink_times_0) begin
            th_blink <= th_blink_4;
          end else begin
            th_blink <= th_blink_7;
          end
        end
        th_blink_4: begin
          LED <= LED + _th_blink_inc_1;
          th_blink <= th_blink_5;
        end
        th_blink_5: begin
          $display("led =  %d", LED);
          th_blink <= th_blink_6;
        end
        th_blink_6: begin
          _th_blink_i_2 <= _th_blink_i_2 + 1;
          th_blink <= th_blink_3;
        end
      endcase
    end
  end


endmodule
"""


def test():
    veriloggen.reset()
    test_module = thread_write.mkTest()
    code = test_module.to_verilog()

    from pyverilog.vparser.parser import VerilogParser
    from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
    parser = VerilogParser()
    expected_ast = parser.parse(expected_verilog)
    codegen = ASTCodeGenerator()
    expected_code = codegen.visit(expected_ast)

    assert(expected_code == code)

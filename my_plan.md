# Overal Plan

## $whomai
 - Not an expert on compil, mlir ... :')
 - Louis Ledoux, postdoc team inria emeraude, embeded audio, compil for fpga asic hls
 - but i do digital design, arithmetic, generators of circuits based on IRs
 - I just got a position as Maitre de Conference ~ associate professor in Rennes, IRISA, INRIA, to work on digital design of systolic arrays and small floating point formats
 - an artist, show eurorack, placement art, etc..

## Refresher on digital design

 - Reminders verilog vhdl fsm comb seq
 - Mutli-Stage prism, multi IR
   - the input / upstream IR is verilog and or vhdl, they are interchganble, they are description language like html
   - steps then, they are also IRs, synthesis floorplaning placement
	 - show modern chips, big rectangles are caches, and in between is logic
   - show off mlir/llvm
 - build the machine, not use the machine
 - important topics nowadays, more and more specialized architectures
 - to find these specific arch, their generation (compilation) could use modern comp. tools
 - express and show the concepts, can be seen as dialects
   - modules, wires, seq, comb logic, fsm, etc..
	 - examples in sv / verilog versus schematic
 - HLS and core generator, what is that ? compilation approach to hardware


## MLIR possible ? Yes, CIRCT !
  - What is the upstream, what is the downstream, how it connects with mlir
	- reshow the previous examples but written in CIRCT core dialects
  - graph region
  - DSL -> DSA
  - synth results, PPA

## Hands-on CIRCT tools
	- show the tools wuickly, mention sam, and our previous tutorial
  - similar handson, do roundtrips between verilog and irs, see they are the same, the fma of int, the mult of int
  - obtain some early ppa metrics with the analysis like in sam tuto
  - While they do exercise, i can show once we have the verilog given by firtool or circt-synth/translate how to make a chip, place the verilog in my ORFS hierarchy and run a make, make promotion for OpenRoad, LibreLane, TinyTapeout, the chip i made in gf0p2 with only mlir that has been tapedout

## Let's multiply

  - Santiago de Compostela ... https://www.biblegateway.com/passage/?search=Genesis%201%3A27-29&version=KJ21
  - where this case can com from ? AI, tensor kernels
	- can you do a LUT ? is it worth ?

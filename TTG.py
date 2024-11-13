from ttgLib.TextToGcode import ttg;
a = input()
gcode = ttg(a,1,0,"File",1).toGcode("M02 S500","M05 S0","G0","G1")

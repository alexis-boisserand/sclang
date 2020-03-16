/internal_transition
Main
  #init
    "number = 0"
  @INC --
    "number++"
  @DEC --
    "number--"
  @RES
    ["number < 0"] --
      "number = 1"
    [else] --
      "number = -1"
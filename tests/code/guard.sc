/guard
On
  @TIMEOUT
    ["number == 1"] -> On
    ["number == 2"] -> Off
    ["number == 3"] -> Other
    [else] -> Error
Off
  @PRESS
    ["number == 4"] -> On
Other
  @PRESS -> On
Error
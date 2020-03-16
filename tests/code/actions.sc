/actions
On
  #init
    "numbers[0] = 2"
    "numbers[1] = 2"
    "numbers[2] = 3"
    "numbers[0] = 1"
  #exit
    "numbers[1] = 1"
  @TIMEOUT -> Off
    "numbers[1] = 3"
  @ERROR -> Error
    "numbers[2] = 4"
    "numbers[2] = 4"
Off
  @PRESS
    ["numbers[0] == 2"] -> On
    [else] -> Error
Error
  @RESET -> On
    "numbers[0] = 0"
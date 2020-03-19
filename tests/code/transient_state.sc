/transient_state
<>Init
  ["number == 0"] -> On
  ["number == 2"] -> Other
  [else] -> Other
On
  @RESET -> Init
<>Other
  ["number == 2"] -> Off
  ["number == 1"] -> Error
  [else] -> Init
Off
  @RESET -> Init
Error
  @RESET -> Init
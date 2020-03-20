/composite
#init
  "Init()"
LevelZero
  @EVENT_ONE -> Other/LevelOne
  <>LevelOne
    ["true"] -> Other
    [else] -> ../Other
  Other
    @EVENT_TWO -> ../../composite
    @SOME_EVENT -> What
  What
    Yo
Other
  LevelOne
    @EVENT_ONE -> ../Other
    @SOME -> LevelOneOther
  LevelOneOther
    @event_four -> LevelOne
    @other -> Final
  <>Final
    ["false"] -> LevelOne
    [else] -> LevelOneOther
/composite
#init
  "init_ = 0"
  "exit_ = 0"
@reset -> composite
LevelZero
  #init
    "init_ |= 0x1"
  #exit
    "exit_ |= 0x1"
  LevelOne
    #init
      "init_ |= 0x2"
    #exit
      "exit_ |= 0x2"
    @event_one -> LevelOneTwo
    @event_two -> LevelOneThree
    LevelTwo
      #init
        "init_ |= 0x4"
      #exit
        "exit_ |= 0x4"
      @event_two -> ../LevelOneTwo
      @event_three -> LevelTwoOne
    LevelTwoOne
  LevelOneTwo
  LevelOneThree
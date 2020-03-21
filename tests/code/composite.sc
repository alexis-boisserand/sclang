/composite
LevelZero
  #init
    "init_ |= 0x1"
  #exit
    "exit_ |= 0x1"
  @EVENT_ZERO -> LevelZeroOther
    "action |= 0x1"
  @TO_BOTTOM -> LevelZeroOther/LevelOne
    "action |= 0x2"
  LevelOne
    #init
      "init_ |= 0x2"
    #exit
      "exit_ |= 0x2"
    @EVENT_ONE -> LevelOneOther
      "action |= 0x4"
    LevelTwo
  LevelOneOther
    #init
      "init_ |= 0x4"
    #exit
      "exit_ |= 0x4"
    @EVENT_ONE -> LevelOne
      "action |= 0x8"
LevelZeroOther
  #init
    "init_ |= 0x8"
  #exit
    "exit_ |= 0x8"
  @EVENT_ZERO -> LevelZero
    "action |= 0x10"
  LevelOne
    #init
      "init_ |= 0x10"
    #exit
      "exit_ |= 0x10"
    @EVENT_ONE -> LevelOneOther
      "action |= 0x20"
    @SAME_LEVEL -> ../LevelZero/LevelOne
      "action |= 0x80"
  LevelOneOther
    #init
      "init_ |= 0x20"
    #exit
      "exit_ |= 0x20"
    @EVENT_ONE -> LevelOne
      "action |= 0x100"
    @TO_TOP -> ../LevelZero
      "action |= 0x200"
    @TO_SELF -> LevelOneOther
      "action |= 0x400"
    LevelTwo
      #init
        "init_ |= 0x40"
      #exit
        "exit_ |= 0x40"
      @EVENT_TWO -> ../../LevelZero/LevelOne/LevelTwo
        "action |= 0x800"
      @EVENT_ONE 
        ["true"] -> ../../LevelZero/LevelOne
          "action |= 0x1000"
      @EVENT_ZERO -> ../../LevelZero
        "action |= 0x2000"
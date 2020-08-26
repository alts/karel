DEFINE turn
    LEFT
    LEFT
END

# ------------------------------------------

DEFINE branch
    # >1 ?
    MOVE
    init
    # 1 >1 OR treasure 1 >0
    turn
    # if treasure taken then nothing
    IFMARK MOVE SKIP
    turn
    # >1 1 OR waiting on 1 >0
END

DEFINE branching
    IFWALL SKIP branch
    LEFT
END

# ------------------------------------------

DEFINE init
    IFMARK _init1 _init0
END

DEFINE _init0
    #    ?
    # ? >0 ?
    #    ?
    PUT
    branching
    # could have found treasure and taken it
    IFMARK branching SKIP
    # no sense in going back now
    LEFT
    IFMARK branching SKIP
    # example
    #    1
    # 1 >1 #
    #    1
END

DEFINE _init1
    PICK
    IFMARK treasure PUT
END

# ------------------------------------------

DEFINE treasure
    # in other steps we do nothing on no-mark
    PICK
    # we stay here until main
    # if main sees no mark it puts back treasure
END

DEFINE put_back_treasure
    PUT
    PUT
END

DEFINE treasure_safe_init
   IFMARK branch SKIP
END

DEFINE main
    # see initialize
    init
    turn
    # have not looked this way
    IFWALL SKIP treasure_safe_init
    # may have found treasure
    IFMARK SKIP put_back_treasure
END

RUN main

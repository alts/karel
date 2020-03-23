DEFINE turn
    LEFT
    LEFT
END

# ------------------------------------------

DEFINE branch
    # >1 ?
    MOVE
    IFMARK SKIP init
    # 1 >1
    turn
    MOVE
    turn
    # >1 1
END

# ------------------------------------------

DEFINE init
    # we do NOT care about N
    #    ?
    # N >0 ?
    #    ?
    PUT
    IFWALL SKIP branch
    LEFT
    IFWALL SKIP branch
    turn
    IFWALL SKIP branch
    LEFT
    # example
    #    1
    # N >1 #
    #    1
END

DEFINE main
    # see initialize
    init
    turn
    IFWALL SKIP branch
END

RUN main

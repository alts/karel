DEFINE TURN
    LEFT
    LEFT
END

DEFINE MOVE2
    MOVE
    MOVE
END

# ------------------------------------------

DEFINE ONE_CHECK
    # SKIP never happens right?
    IFMARK PICK                     SKIP
    IFMARK ONE_CHECK_CONTINUE_BACK  RETURN_JURNEY_START
    # if <1+ he goes on else he starts to go back
END

DEFINE ONE_CHECK_CONTINUE_BACK
    # returns the checked off mark and continues going back
    PUT
    GOING_BACK
END

DEFINE GOING_BACK
    # 1 ... <n ... 0 ...#
    MOVE
    ONE_CHECK
END

DEFINE RETURN_JURNEY_START
    # <1 ... 0 ... #
    PUT
    TURN
    RETURN_JURNEY
END

DEFINE RETURN_JURNEY
    # >1 ... 0 ... #
    MOVE
    IFMARK RETURN_JURNEY SKIP
    PUT
END

DEFINE ZERO_REACHED
    # 1 ... >0
    TURN
    GOING_BACK
    PUT
    IFWALL SKIP INIT
END


# ------------------------------------------

DEFINE INIT
    # 1 >0 ... x_n #
    MOVE
    # if there is mark then it seems wrong
    IFMARK SKIP ZERO_REACHED
    # 1 2 ... n #
END

DEFINE START
    # initialize >0 ... #
    PUT
    IFWALL SKIP INIT
    # 1 2 ... n #
END

DEFINE MAIN
    IFMARK SKIP START
END

RUN MAIN

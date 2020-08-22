DEFINE TURN
    LEFT
    LEFT
END

DEFINE STEP2
    STEP
    STEP
END

# ------------------------------------------

# bring marks from next field
DEFINE WHILEPICK
	TAKE
	IFMARK WHILEPICK STEP
    PUT
END

# bring marks from the field 2 steps away
DEFINE WHILEPICK2
	TAKE
	IFMARK WHILEPICK2 STEP2
    PUT
END


# ------------------------------------------
DEFINE PLUS1TO2FIELDS
    # x >y
    PUT
    TURN
    STEP
    PUT
    TURN
    STEP
    # x+1 >y+1
END

# copy marks
DEFINE WHILEPICKCP
    # >x y
	TAKE
    IFMARK WHILEPICKCP STEP
	PLUS1TO2FIELDS
    # x >x+y
END

# ------------------------------------------

DEFINE MINUS2
    IFMARK MINUS2M1 SKIP
END

DEFINE MINUS2M1
    TAKE
    IFMARK TAKE ONEBEHIND
END

DEFINE ONEBEHIND
    # x >y z
    TURN
    STEP
    PUT
    TURN
    STEP
    # x+1 >y z
END

DEFINE DIV2
    # x >y
    MINUS2
    IFMARK DIV2HELPER SKIP
    # if odd (y+z) then (x+1) >(y/2) else x >(y/2)
END

DEFINE DIV2HELPER
    # continue if there are marks
    IFMARK DIV2 SKIP
    # unload marks/2
    PUT
END

# ------------------------------------------

DEFINE MAIN
    # >0 x y
    STEP2
    TURN
    WHILEPICK
    TURN
    # >0 (x+y) 0
    DIV2
    # 1 >((x+y)/2) 0
    WHILEPICKCP
    # 1 >((x+y)/2) ((x+y)/2)
END

RUN MAIN

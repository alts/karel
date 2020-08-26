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
DEFINE WHILE_PICK
	TAKE
	IFMARK WHILE_PICK STEP
    PUT
END

# bring marks from the field 2 steps away
DEFINE WHILE_PICK2
	TAKE
	IFMARK WHILE_PICK2 STEP2
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
DEFINE WHILE_PICK_CP
    # >x y
	TAKE
    IFMARK WHILE_PICK_CP STEP
	PLUS1TO2FIELDS
    # x >x+y
END

# ------------------------------------------

DEFINE MINUS2
    IFMARK MINUS2M1 SKIP
END

DEFINE MINUS2M1
    TAKE
    IFMARK TAKE ONE_BEHIND
END

DEFINE ONE_BEHIND
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
    WHILE_PICK
    TURN
    # >0 (x+y) 0
    DIV2
    # 1 >((x+y)/2) 0
    WHILE_PICK_CP
    # 1 >((x+y)/2) ((x+y)/2)
END

RUN MAIN

DEFINE TURN
    LEFT
    LEFT
END

DEFINE STEP2
    STEP
    STEP
END

# ------------------------------------------

DEFINE WHILE_PICK
	TAKE
    IFMARK WHILE_PICK STEP
    PUT
END

DEFINE WHILE_PICK2
	TAKE
	IFMARK WHILE_PICK2 STEP2
    PUT
END

# ------------------------------------------

DEFINE MAIN
    STEP
    TURN
	WHILE_PICK
    TURN
    STEP2
    TURN
    WHILE_PICK2
END

RUN MAIN

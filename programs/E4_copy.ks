DEFINE turn
    LEFT
    LEFT
END

# ------------------------------------------

DEFINE add_to_two
	PUT
	turn
	MOVE
	PUT
	turn
	MOVE
END

DEFINE while_pick
	# >x y
	PICK
	IFMARK while_pick MOVE
	add_to_two
	# x >y+x
END

# ------------------------------------------

DEFINE main
	while_pick
END

RUN main

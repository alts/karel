DEFINE turn
	PUT
	LEFT
	LEFT
END

DEFINE main
	IFWALL PUT MOVE
	IFWALL turn main
	# go back
	MOVE
END

RUN main

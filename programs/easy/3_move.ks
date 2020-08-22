DEFINE while_take
	PICK
	IFMARK while_take MOVE
	PUT
END

DEFINE main
	IFMARK while_take MOVE
END

RUN main

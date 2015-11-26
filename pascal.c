
PROGRAM TESTE;
	VAR N, K : INTEGER;
	    F1, F2, F3 : INTEGER;
BEGIN
	READ(N);


	WHILE K <= N DO
	BEGIN
		F3 :=  F1 + F2 ;
		F1 := F2;
		F2 := F3;
		K := (K + 1);
	END;

	WRITE(N, F1 + F2, F3);

	IF A < 2 THEN
		A := A + 1;
	ELSE
		B := B -1;
	END;

END;
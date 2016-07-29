This code implements sound changes.

The parameters are:
1) Language: Common Romance (Sp, Fr, Po), Italian, Romanian
2) Second sound change implemented?: 
	Monophthongization = 1
	Only applies to Spanish and Italian
3) TokFreq

Changes:

All:
ae > ɛ
m# > -

Common Romance:
			ī > i				ū > u
			ē, i > e			ō, u > o
			e > ɛ				o > ɔ
					a > a

Romanian
			ī > i				ū, u > u
			ē, i > e			o, o: > ɔ
			e > ɛ				
					a > a

Italian/Romanian
s# > -i > [+pal]

Romanian:
b, w > β > 0

Italian, French
b, w > v

Spanish
b, w > β

Romanian disallows final e (breaks to ea)

-
Max Syllable
	Common Romance: VC CVC (ebos)
	Italian/Romanian: V CV(C) —> allow second C just in case

-

Suffix		Sp.	Fr.	It.		Rom.
ēs		es	es	ei > i		ei > i
em		e	ei > oi	e		ea
ēī		ei	ei > oi	ei > i		ei > i
ērum		ero	ero	ero		eru
ēbus		eβos	evs?	evoi > evo	eui > eu
ē		e	ei > oi	e		ea
us		os	os > s	oi > o		ui
ūs		us	us > s	ui > u?		ui
um		o	o > 0	o		u
uum > ūm	u	u > 0	u		u
uī		oi	oi	oi > o		ui
ibus		eβos	evs?	evoi > evo	eui > eu
ū		u	u > 0	u		u
-		-	-	-		-
ī		i	i > 0	i		i
ōs		os	os > s	oi > o		oi > ui (unstressed)
ōrum		oro	oro	oro		oru
ō		o	o	o		u
īs		is	is > s	ii > i		ii > i
is		es	es > s	ei > i		ei > i
ium		eo	eo	eo		eu
e		e	e	e		ea
a		a	a > ə	a		a > ă
ae		e	e > 0	e		e > ea
am		a	a > ə	a		a > ă
ās		as	as	ai > e		ai > e
ārum		aro	aro	aro		aru
ā		a	a	a		a
ia		ea	ea	ea		ea
ubus		oβos	ovs?	ovoi > ovo	uui > ui
es		es	es > s	ei > i		ei > i
ua		oa	oa	oa		ua
ābus		aβos	avo	avoi > avo	aui > au
eī		ei	ei > oi	ei > i		ei > i
m		-	-	-		-
Tyler Lau
2016.06.24

This is the revised implementation of Lau (2016)

Main Code 2 guesses only ending

~*~

INPUT LAYER
A stem can have a maximum of 36 phonemes (6 syllables, 6 potential phonemes)

Potential phonemes are: p, t, k, b, d, g, f, v, s, z, h, m, n, w, r, l, y, i, u, e, o, a, - (no phoneme)

-

COMMENTS: Back? High? Also lateral to distinguish l and r?

Each phoneme is represented by 11 features, from Chomsky & Halle (1968):
1) Syllabic (Vowels VS Non-Vowels)
2) Consonantal (Consonants VS Glides & Vowels)
3) Voice (Voiced VS Unvoiced)
4) Continuant (Continuants VS Stops/Nasals)
5) Strident (f, v, s, z, VS others)
6) Nasal (m, n VS others)
7) Anterior (front—includes l and r unlike English VS back)
8) ??? (a, o VS others)
9) Grave (u, o, a, schwa, labial, velar VS coronal)
10) Round (w, u, o VS others)
11) ??? (u, a, ptkfsh VS others)
?12) Lateral (l VS others)

36 * 11 = 396 nodes

-

ABOVE SEEMS OFF SO REMADE:

1) Sonorant
2) Vocalic
3) Consonantal
4) Coronal
5) Anterior (in front of palatoalveolar—labial, dental, alveolar)
6) High (Palatals and Velars VS Uvulars and Pharyngeals)
7) Low (Pharyngeals VS Palatals, Velars, uvulars)
8) Back (Velars, Uvulars, Pharyngeals VS Palatals)
9) Nasal 
10) Lateral
11) Continuant
12) Voice
13) Strident (f, v, s, z, VS others)

Round not distinctive
Strident not distinctive

-

8 nodes are used to represent humanness

1 1 1 1 0 0 0 0 —> male human
0 0 0 0 1 1 1 1 —> female human
0 0 0 0 0 0 0 0 —> non-human

-

Original had Slavic gender, but they are irrelevant (12 nodes)

1 1 1 1 0 0 0 0 0 0 0 0 —> masculine
0 0 0 0 1 1 1 1 0 0 0 0 —> feminine
0 0 0 0 0 0 0 0 1 1 1 1 —> neuter

-

Case Frequencies Implemented as how many times case goes into model—estimated by Polinsky and van Everbroeck

		Human				Non-Human
	Sg		Pl		Sg			Pl
Nom	8		3		4			2
Acc	4.5		2.5		7			2
Gen	4		2		2			1

In this instantiation, we get rid of human frequencies, because the token frequency is ALREADY accounted for—humans are already much more common than non-humans.

From Delatte et al 1981:

Raw Numbers:

		Prose				Poetry
	Sg		Pl		Sg			Pl
Nom	27138		8807		14479			3931
Voc	394		210		1849			401
Acc	33532		17906		9177			12421
Gen	15837		8811		5802			1656
Dat	6081		3446		2141			1610
Abl	28485		10446		10860			3994

TOTAL	112026		49626		44585			24015
		161652				68600

By percentage:

		Prose				Poetry
	Sg		Pl		Sg			Pl
Nom	16.79		5.45		21.11			5.73
Voc	0.24		0.13		2.70			5.85
Acc	20.74		11.08		13.38			18.11
Gen	9.80		5.45		8.46			2.41
Dat	3.76		2.13		3.12			2.35
Abl	17.62		6.46		15.83			5.82

By ratio:

		Prose				Poetry
	Sg		Pl		Sg			Pl
Nom	129.23		41.94		36.11			9.80
Voc	1.88		1		4.61			1
Acc	159.68		85.27		22.89			30.98
Gen	75.41		41.96		14.47			4.13
Dat	28.96		16.41		5.34			4.01
Abl	135.64		49.74		27.08			9.96

~*~
		TOTAL		
	Sg		Pl		
Nom	41617		12738					
Voc	2243		611					
Acc	42709		30327					
Gen	21639		10467					
Dat	8222		5056					
Abl	39345		14440	

		230252

~*~
By percentage:		

		TOTAL		
	Sg		Pl		
Nom	18.07		5.53					
Voc	0.97		0.27					
Acc	18.55		13.17					
Gen	9.40		4.55					
Dat	3.57		2.20					
Abl	17.09		6.27			

~*~
By ratio:
		TOTAL		
	Sg		Pl		
Nom	68.11		20.85					
Voc	3.67		1					
Acc	69.90		49.63					
Gen	35.42		17.13					
Dat	13.46		8.27					
Abl	64.39		23.63

~*~
By ratio without vocative:
		TOTAL		
	Sg		Pl		
Nom	8.23		2.52					
Acc	8.45		6.00					
Gen	4.28		2.07					
Dat	1.63		1					
Abl	7.78		2.86

***

Declension Breakdown (Delatte et al 1981)

	Total		Prose		Poetry
1	39,480		27,176		12,304
2	75,965		55,215		20,750
3	86,882		61,428		25,454
4	12,899		9,087		3,812
5	7,119		5,973		1,146
Total	230,252		161,652		68,600

Percentage

	Total		Prose		Poetry
1	17.15		16.81		17.94
2	32.99		34.16		30.25
3	37.73		38.00		37.10
4	5.60		5.62		5.56
5	3.09		3.58		1.67


***

HIDDEN LAYER

30 hidden nodes

***

OUTPUT LAYER

Mapped to four outputs (P&VE only did gender)

Gender (3):
	M: 1 0 0
	F: 0 1 0
	N: 0 0 1

Declension (5):
	I: 1 0 0 0 0
	II: 0 1 0 0 0
	III: 0 0 1 0 0 
	IV: 0 0 0 1 0
	V: 0 0 0 0 1

Number (2):
	SG: 1 0
	PL: 0 1

Case (3):
	If Case Hierarchy implemented (consider Acc closer to Nom and Gen than Nom and Gen to each other)
		Nom: 1 0 0
		Acc: 1 1 0
		Gen: 1 1 1

	If Case Hierarchy not Implemented (all three equidistant)
		Nom: 1 0 0
		Acc: 0 1 0
		Gen: 0 0 1

*******************
RELEVANT PARAMETERS
*******************

Genitive Drop (Gnv)
	If T, genitive is dropped
	If F, genitive is not dropped
Case Hierarchy
Features 1: Changed features to 1 instead of 0.9

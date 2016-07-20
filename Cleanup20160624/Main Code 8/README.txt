This version forces the result to choose the nearest phonological representation to it (limits output possibilities)

1) Consonantal
2) Sonorant
3) Coronal
*) Anterior (in front of palatoalveolar—labial, dental, alveolar)
4) Nasal
5) Continuant
6) Voice

7) Vocalic
8) High (Palatals and Velars VS Uvulars and Pharyngeals)
9) Low (Pharyngeals VS Palatals, Velars, uvulars)
10) Front
11) Back (Velars, Uvulars, Pharyngeals VS Palatals)
*) Round

TO ELIMINATE: 
anterior completely irrelevant
round irrelevant

Distinguishing features:
b = -son, -cnt
m = +son, -cnt
s = -son, +cnt
r = +son, +cnt

For vowels, can NOT be:
lo, frt, bk (both u/o are -lo, -frt, +bk)
CAN be any other combo
- do hi, lo, back, since +lo distinguishes a

NEED frt feature, otherwise:
dist e,a = 2.0 but o,a = 2.8


Originally, 10 was lateral, but because lateral is not a distinctive feature for vowels, which are relevant, we use round

cns = son = cor = ant = nas = cnt = voi = vow = hgh = low = frt = bck = rnd = (0.0, 1.0, -1.0)

phon_to_feat = {
    "p": (cns[1],  son[-1], cor[-1], ant[0], nas[-1], cnt[-1], voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]), 
    "t": (cns[1],  son[-1], cor[1],  ant[1], nas[-1], cnt[-1], voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]),
    "k": (cns[1],  son[-1], cor[-1], ant[0], nas[-1], cnt[-1], voi[-1], vow[-1], hgh[1],  low[-1], frt[0],  bck[0],  rnd[-1]),
    "b": (cns[1],  son[-1], cor[-1], ant[0], nas[-1], cnt[-1], voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]), # RELEVANT
    "d": (cns[1],  son[-1], cor[1],  ant[1], nas[-1], cnt[-1], voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]),
    "g": (cns[1],  son[-1], cor[-1], ant[0], nas[-1], cnt[-1], voi[1],  vow[-1], hgh[1],  low[-1], frt[0],  bck[0],  rnd[-1]),
    "f": (cns[1],  son[-1], cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]), 
    "v": (cns[1],  son[-1], cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]),
    "s": (cns[1],  son[-1], cor[1],  ant[1], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]), # RELEVANT
    "z": (cns[1],  son[-1], cor[1],  ant[1], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]),
    "h": (cns[1],  son[-1], cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]),
    "m": (cns[1],  son[1],  cor[-1], ant[0], nas[1],  cnt[-1], voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]), # RELEVANT
    "n": (cns[1],  son[1],  cor[1],  ant[1], nas[1],  cnt[-1], voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]),
    "N": (cns[1],  son[1],  cor[-1], ant[0], nas[1],  cnt[-1], voi[-1], vow[-1], hgh[1],  low[-1], frt[0],  bck[0],  rnd[-1]), # engma
    "r": (cns[1],  son[1],  cor[1],  ant[1], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]), # RELEVANT
    "l": (cns[1],  son[1],  cor[1],  ant[1], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0],  rnd[-1]),
    "w": (cns[-1], son[1],  cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[1],  low[-1], frt[-1], bck[1],  rnd[1]),
    "j": (cns[-1], son[1],  cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[1],  low[-1], frt[1], bck[-1],  rnd[-1]), # y
    "i": (cns[-1], son[1],  cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[1],  hgh[1],  low[-1], frt[1], bck[-1],  rnd[-1]), # RELEVANT
    "u": (cns[-1], son[1],  cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[1],  hgh[1],  low[-1], frt[-1], bck[1],  rnd[1]),  # RELEVANT
    "e": (cns[-1], son[1],  cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[1],  hgh[-1], low[-1], frt[1], bck[-1],  rnd[-1]), # RELEVANT
    "o": (cns[-1], son[1],  cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[1],  hgh[-1], low[-1], frt[-1], bck[1],  rnd[1]),  # RELEVANT
    "a": (cns[-1], son[1],  cor[-1], ant[0], nas[-1], cnt[1],  voi[-1], vow[1],  hgh[-1], low[1],  frt[-1], bck[-1], rnd[-1]), # RELEVANT
    "-": (0.0,) * 13
}
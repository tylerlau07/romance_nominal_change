 # This program will lay out the Latin corpus as an addendum
# to Polinsky and Van Everbroeck's corpus
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import codecs
import unicodedata as ud
from collections import defaultdict
from math import log

# Argument should be paradigm.txt
f = sys.argv[1]
readdata = codecs.open(f, encoding='utf-8', mode='r')
##readdata2 = open('../Polinsky_VanEverbroeck_2003/latin_corpus', mode='r')
##readdata2 = open('', mode='r')

newlines = []

for line in readdata: # Strip symbols and add each line to the list
    newlines.append(line.strip('\n').split('\t'))

tokens = newlines[1:] # Get rid of first line which is just info

latin_corpus = defaultdict(dict)  # Map Latin word to its info

for token in tokens: # Make dictionary from Latin word to necessary information
    if token[0] in latin_corpus.keys():
        token[0] = token[0] + '2'
    latin_corpus[token[0]]['LatinGender'] = token[1]        # Gender of Latin word
    latin_corpus[token[0]]['MaxFreq'] = token[27]           # Max Frequency in Vulgate
    latin_corpus[token[0]]['MaxFreq10k'] = token[28]        # Frequency per 10k words in Vulgate
    latin_corpus[token[0]]['MinFreq'] = token[29]           # Frequency per 10k words in Vulgate
    latin_corpus[token[0]]['MinFreq10k'] = token[30]        # Frequency per 10k words in Vulgate
    if token[19] == '':
        latin_corpus[token[0]]['SlavGender'] = '?'
    else:
        latin_corpus[token[0]]['SlavGender'] = token[19][0] # Slavic gender of word
    if token[10] == '':
        latin_corpus[token[0]]['RomGender'] = '?'
    else:
        latin_corpus[token[0]]['RomGender'] = token[10][0]  # Romanian gender of word
    latin_corpus[token[0]]['Declension'] = token[2]         # Declension of the noun
    latin_corpus[token[0]]['NomSg'] = token[3]              # Nominative singular of Latin
    latin_corpus[token[0]]['GenSg'] = token[5]              # Genitive singular of Latin
    latin_corpus[token[0]]['AccSg'] = token[7]              # Accusative singular of Latin
    latin_corpus[token[0]]['NomPl'] = token[4]              # Nominative plural of Latin
    latin_corpus[token[0]]['GenPl'] = token[6]              # Genitive plural of Latin
    latin_corpus[token[0]]['AccPl'] = token[8]              # Accusative plural of Latin
    latin_corpus[token[0]]['Origin'] = token[15]            # Language of Origin of word

# Now we need to phonemicize the words
phonemes = {'y':'i','x':'ks','c':'k','j':'y','qu':'kw','th':'t','ch':'k'}

def phonemicize(word):
    phonemicized = ''
    i = 0
    while i < len(word):
        letter = word[i]
        if i != len(word)-1:                                            # Prevent IndexErrors
            if letter+word[i+1] in phonemes.keys():                     # If two letters represent one phoneme, translate that
                phonemicized+=phonemes[letter+word[i+1]]
                i+=2
            elif letter in phonemes.keys():                             
                phonemicized+=phonemes[letter]
                i+=1
            else:
                phonemicized+=letter
                i+=1
        else:                                                           # If at end of word, don't look ahead
            if letter in phonemes.keys():
                phonemicized+=phonemes[letter]
                i+=2
            else:
                phonemicized+=letter
                i+=1
    return phonemicized

# When syllabifying, be wary of "ï" as it must be short
consonant_clusters = ['pr','br','tr','dr','kr','gr','fr',
                      'pl','bl','kl','gl','fl',
                      'ps','kw']

special_clusters = ['sp','sk','st']

diphthongs = {'ae':'ai','au':'au','oe':'oe','ei':'ei','eu':'eu','io':'io'}

long_vowels = {u'ā':u'aa',u'ē':'ee',u'ī':'ii',u'ō':'oo',u'ū':'uu',u'ȳ':'ii'}

consonants = ['p','b','t','d','k','g',
              'f','v','s','z',
              'm','n','l','r','w','y','h']
            
vowels = ['a','e','i','o','u',u'ï']

# Syllabification
# If three consonants in a row and second two NOT in consonant cluster, the first two will be a coda (temptatio)
def syllabify(word):
    syllabified = ''
    build_onset = True
    build_nucleus = False
    build_coda = False
    i = 0
    if word in ['No info','-']:
        syllabified = '------'
        return syllabified
    while i < len(word):
        letter = word[i]
        if build_onset == True:
            if i != len(word)-1:
                if letter in vowels+long_vowels.keys():                     # If a vowel
                    syllabified += '--'
                elif letter+word[i+1] in special_clusters:                  # If sp, st, or sk
                    if i == 0:
                        syllabified += letter+word[i+1]
                        i += 2
                    elif i > 1 and word[i-2]+word[i-1] in diphthongs.keys():    # If preceded by a diphthong
                        syllabified += letter+word[i+1]                       
                        i += 2
                elif letter+word[i+1] in consonant_clusters:                  # If there is a consonant cluster
                    syllabified += letter+word[i+1]
                    i += 2
                elif letter in consonants:                                  # If there is a single consonant
                    syllabified += letter+'-'
                    i += 1
            else:
                syllabified += '--'                                     # Must be either a nucleus or coda
            build_onset = False
            build_nucleus = True
        elif build_nucleus == True:
            if i != len(word)-1:                                        # Avoid Index Errors
                if letter+word[i+1] in diphthongs.keys():               # If there is a diphthong
                    syllabified += diphthongs[letter+word[i+1]]
                    if i+2 == len(word):
                        syllabified += '--'
                    i += 2
                elif letter in long_vowels.keys():                      # If there is a long vowel
                    syllabified += long_vowels[letter]
                    i += 1
                elif letter == u'ï':
                    syllabified += 'i'+'-'
                    i += 1
                elif letter in vowels:                                  # If it a vowel
                    syllabified += letter+'-'
                    i += 1
            else:
                if letter in long_vowels.keys():                        # If there is a long vowel
                    syllabified += long_vowels[letter]+'--'
                    i += 1
                elif letter in vowels:                                  # If it a vowel
                    syllabified += letter+'---'
                    i += 1
                else:                                                   # Then it is a conosnant
                    syllabified += '--'
            build_nucleus = False
            build_coda = True
        elif build_coda == True:
            if letter in vowels+long_vowels.keys():                     # Then no coda
                syllabified += '--'
            elif i == len(word)-1:                                      # Then it is the last letter
                syllabified += '-'+letter
                i += 1
            else:                                                       # If it is not the last leter
                if i == len(word)-2:                                    # If second to last letter
                    if word[i+1] in consonants:                         # Then complex coda
                        syllabified += letter+word[i+1]
                        i += 2
                    else:                                               # Then the last letter is a vowel and it must be an onset
                        syllabified += '--'
                else:
                    if word[i+1]+word[i+2] in consonant_clusters:       # Then it must be a coda
                        syllabified += '-'+letter
                        i += 1
                    elif (i > 1 and word[i-2]+word[i-1] in diphthongs.keys()) and (letter+word[i+1] in special_clusters): # Such as aistas (ai.stas)
                        syllabified += '--'
                    elif letter+word[i+1] in consonant_clusters:        # Then it is an onset
                        syllabified += '--'
                    elif word[i+1] in consonants:                       # Then the coda consists of two consonants
                        if word[i+2] in consonants:
                            syllabified += letter+word[i+1]
                            i += 2
                        else:                         
                            syllabified += '-'+letter
                            i += 1
                    elif word[i+1] in vowels+long_vowels.keys():        # Then it must be an onset
                        syllabified += '--'
            build_coda = False
            build_onset = True
            if i >= len(word):
                continue
            else: syllabified += '\t'
    return syllabified

# Now phonemicize
for word in sorted(latin_corpus.keys()):
    latin_corpus[word]['NomSg'] = phonemicize(latin_corpus[word]['NomSg'])
    latin_corpus[word]['GenSg'] = phonemicize(latin_corpus[word]['GenSg'])
    latin_corpus[word]['AccSg'] = phonemicize(latin_corpus[word]['AccSg'])
    latin_corpus[word]['NomPl'] = phonemicize(latin_corpus[word]['NomPl'])
    latin_corpus[word]['GenPl'] = phonemicize(latin_corpus[word]['GenPl'])
    latin_corpus[word]['AccPl'] = phonemicize(latin_corpus[word]['AccPl'])
    # Figure out the root (FIX)
    if latin_corpus[word]['NomSg'] != 'No info':
        if latin_corpus[word]['Declension'] == '1': latin_corpus[word]['Root'] = latin_corpus[word]['GenSg'][:-2]
        elif latin_corpus[word]['Declension'] == '2': latin_corpus[word]['Root'] = latin_corpus[word]['GenSg'][:-1]
        elif latin_corpus[word]['Declension'] == '3': latin_corpus[word]['Root'] = latin_corpus[word]['GenSg'][:-2]
        elif latin_corpus[word]['Declension'] == '4': latin_corpus[word]['Root'] = latin_corpus[word]['GenSg'][:-2]
        elif latin_corpus[word]['Declension'] == '5': latin_corpus[word]['Root'] = latin_corpus[word]['GenSg'][:-2]
        
declension = defaultdict(list)

# Now syllabify
for word in sorted(latin_corpus.keys()):
    declension[word].append(syllabify(latin_corpus[word]['NomSg']))
    gensg = latin_corpus[word]['GenSg']
    if '/' in gensg:
        for genform in gensg.split('/'):
            if '*' in genform:
                gensg = genform[:-1]
            elif genform[-2] in ['e',u'ē']:
                gensg = genform
    declension[word].append(syllabify(gensg))
    accsg = latin_corpus[word]['AccSg']
    if '/' in accsg:
        for accform in accsg.split('/'):
            if '*' in accform:
                accsg = accform[:-1]
            elif accform[-2] in ['e',u'ē']:
                accsg = accform
    declension[word].append(syllabify(accsg))
    declension[word].append(syllabify(latin_corpus[word]['NomPl']))
    genpl = latin_corpus[word]['GenPl']
    if '/' in genpl:
        for genform in genpl.split('/'):
            if '*' in genform:
                genpl = genform[:-1]
            elif genform[-2] in ['e',u'ē']:
                genpl = genform
    declension[word].append(syllabify(genpl))
    accpl = latin_corpus[word]['AccPl']
    if '/' in accpl:
        for accform in accpl.split('/'):
            if '*' in accform:
                accpl = accform[:-1]
            elif accform[-2] in ['e',u'ē']:
                accpl = accform
    declension[word].append(syllabify(accpl))
    
## Build how the declensions should look
writedata = open('latincorpus_add.txt', 'w')

i_to_case = {0:'nomsg',1:'gensg',2:'accsg',3:'nompl',4:'genpl',5:'accpl'}
wordinfo = defaultdict(dict)
counter = 0
for base in sorted(declension.keys()):
    writedata.write('_\t'+base+'\t'+latin_corpus[base]['LatinGender']+'\t'+latin_corpus[base]['MaxFreq']+'\t'+latin_corpus[base]['MaxFreq10k']+'\t')
    if latin_corpus[base]['MaxFreq'] != '?':
        writedata.write(str(log(int(latin_corpus[base]['MaxFreq'].replace(',',''))))) # Turn string to integer without commas so log can be taken, then turn to string again
    else:
        writedata.write('?')
##        writedata.write(str(log(2)))    # Artificially give frequency of "2", very small
    writedata.write('\t'+latin_corpus[base]['SlavGender']+'\t'+latin_corpus[base]['RomGender']+'\t'+latin_corpus[base]['Declension']+'\n')
    maxlength = len(max(declension[base],key=len).split('\t'))  # This gives us the max length that we can build back from
    for i in range(0,len(declension[base])):
        form = declension[base][i]
        formlength = len(form.split('\t'))
        length_diff = maxlength - formlength            # This gives us the difference and tells us how many ------ to build back
        difffrom6 = 6-maxlength                         # So we know how many ------ to build in front                                
        form += '\t------'*length_diff
        form = '------\t'*difffrom6 + form
        form += '\t'+i_to_case[i]+'\t------\t------\t------\n'
        writedata.write(form)
        

counts = {'D1':0,'D2':0,'D3':0,'D4':0,'D5':0,
              'm':0,'f':0,'n':0,
              'mD1':0,'mD2':0,'mD3':0,'mD4':0,'mD5':0,
              'fD1':0,'fD2':0,'fD3':0,'fD4':0,'fD5':0,
              'nD1':0,'nD2':0,'nD3':0,'nD4':0,'nD5':0,
              'mD1info':0,'mD2info':0,'mD3info':0,'mD4info':0,'mD5info':0,
              'fD1info':0,'fD2info':0,'fD3info':0,'fD4info':0,'fD5info':0,
              'nD1info':0,'nD2info':0,'nD3info':0,'nD4info':0,'nD5info':0,
              'mm':0,'mf':0,'mn':0,'fm':0,'ff':0,'fn':0,'nm':0,'nf':0,'nn':0,'m?':0,'f?':0,'n?':0,
              'mm1':0,'mf1':0,'mn1':0,'fm1':0,'ff1':0,'fn1':0,'nm1':0,'nf1':0,'nn1':0,'m?1':0,'f?1':0,'n?1':0,
              'mm2':0,'mf2':0,'mn2':0,'fm2':0,'ff2':0,'fn2':0,'nm2':0,'nf2':0,'nn2':0,'m?2':0,'f?2':0,'n?2':0,
              'mm3':0,'mf3':0,'mn3':0,'fm3':0,'ff3':0,'fn3':0,'nm3':0,'nf3':0,'nn3':0,'m?3':0,'f?3':0,'n?3':0,
              'mm4':0,'mf4':0,'mn4':0,'fm4':0,'ff4':0,'fn4':0,'nm4':0,'nf4':0,'nn4':0,'m?4':0,'f?4':0,'n?4':0,
              'mm5':0,'mf5':0,'mn5':0,'fm5':0,'ff5':0,'fn5':0,'nm5':0,'nf5':0,'nn5':0,'m?5':0,'f?5':0,'n?5':0,
              'romm':0,'romf':0,'romn':0,'rom?':0,
              'total':0, 'totinfo':0}

for base in sorted(declension.keys()):
    rom = latin_corpus[base]['RomGender']
    latin = latin_corpus[base]['LatinGender']
    etym = latin_corpus[base]['Origin']
    dec = latin_corpus[base]['Declension']
    if dec != 'No info':
        counts['total'] += 1
        counts['D'+dec] += 1
        counts[latin[0]] += 1
        counts[latin[0]+'D'+dec] += 1
        if rom != '?' and 'l' in etym:
            counts['totinfo'] += 1
            counts[latin[0]+rom] += 1
            counts['rom'+rom] += 1
            counts[latin[0]+rom+dec] += 1
            counts[latin[0]+'D'+dec+'info'] += 1

minfo = counts['mm']+counts['mf']+counts['mn']
finfo = counts['fm']+counts['ff']+counts['fn']
ninfo = counts['nm']+counts['nf']+counts['nn']

print 'Percent Declension I Nouns that were M:\t%s' % str(float(counts['mD1'])/float(counts['D1']))
print 'Percent Declension I Nouns that were F:\t%s' % str(float(counts['fD1'])/float(counts['D1']))
print 'Percent Declension I Nouns that were N:\t%s\n-' % str(float(counts['nD1'])/float(counts['D1']))

print 'Percent Declension II Nouns that were M:\t%s' % str(float(counts['mD2'])/float(counts['D2']))
print 'Percent Declension II Nouns that were F:\t%s' % str(float(counts['fD2'])/float(counts['D2']))
print 'Percent Declension II Nouns that were N:\t%s\n-' % str(float(counts['nD2'])/float(counts['D2']))

print 'Percent Declension III Nouns that were M:\t%s' % str(float(counts['mD3'])/float(counts['D3']))
print 'Percent Declension III Nouns that were F:\t%s' % str(float(counts['fD3'])/float(counts['D3']))
print 'Percent Declension III Nouns that were N:\t%s\n-' % str(float(counts['nD3'])/float(counts['D3']))

print 'Percent Declension IV Nouns that were M:\t%s' % str(float(counts['mD4'])/float(counts['D4']))
print 'Percent Declension IV Nouns that were F:\t%s' % str(float(counts['fD4'])/float(counts['D4']))
print 'Percent Declension IV Nouns that were N:\t%s\n-' % str(float(counts['nD4'])/float(counts['D4']))

print 'Percent Declension V Nouns that were M:\t%s' % str(float(counts['mD5'])/float(counts['D5']))
print 'Percent Declension V Nouns that were F:\t%s' % str(float(counts['fD5'])/float(counts['D5']))
print 'Percent Declension V Nouns that were N:\t%s\n-' % str(float(counts['nD5'])/float(counts['D5']))

print 'Percent Declension I Nouns:\t%s' % str(float(counts['D1'])/float(counts['total']))
print 'Percent Declension II Nouns:\t%s' % str(float(counts['D2'])/float(counts['total']))
print 'Percent Declension III Nouns:\t%s' % str(float(counts['D3'])/float(counts['total']))
print 'Percent Declension IV Nouns:\t%s' % str(float(counts['D4'])/float(counts['total']))
print 'Percent Declension V Nouns:\t%s\n-' % str(float(counts['D5'])/float(counts['total']))

print 'Percent M to M:\t%s' % str(float(counts['mm']/float(minfo)))
print 'Percent M to F:\t%s' % str(float(counts['mf']/float(minfo)))
print 'Percent M to N:\t%s' % str(float(counts['mn']/float(minfo)))
print 'Percent M to ?:\t%s' % str(float(counts['m?']/float(counts['m'])))
print 'Percent F to M:\t%s' % str(float(counts['fm']/float(finfo)))
print 'Percent F to F:\t%s' % str(float(counts['ff']/float(finfo)))
print 'Percent F to N:\t%s' % str(float(counts['fn']/float(finfo)))
print 'Percent F to ?:\t%s' % str(float(counts['f?']/float(counts['f'])))
print 'Percent N to M:\t%s' % str(float(counts['nm']/float(ninfo)))
print 'Percent N to F:\t%s' % str(float(counts['nf']/float(ninfo)))
print 'Percent N to N:\t%s' % str(float(counts['nn']/float(ninfo)))
print 'Percent N to ?:\t%s\n-' % str(float(counts['n?']/float(counts['n'])))

print 'Percent M to M in Declension 1:\t%s' % str(float(counts['mm1']/float(counts['mD1info'])))
print 'Percent M to F in Declension 1:\t%s' % str(float(counts['mf1']/float(counts['mD1info'])))
print 'Percent M to N in Declension 1:\t%s' % str(float(counts['mn1']/float(counts['mD1info'])))
print 'Percent M to ? in Declension 1:\t%s' % str(float(counts['m?1']/float(counts['mD1'])))
print 'Percent F to M in Declension 1:\t%s' % str(float(counts['fm1']/float(counts['fD1info'])))
print 'Percent F to F in Declension 1:\t%s' % str(float(counts['ff1']/float(counts['fD1info'])))
print 'Percent F to N in Declension 1:\t%s' % str(float(counts['fn1']/float(counts['fD1info'])))
print 'Percent F to ? in Declension 1:\t%s\n-' % str(float(counts['f?1']/float(counts['fD1'])))
##    print 'Percent N to M in Declension 1:\t%s' % str(float(counts['nm1']/float(counts['nD1']-counts['n?1'])))
##    print 'Percent N to F in Declension 1:\t%s' % str(float(counts['nf1']/float(counts['nD1']-counts['n?1'])))
##    print 'Percent N to N in Declension 1:\t%s' % str(float(counts['nn1']/float(counts['nD1']-counts['n?1'])))
##    print 'Percent N to ? in Declension 1:\t%s' % str(float(counts['n?1']/float(counts['nD1'])))

print 'Percent M to M in Declension 2:\t%s' % str(float(counts['mm2']/float(counts['mD2info'])))
print 'Percent M to F in Declension 2:\t%s' % str(float(counts['mf2']/float(counts['mD2info'])))
print 'Percent M to N in Declension 2:\t%s' % str(float(counts['mn2']/float(counts['mD2info'])))
print 'Percent M to ? in Declension 2:\t%s' % str(float(counts['m?2']/float(counts['mD2'])))
print 'Percent F to M in Declension 2:\t%s' % str(float(counts['fm2']/float(counts['fD2info'])))
print 'Percent F to F in Declension 2:\t%s' % str(float(counts['ff2']/float(counts['fD2info'])))
print 'Percent F to N in Declension 2:\t%s' % str(float(counts['fn2']/float(counts['fD2info'])))
print 'Percent F to ? in Declension 2:\t%s' % str(float(counts['f?2']/float(counts['fD2'])))
print 'Percent N to M in Declension 2:\t%s' % str(float(counts['nm2']/float(counts['nD2info'])))
print 'Percent N to F in Declension 2:\t%s' % str(float(counts['nf2']/float(counts['nD2info'])))
print 'Percent N to N in Declension 2:\t%s' % str(float(counts['nn2']/float(counts['nD2info'])))
print 'Percent N to ? in Declension 2:\t%s\n-' % str(float(counts['n?2']/float(counts['nD2'])))


print 'Percent M to M in Declension 3:\t%s' % str(float(counts['mm3']/float(counts['mD3info'])))
print 'Percent M to F in Declension 3:\t%s' % str(float(counts['mf3']/float(counts['mD3info'])))
print 'Percent M to N in Declension 3:\t%s' % str(float(counts['mn3']/float(counts['mD3info'])))
print 'Percent M to ? in Declension 3:\t%s' % str(float(counts['m?3']/float(counts['mD3'])))
print 'Percent F to M in Declension 3:\t%s' % str(float(counts['fm3']/float(counts['fD3info'])))
print 'Percent F to F in Declension 3:\t%s' % str(float(counts['ff3']/float(counts['fD3info'])))
print 'Percent F to N in Declension 3:\t%s' % str(float(counts['fn3']/float(counts['fD3info'])))
print 'Percent F to ? in Declension 3:\t%s' % str(float(counts['f?3']/float(counts['fD3'])))
print 'Percent N to M in Declension 3:\t%s' % str(float(counts['nm3']/float(counts['nD3info'])))
print 'Percent N to F in Declension 3:\t%s' % str(float(counts['nf3']/float(counts['nD3info'])))
print 'Percent N to N in Declension 3:\t%s' % str(float(counts['nn3']/float(counts['nD3info'])))
print 'Percent N to ? in Declension 3:\t%s\n-' % str(float(counts['n?3']/float(counts['nD3'])))


print 'Percent M to M in Declension 4:\t%s' % str(float(counts['mm4']/float(counts['mD4info'])))
print 'Percent M to F in Declension 4:\t%s' % str(float(counts['mf4']/float(counts['mD4info'])))
print 'Percent M to N in Declension 4:\t%s' % str(float(counts['mn4']/float(counts['mD4info'])))
print 'Percent M to ? in Declension 4:\t%s' % str(float(counts['m?4']/float(counts['mD4'])))
print 'Percent F to M in Declension 4:\t%s' % str(float(counts['fm4']/float(counts['fD4info'])))
print 'Percent F to F in Declension 4:\t%s' % str(float(counts['ff4']/float(counts['fD4info'])))
print 'Percent F to N in Declension 4:\t%s' % str(float(counts['fn4']/float(counts['fD4info'])))
print 'Percent F to ? in Declension 4:\t%s' % str(float(counts['f?4']/float(counts['fD4'])))
print 'Percent N to M in Declension 4:\t%s' % str(float(counts['nm4']/float(counts['nD4info'])))
print 'Percent N to F in Declension 4:\t%s' % str(float(counts['nf4']/float(counts['nD4info'])))
print 'Percent N to N in Declension 4:\t%s' % str(float(counts['nn4']/float(counts['nD4info'])))
print 'Percent N to ? in Declension 4:\t%s\n-' % str(float(counts['n?4']/float(counts['nD4'])))


print 'Percent M to M in Declension 5:\t%s' % str(float(counts['mm5']/float(counts['mD5info'])))
print 'Percent M to F in Declension 5:\t%s' % str(float(counts['mf5']/float(counts['mD5info'])))
print 'Percent M to N in Declension 5:\t%s' % str(float(counts['mn5']/float(counts['mD5info'])))
print 'Percent M to ? in Declension 5:\t%s' % str(float(counts['m?5']/float(counts['mD5'])))
print 'Percent F to M in Declension 5:\t%s' % str(float(counts['fm5']/float(counts['fD5info'])))
print 'Percent F to F in Declension 5:\t%s' % str(float(counts['ff5']/float(counts['fD5info'])))
print 'Percent F to N in Declension 5:\t%s' % str(float(counts['fn5']/float(counts['fD5info'])))
print 'Percent F to ? in Declension 5:\t%s\n-' % str(float(counts['f?5']/float(counts['fD5'])))

print 'Total number of Latin nouns with Romanian reflexes:\t%s' % str(counts['totinfo'])
print minfo
print finfo
print ninfo
print counts['mD1info']
print counts['mD2info']
print counts['mD3info']
print counts['mD4info']
print counts['mD5info']
print counts['fD1info']
print counts['fD2info']
print counts['fD3info']
print counts['fD4info']
print counts['fD5info']
print counts['nD1info']
print counts['nD2info']
print counts['nD3info']
print counts['nD4info']
print counts['nD5info']

##for word in sorted(latin_corpus.keys()):              # This checks how many consonants you can have in a row
##    consonantsinrow = ''
##    for letter in latin_corpus[word]['NomSg']:
##        if letter in consonants:
##            consonantsinrow += letter
##        elif letter in (vowels+long_vowels.keys()):
##            if len(consonantsinrow) >= 3:
##                print word, consonantsinrow
##            consonantsinrow = ''
    
##    for letter in latin_corpus[word]['NomSg']:        # Just to check what phonemes there are
##        if word == 'filius':
##            print letter
##        if letter not in letters:
##            letters.append(letter)
##print letters

# This program will search up the paradigms of the Latin genders online and return
# the nominative, genitive, and accusative in both the singular and plural
# as well as the max frequencies per 10,000 words in the Latin Vulgate corpus

import urllib2
import urllib
import html5lib
import json
import sys
import re
import HTMLParser
import unicodedata
from bs4 import BeautifulSoup
from collections import defaultdict

# This function searches for a string between strings
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# This function looks up the webpage with the word as the search term
def nouninfo(word):
    request = urllib2.urlopen(urllib2.Request('http://en.wiktionary.org/w/api.php', urllib.urlencode({'action':'query', 'titles':word, 'format':'json'})))
    pageno = json.loads(request.read())['query']['pages'].keys()[0] # Get the page number of the wiktionary page needed
    latinexist = 'No'
    nounexist = 'No'
    multiplenouns = 'No'
    soup = ''
    if pageno != '-1': # Create the environment to ONLY look at the Latin section
        newrequest = urllib2.urlopen(urllib2.Request('http://en.wiktionary.org/w/api.php', urllib.urlencode({'action':'parse','pageid':pageno,'format':'json'})))    # Now we get the actual page with the conjugation info
        html = json.loads(newrequest.read())['parse']['text']['*'] # This gets the info we need
        if BeautifulSoup(html,'html5lib').find('span',attrs={'id':'Latin'}) != None: # See if there is Latin info
            latinexist = 'Yes'
            if find_between(html,'<span class="mw-headline" id="Latin">','<h2') == '': # If Latin is the last section
                latin_env = html[html.index('span class="mw-headline" id="Latin">'):]
            else: latin_env = find_between(html,'span class="mw-headline" id="Latin">','<h2')
##            print latin_env
            if len(BeautifulSoup(latin_env,'html5lib').findAll('span',attrs={'id':re.compile('Noun(_\d)?')})) != 0: # Now we need to find the Noun section
                nounexist = 'Yes'
                if len(BeautifulSoup(latin_env,'html5lib').findAll('span',attrs={'id':re.compile('Noun(_\d)?')})) > 1: # There may be multiple instances of the noun
                    multiplenouns = 'Yes'
                headertype = re.search('<h\d>.*<span class="mw-headline" id="Noun',latin_env).group()[2] # Gets the header type of the noun so we know where to go up to
                if find_between(latin_env,'<span class="mw-headline" id="Noun','<h'+headertype+'>') == '':  # If Noun is the last section
                    noun_env = latin_env[latin_env.index('<span class="mw-headline" id="Noun'):]
                else: noun_env = find_between(latin_env,'<span class="mw-headline" id="Noun','<h'+headertype+'>')
                soup = BeautifulSoup(noun_env,'html5lib')
    return pageno, latinexist, nounexist, multiplenouns, soup

# This function searches the Perseus corpus for the proper definition
def findperseuspage(word,deflist):      # Make definitions into list
    defpage = urllib2.urlopen('http://www.perseus.tufts.edu/hopper/morph?l='+word+'&la=la') # Gives frequencies
    check_def = defpage.read()
##    print BeautifulSoup(check_def)
    freqpage = ''
    perseusdefs = BeautifulSoup(check_def,'html5lib').findAll('span',attrs={'class':'lemma_definition'})
##    print BeautifulSoup(check_def,'html5lib').findAll('h4',attrs={'class':'la'})
    if word == 'vallis': return 'http://www.perseus.tufts.edu/hopper/wordfreq?lang=la&lookup='+word # Cheap fix for vallis, where the first definition is correct
    if len(perseusdefs) != 0:
        if len(perseusdefs) == 1:
            freqpage = 'http://www.perseus.tufts.edu/hopper/wordfreq?lang=la&lookup='+word # If there is only one definition, then give that as the page
        else:
            for definition in deflist:
                for defchoice in BeautifulSoup(check_def,'html5lib').findAll('span',attrs={'class':'lemma_definition'}):    # Find all the definitions
                    edited = defchoice.next.strip().strip(':;').replace('\n','')                                                        
                    while '  ' in edited:                                                                                   # Remove all whitespace
                        edited = edited.replace('  ',' ')
                    if definition+',' in HTMLParser.HTMLParser().unescape(edited).encode('utf8')+',' or definition+' (' in HTMLParser.HTMLParser().unescape(edited).encode('utf8'):
                        defno = BeautifulSoup(check_def,'html5lib').findAll('span',attrs={'class':'lemma_definition'}).index(defchoice)
                        correctdef = BeautifulSoup(check_def,'html5lib').findAll('h4',attrs={'class':'la'})[defno].next
                        freqpage = 'http://www.perseus.tufts.edu/hopper/wordfreq?lang=la&lookup='+str(correctdef)
                        break
            if freqpage == '': return 'Definitions do not match'
    return freqpage

# This function searches the Perseus corpus for the frequency of the given word
def getperseusfreq(word,page):
    maxfreq = '?'
##    freq10k = '?'
    minfreq = '?'
    minfreq10k = '?'
    if page not in ['','Definitions do not match']:
        check_freq = urllib2.urlopen(page).read()                                                       # Look for the frequency info
        soup = BeautifulSoup(check_freq,'html5lib')
        if soup.find('a',attrs={'href':'text?doc=Perseus:text:1999.02.0060'}) != None:                  # Check that Vulgate frequency exists                                                  
            maxfreq = soup.find('tr',attrs={'class':'even'}).findAll('td')[1].next.next                 # Embedded in the first <td> tag is the MaxFreq
##            freq10k = soup.find('tr',attrs={'class':'even'}).findAll('td')[2].next                    # The second <td> tag is the one with the MaxFreq/10k
            minfreq = soup.find('tr',attrs={'class':'even'}).findAll('td')[3].next                      # Third one is the minimum frequency
            minfreq10k = soup.find('tr',attrs={'class':'even'}).findAll('td')[4].next                   # Fourth one is the minimum frequency per 10k
    return maxfreq, minfreq, minfreq10k          

# This class takes the root and finds the necessary information
class Root:
    def __init__(self,word,definition,section):     # Give the word, the definition, and use nouninfo(word) to get the Noun section
	self.word = word
	self.definition = definition
	self.nounsection = section
    def gen(self):
        gender = 'No info'
        for token in self.nounsection.findAll('strong',attrs={'lang':'la'}):
            if self.nounsection.find('strong',attrs={'lang':'la'}).findNext('abbr') != None:                # If there is gender info
                gender = self.nounsection.find('strong',attrs={'lang':'la'}).findNext('abbr').next
            else:
                continue
        return gender
    def dec(self):
        declension = 'No info'
        decenv = re.compile('Appendix:Latin ((first)|(second)|(third)|(fourth)|(fifth)) declension')
        if self.nounsection.find('a',attrs={'title':decenv}) != None:                                       # If there is declension info
            declension = self.nounsection.find('a',attrs={'title':decenv}).next
        return declension
    def cases(self):
        case_to_form = defaultdict(list)                                                                    # Make a dictionary of the cases to the sg. and pl. forms
        singnotexist = False
        plnotexist = False
        nom = ['-','-']
        gen = ['-','-']
        acc = ['-','-']
        if self.nounsection.find('table',attrs={'class':'prettytable inflection-table'}) != None:               # If there is an inflection available
            inflection_table = self.nounsection.find('table',attrs={'class':'prettytable inflection-table'})
            if 'Singular' not in str(inflection_table): singnotexist = True                                     # If the singular paradigm is missing
            if 'Plural' not in str(inflection_table): plnotexist = True                                         # If the plural paradigm is missing
            for caseenv in inflection_table.findAll('tr'):
                if caseenv.th.a == None:                                                                    # Skip the first part which just has the number info
                    next
                else:
                    for formenv in caseenv.findAll('span'):                         
                        if singnotexist == True: case_to_form[caseenv.th.a.next].append('-')            
                        case_to_form[caseenv.th.a.next].append(formenv.a.next)                              # Append the case forms
                        if plnotexist == True: case_to_form[caseenv.th.a.next].append('-')
            nom = case_to_form['nominative']
            gen = case_to_form['genitive']
            acc = case_to_form['accusative']
        return nom, gen, acc
    def freq(self):
        freqpage = findperseuspage(self.word,self.definition)
        freq10k = getperseusfreq(self.word,freqpage)
        return freq10k

f = sys.argv[1]
readdata = open(f, mode='r')

# Now we take the words and genders and convert them into a dictionary
newlines = []

for line in readdata: # Strip symbols and add each line to the list
    newlines.append(line.strip('\n').split('\t'))

tokens = newlines[1:] # Get rid of first line which is just info

latin_words = defaultdict(dict)    # Collects the Latin words

for token in tokens: # Make dictionary from Latin word to Latin and Romanian genders
    if ',' in token[0]:
        token[0] = token[0][:token[0].index(',')]
    token[0] = re.sub('\(sg\)|\(pl\)','',token[0])  # Get rid of singular and plural notes
    token[0] = re.sub('\(|\)','',token[0])          # Get rid of other parentheses
    i = 1                                           # Set i to 0 to count how many homophones there are
    while token[0] in latin_words.keys():           # Add i until you get no homophone
        i += 1
        token[0] = token[0]+str(i)                  # For example, we have frons, so change to frons2
    if token[0] not in ['pascuum','equus']:                         # Pascuum and Equus seem to be the only word in our database with a true double u
        token[0] = re.sub('aa','a',token[0])
        token[0] = re.sub('ee','e',token[0])
        token[0] = re.sub('ii','i',token[0])
        token[0] = re.sub('oo','o',token[0])
        token[0] = re.sub('uu','u',token[0])
        token[0] = re.sub('yy','y',token[0])
    latin_words[token[0]]['LatinGender'] = token[1].lower()         # The gender of the word in Latin
    latin_words[token[0]]['RomanianGender'] = token[2].lower()      # The gender of the word in Romanian
    latin_words[token[0]]['SlavicGender'] = token[3].lower()        # The gender of the word in Proto-Slavic
    latin_words[token[0]]['EnglishDef'] = token[4]                  # The English definition of the word
    latin_words[token[0]]['RomanianSg'] = token[6].lower()          # The modern Romanian singular form
    latin_words[token[0]]['RomanianPl'] = token[7].lower()          # The modern Romanian plural form
    latin_words[token[0]]['OlderRom'] = token[8].lower()            # The older Romanian form according to the source we have
    latin_words[token[0]]['OldestRom'] = token[9].lower()           # The oldest Romanian form according to the source we have
    latin_words[token[0]]['OrigLang'] = token[12].lower()           # What language it is borrowed from (or inherited if Latin)
    latin_words[token[0]]['UnsureCognate'] = token[14].lower()      # * if we are unsure that it is a cognate
    latin_words[token[0]]['ChangedMeaning'] = token[15].lower()     # If the Romanian word has a different meaning from the original language
    latin_words[token[0]]['SlavicWord'] = token[16].lower()         # The Slavic word with the same meaning
    latin_words[token[0]]['SlavicNote'] = token[17].lower()         # Any notes about the Slavic word, possible meanings
    latin_words[token[0]]['NewWord'] = token[21].lower()            # Words that are added to Polinsky and Everbroeck's original list have a *

##print Root('aer',['ligature'],nouninfo('aer')[4]).cases()     # Use this to test specific words
##
### Now we get the info for the words
##for word in sorted(latin_words.keys()):
##    print word
##    definition = latin_words[word]['EnglishDef'].replace(';',',').split(', ')
##    # Need to change the searches for some token[0]s as they are plural and won't show up
##    if word == 'bonum': newword = 'bonus'                                 
##    elif word == 'castella': newword = 'castellum' 
##    elif word == 'daemonia': newword = 'daemonium'
##    elif word == 'deserta': newword = 'desertus'
##    elif word == 'fores': newword = 'foris'
##    elif word == 'horrea': newword = 'horreum'
##    elif word == 'incensum': newword = 'incensus'
##    elif word == 'infernum': newword = 'infernus'
##    elif word == 'negotio': newword = 'negotium'
##    elif word == 'nives': newword = 'nix'
##    elif word == 'nubilum': newword = 'nubes'
##    elif word == 'officia': newword = 'officium'
##    elif word == 'pepon': newword = 'pepo'
##    elif word == 'plaustra': newword = 'plaustrum'
##    else: newword = word
##    pageno, latinexist, nounexist, multiplenouns, noun_env = nouninfo(newword)  # Map tuples to variables
##    latin_words[word]['PageNo'] = pageno
##    latin_words[word]['LatinExist?'] = latinexist
##    latin_words[word]['NounExist?'] = nounexist
##    latin_words[word]['MultipleNouns?'] = multiplenouns
##    if noun_env != '':                                                          # If there is a noun environment
##        gender = Root(word,definition,noun_env).gen()
##        dectrans = {'first declension':'1','second declension':'2','third declension':'3','fourth declension':'4','fifth declension':'5',
##                    'first':'1','second':'2','third':'3','fourth':'4','fifth':'5','No info':'No info'}
##        declension = dectrans[Root(word,definition,noun_env).dec()]
##        nominative, genitive, accusative = Root(word,definition,noun_env).cases()
##    else:                                                                       # Otherwise, no information
##        gender = 'No info'
##        declension = 'No info'
##        nominative = ['No info','No info']
##        genitive = ['No info','No info']
##        accusative = ['No info','No info']
##    latin_words[word]['Gender'] = gender
##    latin_words[word]['Declension'] = declension
##    latin_words[word]['Nominative'] = nominative
##    latin_words[word]['Genitive'] = genitive
##    latin_words[word]['Accusative'] = accusative
##    print latin_words[word]
##
### Write data to file
##writedata = open('/Users/Tyler/Desktop/paradigms.txt', 'w')
##writedata.write("""Latin\tLatGender\tLatDec\tnomsg\tnompl\tgensg\tgenpl\taccsg\taccpl\tRomGender\tRomSg\tRomPl\tOldRom\tOldestRom\tOrigLang\tUnsureCog?\tChangedMean\tPSlWord\tPSlavGender\tPSlNote\tNewWord?\tPageNo\tLatinExist?\tNounExist?\tMultipleNouns?\n""")
##for word in sorted(latin_words.keys()):
##    writedata.write(word.lower()+'\t')
##    h = HTMLParser.HTMLParser()
##    writedata.write(latin_words[word]['Gender']+'\t')
##    writedata.write(latin_words[word]['Declension']+'\t')   
##    for form in latin_words[word]['Nominative']:                        # Decode HTML into Unicode then to normal text
##        writedata.write(h.unescape(form).encode('utf8')+'\t')
##    for form in latin_words[word]['Genitive']:                        # Decode HTML into Unicode then to normal text
##        writedata.write(h.unescape(form).encode('utf8')+'\t')
##    for form in latin_words[word]['Accusative']:                        # Decode HTML into Unicode then to normal text
##        writedata.write(h.unescape(form).encode('utf8')+'\t')
##    writedata.write(latin_words[word]['EnglishDef']+'\n')    
##    writedata.write(latin_words[word]['RomanianGender']+'\t')
##    writedata.write(latin_words[word]['RomanianSg']+'\t')
##    writedata.write(latin_words[word]['RomanianPl']+'\t')
##    writedata.write(latin_words[word]['OlderRom']+'\t')
##    writedata.write(latin_words[word]['OldestRom']+'\t')
##    writedata.write(latin_words[word]['OrigLang']+'\t')
##    writedata.write(latin_words[word]['UnsureCognate']+'\t')
##    writedata.write(latin_words[word]['ChangedMeaning']+'\t')
##    writedata.write(latin_words[word]['SlavicWord']+'\t')
##    writedata.write(latin_words[word]['SlavicGender']+'\t')
##    writedata.write(latin_words[word]['SlavicNote']+'\t')
##    writedata.write(latin_words[word]['NewWord']+'\t')
##    writedata.write(latin_words[word]['PageNo']+'\t')
##    writedata.write(latin_words[word]['LatinExist?']+'\t')
##    writedata.write(latin_words[word]['NounExist?']+'\t')
##    writedata.write(latin_words[word]['MultipleNouns?'])
##    writedata.write('\n')


# Gather the frequencies separately as they take time
writefreq = open('/Users/Tyler/Desktop/frequencies.txt','a')
##writefreq.write('Latin\tMaxFreq\tMinFreq\tMinFreq10k\n')

freqexists = 0                                                                      # Check if frequency exists to see how many words we have the freq of
total = 0
    
for i in range(541,len(sorted(latin_words.keys()))):                                # Do in batches
    word = sorted(latin_words.keys())[i]                                            
##    total += 1
    definition = latin_words[word]['EnglishDef'].replace(';',',').split(', ')       
    writefreq.write(word.lower()+'\t')                                              # Write the word
    print i, word, Root(word,definition,nouninfo(word)).freq()              
    if word[-1] in ['0','1','2','3','4']:
        wordnonum = word[:-1]
    else: wordnonum = word
    maxfreq, minfreq, minfreq10k = Root(wordnonum,definition,nouninfo(wordnonum)).freq()
    latin_words[word]['MaxFreq'] = maxfreq      # Write the frequency
    latin_words[word]['MaxFreq'] = minfreq      # Write the frequency
    latin_words[word]['MaxFreq'] = minfreq10k      # Write the frequency
##    if latin_words[word]['Freq10k'] != '?':                                     
##        freqexists += 1
    writefreq.write(maxfreq+'\t'+minfreq+'\t'+minfreq10k+'\n') 

##print freqexists
##print total

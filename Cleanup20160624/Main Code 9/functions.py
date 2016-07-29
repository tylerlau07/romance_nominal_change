# -*- coding: utf-8 -*-
# Author: Tyler Lau

from math import ceil
from math import log

#############
# Functions #
#############

def binaryDict(category):
    '''Create dictionary of each item to binary'''
    # Pad with 0's up to size (log base 2 of number of items)
    fill_size = int(ceil(log(len(category), 2)))
    bin_list = [tuple(map(int, bin(num)[2:].zfill(fill_size))) for num in range(len(category))]
    return dict(zip(category, bin_list))

def invert(d):
    '''
    Invert a dictionary
    '''
    return dict((value, key) for key, value in d.iteritems())

def getTime(seconds):
    '''Convert seconds into hours, minutes, and days'''
    hrs = seconds/3600
    mins_remaining = seconds % 3600
    mins = mins_remaining/60
    secs = mins_remaining % 60
    return '%d hours, %d minutes, %d seconds' % (hrs, mins, secs)

#################################
# Constants for Phonemicization #
#################################

# Also replace diphthongs with single letter
spec_seq = {'ph':'p', 'th':'t', 'ch':'k', 'qu':'kw',
            'y':'i', 'c':'k', 'x':'ks', 'h':'-', 'v':'w',
            'gn':'Nn', 'ng':'Ng', 'nk':'Nk', u'iū':u'jū'}

vowels = {'a':'a', 'e':'e', 'i':'i', 'o':'o', 'u':'u', 'E':'E', 'O':'O'} 

# ia, iu, ua is a diphthong only for endings...
# diphthongs = {'ui':'1', 'ei':'2', 'eu':'3', 'oe':'4', 'ou':'5', 
                # 'ae':'6', 'au':'7', 'ia':'8', 'iu':'9', 'ua':'0'}
diphthongs = {'ai':'1', 'ei':'2', 'ii':'3', 'oi':'4', 'ui':'5', 
            'ea':'6', 'oa':'7', 'ua':'8', 'eu':'9', 'eo':'0'}

revert_to_diph = invert(diphthongs)

lv = {u'ā':'aa', u'ē':'ee', u'ī':'ii', u'ō':'oo', u'ū':'uu', u'ȳ':'ii'}

revert_to_lv = invert(lv)

consonant_clusters = ['pr','br','tr','dr','kr','gr','fr',
                      'pl','bl','kl','gl','fl',
                      'ps','kw']

triple_clusters = ['spr', 'str', 'skr']

# Combine vowels, diphthongs, and long vowels
all_v = {}
all_v.update(vowels)
all_v.update(revert_to_diph)
all_v.update(lv)

# Combine sequences to be replaced
to_replace = {}
to_replace.update(spec_seq)
to_replace.update(diphthongs)

# To revert
to_revert = {}
to_revert.update(revert_to_diph)
to_revert.update(revert_to_lv)

#################################
# Functions for Phonemicization #
#################################

def checkEqual(iterator):
    '''Checks if all elements in a list are equal'''
    try:
        iterator = iter(iterator)
        first = next(iterator)
        return all(first == rest for rest in iterator)
    except StopIteration:
        return True

def replace(word):
    '''
    Replace phonemic sounds with phonetic
    '''
    # First replace phonemic consonants with phonetic and diphthongs with symbols
    for seq in to_replace.keys():
        if seq in word:
            word = word.replace(seq, to_replace[seq])
    return word

def syllabify(word):
    '''
    Treat syllables as CV so that relevant information in ending will line up
    '''
    new_word = ''
    for i in range(0, len(word)):
        letter = word[i]
        # If a vowel, marks the end of a syllable
        if letter in all_v.keys():
            new_word += all_v[letter] + '.'
        else:
            new_word += letter
    return new_word

def codaToOnset(word):
    '''
    Realign codas to onsets
    '''
    word = word.strip('.').split('.')

    # If monosyllabic ignore
    if len(word) == 1:
        return word

    # Leave first one alone
    for i in range(1, len(word)):
        syllable = word[i]
        # If more complicated than CV
        while len(word[i]) > 2:
            # Ex. 'ees', 'stra', 'tra'
            if syllable[0:3] not in triple_clusters and syllable[0:2] not in consonant_clusters:
                # Move onset to coda of previous
                if syllable[0] not in vowels and syllable[1] not in vowels:
                    word[i-1] = word[i-1] + syllable[0]
                    word[i] = syllable[1:]
            # Ex. 'taa'
            if len(syllable) == 3 and syllable[1:] in lv.values(): break
            else: break

    # If last syllable is one or two consonants, realign
    if len(word[-1]) == 1 and word[-1] not in vowels:
        word[-2] = word[-2] + word[-1]
        del(word[-1])
    elif len(word[-1]) == 2 and word[-1][0] not in vowels and word[-1][1] not in vowels:
        word[-2] = word[-2] + word[-1]
        del(word[-1])
    return word

def addDashes(word):
    '''
    Add dashes in appropriate places
    Max of six syllables, max of 7 spots CCCVVCC
    '''
    fixed_word = []

    # If empty string, just set up the dashes
    if word == ['']:
        fixed_word = ['-'*8]*6
        return fixed_word

    for i in range(0, len(word)):
        syllable = word[i]
        syll_len = len(syllable)
        
        # If only one letter in syllable it is a vowel
        if syll_len == 1:
            new_syll = '-'*3 + syllable + '-'*4

        # Could be VV, CV, or VC
        elif syll_len == 2:
            # If VV
            if syllable[0] in vowels and syllable[1] in vowels:
                new_syll = '-'*3 + syllable + '-'*3
            # If CV
            elif syllable[0] not in vowels:
                new_syll = '-' + syllable[0] + '-' + syllable[1] + '-'*4
            # If VC
            else:
                new_syll = '-'*3 + syllable[0] + '-'*2 + syllable[1] + '-'

        # If 3 or more
        else:
            # FIRST DEAL WITH ONSETS    
            # No onset ---V
            if syllable[0] in vowels:
                onset_done = '-'*3 + syllable
            # One onset -C-
            elif syllable[0] not in vowels and syllable[1] in vowels:
                onset_done = '-' + syllable[0] + '-' + syllable[1:]
            # Two onsets -CC
            elif syllable[0] not in vowels and syllable[1] not in vowels:
                onset_done = '-' + syllable
            # Three onsets CCC
            else:
                onset_done = syllable 

            # NOW DEAL WITH NUCLEUS
            # Minimum is CCCV
            if len(onset_done) == 4:
                new_syll = onset_done + '-'*4
            else:
                # If CCCVV
                if onset_done[4] in vowels:
                    nuc_done = onset_done
                # If CCCVC
                else:
                    nuc_done = onset_done[:4] + '-' + onset_done[4:]

                # NOW DEAL WITH CODA(S)
                # No coda
                if len(nuc_done) == 5:
                    new_syll = nuc_done + '-'*3
                # One coda
                elif len(nuc_done) == 6:
                    new_syll = nuc_done[:-1] + '-' + nuc_done[-1] + '-'
                # Two codas
                elif len(nuc_done) == 7:
                    new_syll = nuc_done[:-2] + '-' + nuc_done[-2:]
                # Three codas
                else:
                    new_syll = nuc_done

        # SANITY CHECK
        if len(new_syll) != 8:
            print "You screwed up the size of the syllable"
            print word, len(new_syll), new_syll
            raise SystemExit
        else:
            fixed_word.append(new_syll)

    return fixed_word

def reworkSuffix(suffix, language, secondsoundchange):
    '''
    Recreates the suffix to be the desired phonological form depending on language
    Form should have VVC CVVC skeleton (max: iu, a ui)
    If trying second sound change, set to True
    '''

    # Short vowel changes
    sv_changes = {'m':'', 'i':'e', 'ae':'e', 'uu':u'ū'}
    # Non-Romanian changes
    nonrom_sv = {'u':'o'}
    # All lv_changes
    lv_changes = {u'ā':'a', u'ī':'i', u'ē':'e', u'ō':'o', u'ū':'u'}

    # Italian consonantal changes
    ita_changes = {'s':'i'}
    rom_changes = {'s':'i', 'b':'', 'o':'u'}
    postrom_changes = {'uru':'oru'}

    # Changes for Italian and Romanian following generation of change
    # Test against hypothesis of oi > i, ui > i?
    ita_mono = {'ai':'e', 'ei':'i', 'ii':'i', 'oi':'o', 'ui':'u'}
    # If penultimate long, stress, otherwise, antepenultimate
    # Reverse uru to oru because of penultimate stress
    rom_mono = {'ai':'e', 'ei':'i', 'ii':'i'}

    replaced = suffix

    # Apply the common sound changes
    # First SV changes that apply everywhere
    for phon in sv_changes.keys():
        if phon in replaced:
            replaced = replaced.replace(phon, sv_changes[phon])
    # Then nonrom SV change
    if language != 'Romanian':
        for phon in nonrom_sv.keys():
            if phon in replaced:
                replaced = replaced.replace(phon, nonrom_sv[phon])
    # Then long vowel changes
    for phon in lv_changes.keys():
        if phon in replaced:
            replaced = replaced.replace(phon, lv_changes[phon])

    # Now language-specific
    if language == 'Italian':
        for phon in ita_changes.keys():
            if phon in replaced:
                replaced = replaced.replace(phon, ita_changes[phon])
        if secondsoundchange == True:
            for phon in ita_mono.keys():
                if phon in replaced:
                    replaced = replaced.replace(phon, ita_mono[phon])
    elif language == 'Romanian':
        for phon in rom_changes.keys():
            if phon in replaced:
                replaced = replaced.replace(phon, rom_changes[phon])
        for phon in postrom_changes.keys():
            if phon in replaced:
                replaced = replaced.replace(phon, postrom_changes[phon])
        # Now break e to ea if final
        if replaced == 'e': replaced += 'a'
        if secondsoundchange == True:
            for phon in rom_mono.keys():
                if phon in replaced:
                    replaced = replaced.replace(phon, rom_mono[phon])

    if replaced in ['aui', 'eui', 'uui']:
        mod_sylls = [replaced[0], replaced[1:]]
    else: mod_sylls = codaToOnset(syllabify(replace(replaced)))

    # Now add dashes and align
    aligned_suf = []

    # Max VVC CVVC
    for i in range(len(mod_sylls)):
        syllable = mod_sylls[i]
        # Null ending
        if syllable == '':
            aligned_suf.append('-'*3)
        # First syllable, maximally VVC
        elif i == 0:
            # V or C
            if len(syllable) == 1:
                # V
                if syllable in vowels:
                    aligned_suf.append(syllable + '-'*2)
                # C
                else:
                    aligned_suf.append('-'*2 + syllable)
            # VV or VC
            elif len(syllable) == 2:
                # VV
                if syllable[-1] in vowels:
                    aligned_suf.append(syllable + '-')
                # VC
                else:
                    aligned_suf.append(syllable[0] + '-' + syllable[-1])
            # VVC
            else: aligned_suf.append(syllable)
        # Second syllable, maximally CVVC
        elif i == 1:
            # V or C
            if len(syllable) == 1:
                # V
                if syllable in vowels:
                    aligned_suf.append('-' + syllable + '-'*2)
                # C
                else:
                    aligned_suf.append('-'*3 + syllable)
            # VV, VC, or CV
            elif len(syllable) == 2:
                # VC
                if syllable[-1] not in vowels:
                    aligned_suf.append('-' + syllable[0] + '-' + syllable[-1])
                # CV
                elif syllable[0] not in vowels:
                    aligned_suf.append(syllable + '-'*2)
                # VV
                else: aligned_suf.append('-' + syllable + '-')
            # 3 syllables
            else:
                # CVV
                if syllable[-1] in vowels:
                    aligned_suf.append(syllable + '-')
                # CVC
                else: aligned_suf.append(syllable[:-1] + '-' + syllable[-1])
    if len(aligned_suf) == 1:
        aligned_suf.append('-'*4)

    # Sanity check
    if len(''.join(aligned_suf)) != 7:
        print "You screwed up the size of the suffix"
        print suffix, len(aligned_suf), aligned_suf
        raise SystemExit
    else:
        return map(str, aligned_suf)
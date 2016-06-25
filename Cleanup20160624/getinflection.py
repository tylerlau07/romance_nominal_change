# -*- coding: utf-8 -*-

# Author: Tyler Lau
# This program will fetch the inflected forms of each word

import urllib
import re
import csv

from bs4 import BeautifulSoup
import codecs

#############
# Functions #
#############

def lookUp(word):
	soup = urllib.urlopen("https://en.wiktionary.org/wiki/%s" % word)
	htmlSource = soup.read()                            
	soup.close() 

	parsed_html = BeautifulSoup(htmlSource)
	print parsed_html

########
# Main #
########

lookUp("res")

# reader = codecs.open('declinedforms.txt', encoding='utf-8', mode='rU')
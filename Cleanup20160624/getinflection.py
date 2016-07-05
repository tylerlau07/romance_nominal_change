# -*- coding: utf-8 -*-

# Author: Tyler Lau
# This program will fetch the inflected forms of each word
import urllib
import unicodecsv as csv

from BeautifulSoup import BeautifulSoup
import codecs

#############
# Functions #
#############

def InflTable(word):
	'''
	Takes in a word and returns the inflection table,
	whether it is defective (lacking a number),
	or if there is variation in the individual inflections
	'''
	soup = urllib.urlopen('https://en.wiktionary.org/wiki/%s' % word)
	htmlSource = soup.read()                            
	soup.close() 

	parsed_html = BeautifulSoup(htmlSource)

	# If there is only one inflection table
	if len(parsed_html.findAll('table', attrs={'class':'prettytable inflection-table'})) == 1:

		infl_table = parsed_html.find('table', attrs={'class':'prettytable inflection-table'})

		# Check if defective or variable
		defective = False
		variation = False

		numbers = infl_table.findAll('th', attrs={'style':'background:#549EA0; font-style:italic;'})

		# If defective, return which number exists
		if len(numbers) != 3:
			defective = numbers[1].text

		# Check if variation in forms
		if len(infl_table.findAll('span')) != 12:
			variation = True

		return infl_table, defective, variation

	# If multiple inflection tables (because of multiple definitions), easier to just check which is correct
	else: return None

def getInfl((infl_table, defective, variation)):
	'''
	Takes in an inflection table and returns the inflection
	If defective, will return only singular or plural
	If there is variation, inflections will be divided by /
	'''
	to_return = []

	if defective == False:
		# Only one form for each inflection
		if variation == False:
			to_return += [inflection.text for inflection in infl_table.findAll('td')]

		# Multiple forms for each inflection
		else:
			for inflection in infl_table.findAll('td'):
				# Join multiple inflections with /
				infl_form = '/'.join([inflection.text for inflection in inflection.findAll('span')])
				to_return.append(infl_form)
	
	# One of the numbers is lacking
	else:
		for inflection in infl_table.findAll('td'):
			# Join multiple inflections with /
			infl_form = '/'.join([inflection.text for inflection in inflection.findAll('span')])

			if defective == 'Singular':
				to_return += [infl_form, '-']

			elif defective == 'Plural':
				to_return += ['-', infl_form]

			else:
				print "Check what numbers are represented because it is neither Singular nor Plural"
				return ["CHECK"]

	# Sanity check
	if len(to_return) == 12:
		return to_return	
	else:
		print "The number of inflections is not 12"
		return ["CHECK"]

	return to_return

########
# Main #
########

# print getInfl(InflTable("domus"))

reader = codecs.open('latin_nouns.txt', encoding='utf-8', mode='rU')

with open('noun_paradigms2.txt', mode = 'wb') as f:
	out = csv.writer(f, delimiter = '\t')
	out.writerow(["Latin", "English", "Declension", "Gender", "Total", "Prose", "Poetry",
		"NomSg", "NomPl", "GenSg", "GenPl", "DatSg", "DatPl", "AccSg", "AccPl", "AblSg", "AblPl", "VocSg", "VocPl"])

	for row in reader.readlines()[1:]:
		row = row.strip("\r\n").split("\t")

		# Create object to be added to
		to_write = row
		word = row[0]

		# If there are multiple inflection tables (different definitions/parts of speech), just check and fix manually
		if InflTable(word) == None:
			to_write += ["CHECK"]

		else:
			to_write += getInfl(InflTable(word))

		print word, to_write
		out.writerow(to_write)
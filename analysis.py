#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import cochrane
import dblp
import pubmed
import ast
import os
import re
from matplotlib import pyplot as plt
import operator
import unicodedata
import string
import pylab
import numpy as np


def print_data(data, outfile):

	if data['Database'] == 'DBLP':
		dblp.print_data_DBLP(data, outfile)

	elif data['Database'] == 'Cochrane Library':
		cochrane.print_data_Cochrane(data, outfile)

	elif data['Database'] == 'PubMed':
		pubmed.print_data_Pubmed(data, outfile)



def extract_data(dbs, outfileName):

	infiles = []
	outfile = codecs.open(outfileName + '.csv', 'w', encoding='utf-8')

	for db in dbs:
		infile = codecs.open('temp_' + db + '.csv', 'r', encoding='utf-8')
		infiles.append(infile)

	for i in range(len(dbs)):

		for line1 in infiles[i]:
			item1 = ast.literal_eval(line1.strip())
			print_data(item1, outfile)

	for infile in infiles:
		infile.close()

	for db in dbs:
		os.remove('temp_' + db + '.csv')

	outfile.close()




def deduplicate(dbs, outfileName):
	
	infiles = []
	outfile = codecs.open(outfileName + '.csv', 'w', encoding='utf-8')

	for db in dbs:
		infile = codecs.open('temp_' + db + '.csv', 'r', encoding='utf-8')
		infiles.append(infile)

	for i in range(len(dbs)):
		infiles[i].seek(0)

		for line1 in infiles[i]:
			item1 = ast.literal_eval(line1.strip())
			duplicated = False

			for j in range(i + 1, len(dbs)):
				infiles[j].seek(0)

				for line2 in infiles[j]:
					item2 = ast.literal_eval(line2.strip())

					if len(item1['Title']) > 0 and item1['Title'] == item2['Title'] and item1['Year'] == item2['Year']:
						authors1 = item1['Authors']
						authors2 = item2['Authors']

						if len(authors1) == len(authors2) and cmp(authors1, authors2) == 0:
							duplicated = True
							break

				if duplicated:
					break

			print_data(item1, outfile)

	for infile in infiles:
		infile.close()

	for db in dbs:
		os.remove('temp_' + db + '.csv')

	outfile.close()

def filter_accents(s):
	return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def filter_punct(ent):
	''' Remove sinais de pontuaçao STRING --> STRING '''
	punct = re.compile('[%s]' % string.punctuation)  #Tags precisam ser mantidas, bem como @ 
	ent = punct.sub('', ent)
	
	return ent

def filter_stopwords(ent):
	arq = open('stop-words-english5.txt', 'r')
	stopwords = []

	words = re.findall('[a-z][a-z]*', ent)
	
	for line in arq:
		word = line.strip()
		word = word.decode('utf8')
		if word in [w.lower() for w in words]:
			words = filter(lambda x: x.lower() != word and len(x) > 1, words)

	return words


def filter_title(title):

	title = filter_accents(title.lower())
	title = filter_punct(title)
	words = filter_stopwords(title)

	return words


def plot_words(words, outfileName):

	count = 0
	y, labels = [], []

	for key in sorted(words.items(), key=operator.itemgetter(1), reverse=True):
		y.insert(0, words[key[0]])
		labels.insert(0, key[0])
		count += 1
		if count == 20:
			break

	fig, ax = plt.subplots(figsize=(13,8))
	y_pos = np.arange(len(y))
	plt.barh(y_pos, y)
	plt.subplots_adjust()
	plt.title('Most frequent terms')
	plt.xlabel('# entries containing term')
	plt.ylabel('term')
	pylab.yticks(y_pos, labels)
	plt.savefig('frequentTerms_' + outfileName + '.png')
	

def plot_years(years, outfileName):

	x, y, labels = [[] for x in range(3)]
	count = 0

	for key in sorted(years.keys()):
		x.append(count)
		y.append(years[key])
		labels.append(key)
		count += 1

	fig = plt.figure()
	ax = plt.bar(labels, y, align='center', width=0.3)
	plt.title('Number of publications for each year')
	plt.xlabel('year')
	plt.ylabel('# entries')
	#pylab.xticks(x, labels)
	plt.savefig('yearDistribution_' + outfileName + '.png')
	

def plot_types(types, outfileName):

	y, labels = [], []
	count = 0

	for key in sorted(types.items(), key=operator.itemgetter(1), reverse=True):
		y.insert(0, types[key[0]])
		labels.insert(0, key[0].replace(' ', '\n')) 
		count += 1
		if count == 5:
			break

	fig, ax = plt.subplots(figsize=(11,8))
	y_pos = np.arange(len(y))
	plt.bar(y_pos, y, align='center', width=0.3)
	plt.subplots_adjust()
	plt.title('Most frequent types of results')
	plt.ylabel('# entries of the type')
	plt.xlabel('type')
	pylab.xticks(y_pos, labels)
	plt.savefig('frequentTypes_' + outfileName + '.png')


def get_analysis(outfileName):

	infile = codecs.open(outfileName + '.csv', 'r', encoding='utf-8')
	words, years, types = [dict() for x in range(3)]

	for line in infile:
		item = dict()
		fields = line.strip().split('\t')

		for field in fields:
			keyvalue = field.split(':', 1)
			item[keyvalue[0]] = keyvalue[1][1:]

		text = item['Title']

		if len(text) == 0:
			continue

		title_words = filter_title(text)

		for w in title_words:

			if not words.has_key(w):
				words[w] = 0
			words[w] += 1

		year = int(item['Year'][:4])
		if not years.has_key(year):
			years[year] = 0
		years[year] += 1

		if item.has_key('Type'):
			if not types.has_key(item['Type']):
				types[item['Type']] = 0
			types[item['Type']] += 1


	plot_words(words, outfileName)
	plot_years(years, outfileName)
	plot_types(types, outfileName)
			
	infile.close()



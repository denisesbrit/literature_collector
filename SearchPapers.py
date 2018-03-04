#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import cochrane
import dblp
import pubmed
import analysis
import codecs
import re


def parse_query(query):

	query = query.strip()

	DBLP_query = query.replace(' OR ', '|').replace(' AND ', '+').replace('NOT ', '-').replace('+', ' ')
	Pubmed_query = query.replace(' OR ', ') OR ').replace(' AND ', ') AND '). replace(' NOT ', ') NOT ')

	#whitespace = and, not in the begining has unknown behavior, not allowed to have exact matching, not allowed to alter the priority
	#pubmed will search mesh terms, cochrane will not. abbreviations should not be used. 
	#search will be done with prefix 

	matches = re.findall('\)', Pubmed_query)
	num_operators = len(matches)

	for i in range(num_operators):
		Pubmed_query = '(' + Pubmed_query

	Cochrane_query = Pubmed_query.replace(')', '*)')
	Cochrane_query += '*'

	return DBLP_query, Cochrane_query, Pubmed_query



def read_query_databases(infileName):

	try:
		infile = codecs.open(infileName, 'r', encoding='utf-8')
	except:
		print 'Error: file could not be opened.'
		sys.exit(0)

	try:
		lines = infile.readlines()
		query = lines[0]
		databases = []
	
		for line in lines[1:]:
			databases.append(line.strip().lower())

	except:
		print 'Error: file is not in the proper format.'
		sys.exit(0)	

	infile.close()

	return query, databases

	


def query_data(query, databases, outfileName, deduplicate=False):

	DBLP_query, Cochrane_query, Pubmed_query = parse_query(query)
	dbs = []

	if 'dblp' in databases:
		DBLP_data = dblp.get_data_DBLP(DBLP_query)
		dbs.append('dblp')
	if 'cochrane library' in databases:
		Cochrane_data = cochrane.get_data_Cochrane(Cochrane_query)
		dbs.append('cochrane')
	if 'pubmed' in databases:
		Pubmed_data = pubmed.get_data_Pubmed(Pubmed_query)
		dbs.append('pubmed')
	
	if deduplicate:
		analysis.deduplicate(dbs, outfileName)
	else:
		analysis.extract_data(dbs, outfileName)

	analysis.get_analysis(outfileName)



if __name__ == '__main__':

	query, databases = read_query_databases(sys.argv[1])

	if len(sys.argv) == 4:
		deduplicate = True
	else:
		deduplicate = False

	query_data(query, databases, sys.argv[2], deduplicate)



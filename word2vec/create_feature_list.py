from calculate_soft_tf import calculate_query_doc_softfrequency
from gensim.models import Word2Vec
import re

def mean(numbers):
    return float(sum(numbers))/len(numbers)

word2vec_model = Word2Vec.load("word2vec_model.bin")

document_map = {}
query_map = {}
with open("qrels.txt") as file:
		line = file.readline()
		while line:
			query = line.split()[0]
			doc_id = line.split()[2]
			if doc_id in document_map:
				document_map[doc_id].append(query)
			else:
				document_map[doc_id] = []
				document_map[doc_id].append(query)
			line = file.readline()

with open("queries.txt") as query_file:
		line = query_file.readline()
		while line:
			query_list = line.split(' ', 1)
			query_map[query_list[0]] = query_list[1]
			line = query_file.readline()
		# print(query_map)

with open("lines-trec45.txt") as trec_file:
	with open("feature.txt", 'w') as output_file:
		line = trec_file.readline()
		while line:
			doc = re.split(r'\t+', line)
			document = doc[1]
			if len(doc) == 3:
				document += doc[2]
			doc_id = doc[0]
			if doc_id in document_map:
				query_list = document_map[doc_id]
				for query_id in query_list:
					similarity5, similarity6, similarity7, similarity_exact = calculate_query_doc_softfrequency(query_map[query_id], document, word2vec_model)
					# print(similarity5)
					query_list_frequencies_5 = list(similarity5.values())
					query_list_frequencies_6 = list(similarity6.values())
					query_list_frequencies_7 = list(similarity7.values())
					query_list_frequencies_exact = list(similarity_exact.values())
					# print(query_list_frequencies_5)
					# print(query_list_frequencies_6)
					# print(query_list_frequencies_7)
					# print(query_list_frequencies_exact)

					output_file.write(query_id + " " + doc_id + " " \
						+ str(min(query_list_frequencies_5)) + " " + str(max(query_list_frequencies_5)) + " " + str(mean(query_list_frequencies_5)) + " " \
						+ str(min(query_list_frequencies_6)) + " " + str(max(query_list_frequencies_6)) + " " + str(mean(query_list_frequencies_6)) + " " \
						+ str(min(query_list_frequencies_7)) + " " + str(max(query_list_frequencies_7)) + " " + str(mean(query_list_frequencies_7)) + " " \
						+ str(min(query_list_frequencies_exact)) + " " + str(max(query_list_frequencies_exact)) + " " + str(mean(query_list_frequencies_exact)) + "\n")
						
			line = trec_file.readline()

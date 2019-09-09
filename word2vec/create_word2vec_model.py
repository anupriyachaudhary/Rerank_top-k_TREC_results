from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from gensim.models import Word2Vec
import re
import sys

def construct_input_array(sentence):
	stop_words = set(stopwords.words('english'))
	 # tokenize
	word_tokens = word_tokenize(sentence)
	 # remove stop words
	 # remove punctuation
	 # convert to lower case
	 # stemming
	porter = PorterStemmer()
	filtered_sentence = [porter.stem(w.lower()) for w in word_tokens if not w in stop_words and w.isalpha()]
	# add to sentences array
	return filtered_sentence


if __name__ == "__main__":

	if len(sys.argv) < 3:
		print("Please provide the document and query file name")

	sentences = []

	# add documents to input
	with open(sys.argv[1]) as trec_file:
		line = trec_file.readline()
		while line:
			doc = re.split(r'\t+', line)
			if len(doc) == 2:
				document_content = construct_input_array(doc[1])
				sentences.append(document_content)
			elif len(doc) == 3:
				document_content = construct_input_array(doc[1]) + construct_input_array(doc[2])
				sentences.append(document_content)
			# sentences.append(construct_input_array(doc[1]))
			# if len(doc) == 3:
				# sentences.append(construct_input_array(doc[2]))
			line = trec_file.readline()

	# add queries to input
	with open(sys.argv[2]) as query_file:
		line = query_file.readline()
		while line:
			sentences.append(construct_input_array(line.split(' ', 1)[1]))
			line = query_file.readline()

	print(len(sentences))

	# create word2vec model and store it
	word2vec_model=Word2Vec(sentences, size=100, min_count=5)
	word2vec_model.save("word2vec_model.bin")
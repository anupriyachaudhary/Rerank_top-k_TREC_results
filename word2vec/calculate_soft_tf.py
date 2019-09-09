from gensim.models import Word2Vec
from scipy import spatial
import numpy as np
from create_word2vec_model import construct_input_array
import math

def mean(numbers):
    return float(sum(numbers))/len(numbers)

word2vec_model = Word2Vec.load("word2vec_model.bin")


# load the word2vec model
# word2vec_model = Word2Vec.load("word2vec_model.bin")

def calculate_query_doc_softfrequency(query, document, model):
    
    index2word_set = set(model.wv.index2word)
    
    query_list = construct_input_array(query)
    document_list = construct_input_array(document)
    
    query_list_frequencies_5 = {}
    query_list_frequencies_6 = {}
    query_list_frequencies_7 = {}
    query_list_frequencies_exact = {}

    for qt in query_list:
        query_list_frequencies_5[qt] = 0
        query_list_frequencies_6[qt] = 0
        query_list_frequencies_7[qt] = 0
        query_list_frequencies_exact[qt] = document_list.count(qt)

    for word in document_list:
        for queryTerm in query_list:
            try:
                similarity_score = model.wv.similarity(queryTerm, word)
            
                

                if similarity_score >= 0.7:
                    query_list_frequencies_7[queryTerm] += similarity_score
                if similarity_score >= 0.6:
                    query_list_frequencies_6[queryTerm] += similarity_score
                if similarity_score >= 0.5:
                    query_list_frequencies_5[queryTerm] += similarity_score
            except:
                continue
    # print("sleeping")
    # print(query_list_frequencies_5)
                
    return query_list_frequencies_5, query_list_frequencies_6, query_list_frequencies_7, query_list_frequencies_exact

if __name__ == "__main__":
    query = "mexican political war"
    document = "mexican political threat mr manuel camacho sols the mexican government s peace envoy in the southern state of chiapas has indicated he might run for national office if the government did not approve democratic reforms under discussion for the country and failed to comply with the recent peace accord for the rebels in chiapas he thereby resisted rising pressure from his colleagues in the governing party to rule himself out of the presidential race the party s 65 year hold on power could be jeopardised if mr camacho a former mayor of mexico city and an ex foreign minister were to realise his veiled threat to run as an opposition candidate in the presidential election in august if there are no advances in democracy and if instead of accord there is polarisation and if anyone wants to trample on my political rights as a citizen then after i have fulfilled my mission in chiapas i will take the necessary political decision to bring democracy and unity to mexico mr camacho told reporters"
   # print(calculate_query_doc_similarity( "party", "", word2vec_model))
    similarity5, similarity6, similarity7, similarity_exact = calculate_query_doc_softfrequency( query, document, word2vec_model)
    query_list_frequencies_7 = list(similarity7.values())
    print(query_list_frequencies_7)
    print(mean(query_list_frequencies_7))
    # print(calculate_query_doc_softfrequency( query, document, word2vec_model))

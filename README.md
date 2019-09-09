REQUIREMENTS:
This project needs access to lines-trec45.txt, qrels.trec6-8.nocr, title-queries.301-450 which needs to be supplied by the user. 
Download and extract the latest Lucene distribution. Copy three JARs: the LuceneCore JAR, the queryparser JAR, and the common analysis JAR and place all the files in the ‘lib’ folder.
Download standalone program RankLib.jar and put it in the bin folder in working directory

FILES & FOLDERS:
(1) 1doclen_ext.py: extracts length of each doc in the query relevance file from index. Output for this script is input for 3feature_ext.py
(2) 2doclen_ext_bm25.py: extracts length of each doc in the ranked list (for a test query, query.txt) to be re-ranked by LTR model. Output for this script is input for 3feature_ext.py
(3) 3feature_ext.py: produces training data by extracting feature values for each query-doc pair in relevance judgement file from index
(4) 4rerank.py: reranks the ranked documents (ranked by BM25 similarity) for test query
(5) 5feature_ext_proximity.py: produce 5 training files corresponding to each proximity measure + 18 common features for each query-doc pair in relevance judgement file from index
(6) 6parser.py: code to covert lines-trec45.txt to xml file (the format accepted by lucene)
(7) src: code built on top of Lucene to index a collection, run a set of queries and inspect Lucene indexes
(8) build.xml: build file to build the project.
(9) test-data: contains 4 files
     -title-queries.301-450: TREC search topics.
     -qrels.trec6-8.nocr: correct(and incorrect) answers for each topic (Gold standard).
     -2 test files for re-ranking part of the project. query.txt contains one query and qrels.nocr contains relevance judgement for given query.
(10) trec_eval: executable file which compares a ranked list of output with Gold standard to give a set of quality measures (like MAP, ndcg etc.).


-------------------------------------------------------------------------------
PART I: STEPS TO OBTAIN TRAINING DATA FROM INDEX AND EVALUATE PERFORMANCE OF LTR ALGORITHMS:
-------------------------------------------------------------------------------

Test Instructions:
(1) Run ant to compile:
	$ ant

(2) Run the following scripts to covert lines-trec45.txt to xml file (the format accepted by lucene)
	$ python 6parser.py /path/to/lines-trec45.txt

(3) To create an index of the given TREC data run the following command:
	$ java -cp "bin:lib/*" IndexTREC -docs /path/to/cd45/documents

(4) Run the following command to get training data for given query relevance file
	$ python 1doclen_ext.py path/to/qrels.trec6-8.nocr | python 3feature_ext.py path/to/title-queries.301-450 path/to/training-data_file

(5) To train the training data using different LTR algorithms, run following command which conducts a 3-fold cross validation. 
	$ java -jar bin/RankLib.jar -train train.txt -ranker 4 -kcv 3 -kcvmd models/ -kcvmn ca -metric2t NDCG@10 -metric2T NDCG@10 -silent
		(-kcv Number of folds for k-fold cross validation using training data
		-kcvmd Directory for models trained via cross-validation
		-kcvmn Name for model learned in each fold)
	After training, the NDCG@10 on test data will be outputted on command line screen and the trained model will be stored in the specified folder.

----------------------------------------
PART II: RERANK TOP-k RETRIEVED RESULTS:
----------------------------------------

Requirements: Indexed data and trained model for chosen LTR Algorithm (from steps above)

Test Instructions:
(1) Run the following command to get ranked results based on BM25 similarity for a given query (query.txt file in test-data folder or replace the query in the file with user supplied query)
	$ java -cp "bin:lib/*" BatchSearch -index index/ -queries test-data/query.txt -simfn bm25 > bm25.out

(2) Run the following command to get feature values for query-doc pairs in the file (bm25.out) that contains ranked documents according to BM25.
	$ python 2doclen_ext_bm25.py bm25.out k | python 3feature_ext.py test-data/query.txt rerank-data.txt(/path/to/output)

   Note: Python script 2doclen_ext_bm25.py takes bm25.out file as first argument and k (i.e. number of documents to be re-ranked) as second argument

(3) For each document in the output file from step (2), get the scores obtained by LTR model using following command with RankLib
	$ java -jar bin/RankLib.jar -load /path/to/model -rank path/to/rerank-data.txt -score /path/to/myscorefile.txt

    The output file myscorefile.txt provides the score that the ranker assigns to each of the documents. 

(4) To obtain re-ranked top-k results, simply sort the documents according to calculated score by running following script:
	$ python 4rerank.py /path/to/bm25.out /path/to/newscore.out

(5) To evaluate the re-ranked results compare the NDCG@10 of ranked results by BM25 and re-ranked results using LTR models
	$ ./trec_eval -m ndcg_cut.10 test-data/qrels.nocr bm25.out > bm25.eval

	$ ./trec_eval -m ndcg_cut.10 test-data/qrels.nocr newscore.out > newscore.eval
    Compare scores from bm25.eval file and newscore.eval file

PART II: PROXIMITY SCORES:

(1) Run the following command to get 5 training files (corresponding to each proximity measure) for given query relevance file
	$ python 1doclen_ext.py test-data/qrels.nocr | python 5feature_ext_proximity test-data/query.txt

    The above command gives 5 training files corresponding to different proximity measures. Namely, train_span.txt, train_MinCover.txt, train_MinDist.txt',train_MaxDist.txt',train_AvgDist.txt.

(2) To get NDCG@10 scores for training data with different proximity features, run following command 
	$ java -jar bin/RankLib.jar -train /path/to/train.txt -ranker 4 -kcv 3 -kcvmd models/ -kcvmn ca -metric2t NDCG@10 -metric2T NDCG@10

----------------------------------------
PART III: Deep learning with word2vec
----------------------------------------

Prequisites: 
Python 3
Gensim

create_word2vec_model.py trains the word2vec model on the given corpus and stores it in a binary format. It also does the following text pre-processing:
- Stop words removal
- Punctuation removal
- Lower case conversion
- Stemming using PorterStemmer

python create_word2vec_model.py <trec_data> <query>

create_feature_list.py uses the word2vec model created above to calculate the soft term frequency for a given query document pair. It creates a txt file of the format
<query_id> <document_id> <min_soft_TF> <max_soft_TF> <avg_soft_TF> 

python create_feature_list.py 

Train using the last step in PARTI







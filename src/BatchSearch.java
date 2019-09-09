import java.io.BufferedReader;
import java.io.File;
import java.io.FileWriter;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import org.apache.lucene.search.BooleanClause;
import java.util.Date;
import java.io.StringReader;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.Tokenizer;
import org.apache.lucene.analysis.standard.StandardTokenizer;
import org.apache.lucene.analysis.LowerCaseFilter;
import org.apache.lucene.analysis.en.PorterStemFilter;
import org.apache.lucene.analysis.StopFilter;
import org.apache.lucene.analysis.core.StopAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.classic.QueryParser.Operator;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.index.Term;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.similarities.*;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;
import org.apache.lucene.search.BooleanClause.Occur;

public class BatchSearch {

	private BatchSearch() {}

    public static void main(String[] args) throws Exception {
		String usage =
				"Usage:\tjava BatchSearch [-index dir] [-simfn similarity] [-field f] [-queries file]";
		if (args.length > 0 && ("-h".equals(args[0]) || "-help".equals(args[0]))) {
			System.out.println(usage);
			System.out.println("Supported similarity functions:\nclassic: ClassicSimilary (tfidf)\n");
			System.exit(0);
		}

		String index = "index";
		String field = "contents";
		String queries = null;
		String simstring = "classic";

		for(int i = 0;i < args.length;i++) {
			if ("-index".equals(args[i])) {
				index = args[i+1];
				i++;
			} else if ("-field".equals(args[i])) {
				field = args[i+1];
				i++;
			} else if ("-queries".equals(args[i])) {
				queries = args[i+1];
				i++;
			} else if ("-simfn".equals(args[i])) {
				simstring = args[i+1];
				i++;
			}
		}

		Similarity simfn = null;
		if ("classic".equals(simstring)) {
			simfn = new ClassicSimilarity();
		} else if ("bm25".equals(simstring)) {
			simfn = new BM25Similarity();
		} else if ("dfr".equals(simstring)) {
			simfn = new DFRSimilarity(new BasicModelP(), new AfterEffectL(), new NormalizationH2());
		} else if ("lm".equals(simstring)) {
			simfn = new LMDirichletSimilarity();
		}
		if (simfn == null) {
			System.out.println(usage);
			System.out.println("Supported similarity functions:\nclassic: ClassicSimilary (tfidf)");
			System.out.println("bm25: BM25Similarity (standard parameters)");
			System.out.println("dfr: Divergence from Randomness model (PL2 variant)");
			System.out.println("lm: Language model, Dirichlet smoothing");
			System.exit(0);
		}
		
		IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(index).toPath()));
		IndexSearcher searcher = new IndexSearcher(reader);
		searcher.setSimilarity(simfn);
        Analyzer analyzer = new Analyzer() {
            @Override
            protected TokenStreamComponents createComponents(String fieldName) {
                StringReader reader = new StringReader(fieldName);
                Tokenizer tokenizer = new StandardTokenizer();
                tokenizer.setReader(reader);
                TokenStream tokenStream = new LowerCaseFilter(tokenizer);
                tokenStream = new StopFilter(tokenStream, StopAnalyzer.ENGLISH_STOP_WORDS_SET);
                tokenStream = new PorterStemFilter(tokenStream);
                return new TokenStreamComponents(tokenizer, tokenStream);
            }
        };
		
		BufferedReader in = null;
		if (queries != null) {
			in = new BufferedReader(new InputStreamReader(new FileInputStream(queries), "UTF-8"));
		} else {
			in = new BufferedReader(new InputStreamReader(new FileInputStream("queries"), "UTF-8"));
		}
        
        String[] fields = new String[] { "title", "body" };
        HashMap<String,Float> boosts = new HashMap<String,Float>();
        boosts.put("title", 1.0f);
        boosts.put("body", 1.0f);
        MultiFieldQueryParser parser = new MultiFieldQueryParser(fields, analyzer, boosts);
        
        while (true) {
            Date start = new Date();
			String line = in.readLine();

			if (line == null || line.length() == -1) {
				break;
			}

			line = line.trim();
			if (line.length() == 0) {
				break;
			}
			
			String[] pair = line.split(" ", 2);
			Query query = parser.parse(pair[1]);

			doBatchSearch(in, searcher, pair[0], query, simstring);
            
		}
		reader.close();
	}

	public static void doBatchSearch(BufferedReader in, IndexSearcher searcher, String qid, Query query, String runtag)	 
			throws IOException {

		TopDocs results = searcher.search(query, 1000);
		ScoreDoc[] hits = results.scoreDocs;
		HashMap<String, String> seen = new HashMap<String, String>(1000);
		long numTotalHits = results.totalHits;
		
		int start = 0;
		long end = Math.min(numTotalHits, 1000);

		for (int i = start; i < end; i++) {
			Document doc = searcher.doc(hits[i].doc);
			String docid = doc.get("docid");
			if (seen.containsKey(docid)) {
				continue;
			}
			seen.put(docid, docid);
			System.out.println(qid+" Q0 "+docid+" "+i+" "+hits[i].score+" "+runtag);
		}
	}
}


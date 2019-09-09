import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Date;
import java.io.StringReader;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.Tokenizer;
import org.apache.lucene.analysis.standard.StandardTokenizer;
import org.apache.lucene.analysis.LowerCaseFilter;
import org.apache.lucene.analysis.en.PorterStemFilter;
import org.apache.lucene.analysis.core.StopAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;


public class IndexTREC {

	private IndexTREC() {}
	
	public static void main(String[] args) {

        String indexPath = "index";
		String docsPath = null;
		boolean create = true;
		for(int i = 0;i < args.length; i++) {
			if ("-index".equals(args[i])) {
				indexPath = args[i+1];
				i++;
			} else if ("-docs".equals(args[i])) {
				docsPath = args[i+1];
				i++;
			} else if ("-update".equals(args[i])) {
				create = false;
			}
		}

		if (docsPath == null) {
			System.err.println("Usage: " + usage);
			System.exit(1);
		}

		final File docDir = new File(docsPath);
		if (!docDir.exists() || !docDir.canRead()) {
			System.out.println("Document directory '" +docDir.getAbsolutePath()+ "' does not exist or is not readable, please check the path");
			System.exit(1);
		}

		Date start = new Date();
		try {
			System.out.println("Indexing to directory '" + indexPath + "'...");

			Directory dir = FSDirectory.open(new File(indexPath).toPath());
			Analyzer analyzer = new Analyzer() {
                @Override
                protected TokenStreamComponents createComponents(String fieldName) {
                    StringReader reader = new StringReader(fieldName);
                    Tokenizer tokenizer = new StandardTokenizer();
                    tokenizer.setReader(reader);
                    TokenStream tokenStream = new LowerCaseFilter(tokenizer);
                    tokenStream = new PorterStemFilter(tokenStream);
                    return new TokenStreamComponents(tokenizer, tokenStream);
                }
            };
			IndexWriterConfig iwc = new IndexWriterConfig(analyzer);

			if (create) {
				iwc.setOpenMode(OpenMode.CREATE);
			} else {
				iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);
			}
            
			iwc.setRAMBufferSizeMB(256.0);

			IndexWriter writer = new IndexWriter(dir, iwc);
			indexDocs(writer, docDir);

			writer.close();

			Date end = new Date();
			System.out.println(end.getTime() - start.getTime() + " total milliseconds");

		} catch (IOException e) {
			System.out.println(" caught a " + e.getClass() +
					"\n with message: " + e.getMessage());
		}
	}

    static void indexDocs(IndexWriter writer, File file)
			throws IOException {

		if (file.canRead()) {
			if (file.isDirectory()) {
				String[] files = file.list();
				// an IO error could occur
				if (files != null) {
					for (int i = 0; i < files.length; i++) {
						indexDocs(writer, new File(file, files[i]));
					}
				}
			} else {
				TrecDocIterator docs = new TrecDocIterator(file);
				Document doc;
                String newLine = System.getProperty("line.separator");
                //FileWriter docHeadlineFields = new FileWriter("titles.txt");
                //FileWriter docbodyFields = new FileWriter("body.txt");

				while (docs.hasNext()) {
					doc = docs.next();
					if (doc != null)
                        //docHeadlineFields.write(doc.getField("title") + newLine);
                        //docbodyFields.write(doc.getField("body") + newLine);
						writer.addDocument(doc);
				}
                //docHeadlineFields.close();
            }
		}
	}
}


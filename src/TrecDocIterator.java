import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Iterator;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.FieldType;
import org.apache.lucene.document.NumericDocValuesField;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;

public class TrecDocIterator implements Iterator<Document> {

	protected BufferedReader rdr;
	protected boolean at_eof = false;
	
	public TrecDocIterator(File file) throws FileNotFoundException {
		rdr = new BufferedReader(new FileReader(file));
		System.out.println("Reading " + file.toString());
	}
	
	@Override
	public boolean hasNext() {
		return !at_eof;
	}

	@Override
	public Document next() {
		Document doc = new Document();
		try {
			String line;
			Pattern docid_tag = Pattern.compile("<docid>\\s*(\\S+)\\s*<");
            Pattern title_tag = Pattern.compile("<title>(.+?)</title>");
            Pattern body_tag = Pattern.compile("<body>(.+?)</body>");
            
            FieldType fieldType = new FieldType(TextField.TYPE_STORED);
            fieldType.setStoreTermVectors(true);
            
            
			boolean in_doc = false;

			while (true) {
				line = rdr.readLine();
				if (line == null) {
					at_eof = true;
					break;
				}
				if (!in_doc) {
					if (line.startsWith("<doc>"))
                    {
						in_doc = true;
                    }
					else
						continue;
				}
				if (line.startsWith("</doc>")) {
					in_doc = false;
					break;
				}

				Matcher m = docid_tag.matcher(line);
				if (m.find()) {
					String docid = m.group(1);
					doc.add(new StringField("docid", docid, Field.Store.YES));
				}
                
                m = title_tag.matcher(line);
                if (m.find()) {
                    String title = m.group(1);
                    doc.add(new Field("title", title, fieldType));
                }
                
                m = body_tag.matcher(line);
                if (m.find()) {
                    String body = m.group(1);
                    doc.add(new Field("body", body, fieldType));
                }
            }
			
		} catch (IOException e) {
			doc = null;
		}
		return doc;
	}

	@Override
	public void remove() {
		// Do nothing, and don't complain
	}

}

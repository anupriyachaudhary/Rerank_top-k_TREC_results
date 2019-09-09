import os
import sys

#make dict of edocid->idocid
def getIdocid():
    os.system('java -cp "bin:lib/*" InspectIndex -index index/ -list-docids > edocid.txt')
    iDocid = dict()
    with open('edocid.txt') as f:
        for line in f:
            words = line.split()
            if(words[0] == '-list-docids:'):
                continue
            else:
                iDocid[words[6]] = words[4]
    return iDocid


def get_doc_length(docid, field):
    os.system('java -cp "bin:lib/*" InspectIndex -index index/ -list-termvector-field ' +\
              docid + ' ' + field +' > term.txt')
    with open('term.txt') as file:
        for line in file:
            words = line.split()
            if(len(words) == 0):
                continue
            elif(words[0] == "The"):
                return 0
                break
            elif(words[0] == "TermVector:"):
                continue
            elif(words[0] == "Vocabulary"):
                return int(words[2])
                break
            else:
                continue
            
if __name__ == "__main__":  
    iDocid = getIdocid()            
    with open(sys.argv[1]) as qrels:
        for line in qrels:
            if(len(line.split()) == 4):
                key, itr, edocid, rel_score = line.split()
                if edocid in iDocid:
                    idocid = iDocid[edocid]
                    len_title = get_doc_length(idocid, "title")
                    len_body = get_doc_length(idocid, "body")
                    line = str(key) + " " + str(rel_score) + " " + str(edocid) + " " + str(idocid) \
                              + " " + str(len_title) + " " + str(len_body)
                    sys.stdout.write(line + '\n')
    os.remove("term.txt")
    os.remove("edocid.txt")

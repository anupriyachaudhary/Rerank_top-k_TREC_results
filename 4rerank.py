import os
import sys

if __name__ == "__main__":
    docidDict = {}
    with open(sys.argv[1]) as f:
        for line in f:
            words = line.split()
            key = words[0]
            edocid = words[2]
            docno = words[3]
            docidDict[docno] = edocid

    qkey = ""
    scorelist = {}
    with open(sys.argv[2]) as f:
        for line in f:
            words = line.split()
            qkey = words[0]
            docno = words[1]
            scorelist[float(words[2])] = docidDict[docno]

            
    fi = open('newscores_tmp.txt', 'w')
    i = 0 
    scores = []
    for key in sorted(scorelist):
        if(i == 0):
            scores = [[scorelist[key], key]]
        else:
            scores.append([scorelist[key], key])
        i = i + 1


    fi = open(sys.argv[3], 'w')
    length = len(scores)
    for i in range(0, length):
        line = str(qkey) + " Q0 " + str(scores[(length-1 -i)][0]) + " " + str(i) + " " + str(scores[(length-1 -i)][1]) + " newscore(RM)"
        fi.write(line)
        fi.write('\n')
    fi.close()
    os.remove('newscores_tmp.txt')

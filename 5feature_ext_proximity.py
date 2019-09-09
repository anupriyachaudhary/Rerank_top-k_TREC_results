import os
import sys
import math
from nltk.stem.porter import *
import nltk
from nltk.corpus import stopwords

#remove stopwords, normalize and stem the terms in queries and store them in titleQueries dictionary
def getQueries(queryFile):
    titleQueries = dict()
    stop_words = stopwords.words('english')
    stemmer = PorterStemmer()           
    with open(queryFile) as queries:
        for query in queries:
            stemmed_query = []
            query = query.split()
            key = query.pop(0)
            for term in query:
                term = term.lower()
                if term in stop_words:
                    continue
                else:
                    term = stemmer.stem(term)
                    term = str(term)
                    stemmed_query.append(term)
            titleQueries[key] = stemmed_query
    return titleQueries

# get numDocs_title, avglen_title, numDocs_body, avglen_body for entire collection                     
def getDataStats():
    os.system('java -cp "bin:lib/*" InspectIndex -index ../trunk_lucene/index/ -list-stats ' + ' > stats.txt')
    with open('stats.txt') as file:
        for line in file:
            parts = line.split()
            if(parts[0] == "title:"):
                numDocs_title = int(parts[1].split("=")[1])
                avglen_title = float(parts[3].split("=")[1])
            if(parts[0] == "body:"):
                numDocs_body = int(parts[1].split("=")[1])
                avglen_body = float(parts[3].split("=")[1])
    os.remove("stats.txt")
    return [numDocs_title, avglen_title, numDocs_body, avglen_body]

#parse postings of a given (term, field)  and store in totalPostings<-(df,ctf), docPostings<-(docid,tf, positions)
def query_doc_postings(term, field, totalPostings, docPostings):
    os.system('java -cp "bin:lib/*" InspectIndex -index ../trunk_lucene/index/ -list-postings ' + term + ' ' + field + ' > postings.txt')
    with open('postings.txt') as file:
        for line in file:
            parts = line.split()
            if(len(parts) == 0):
                continue
            elif(parts[0] == "Postings:"):
                continue
            elif(parts[0] == "df:"):
                if(parts[1] == "0"):
                    del docPostings[term]
                    return 
                else:
                    totalPostings[term] = [int(parts[1])]
            elif(parts[0] == "ctf:"):
                totalPostings[term].append(int(parts[1]))
            elif(parts[0] == "docid:"): 
                docid = parts[1]
                docPostings[term][docid] = {}    
            elif(parts[0] == "tf:"):
                if(parts[0] == "0"):
                    del docPostings[term][docid]
                else:
                    docPostings[term][docid] = [int(parts[1])]
            elif(parts[0] == "Positions:"):
                parts.pop(0)
                if(parts != []):
                    docPostings[term][docid].append(list(map(int, parts)))
            else:
                continue
    
#Calculate bm25 score
def calc_bm25(numDocs, doclen, avglen, df, ctf, tf):
    k = 1.2
    b = 0.75
    totalFreq = (tf*(k + 1))/(tf + k*(1 - b + (b*doclen)/avglen))
    idf = math.log(((numDocs - df + 0.5)/(df + 0.5)), 10)
    return totalFreq*idf

#Calculate tfidf score
def calc_tfidf(numDocs, df, tf):
    totalFreq = math.sqrt(tf)
    idf = 1 + math.log((numDocs/(df + 1.0)), 10)
    return totalFreq*idf
                
#check if given window contains all the terms present atleast once
def isFeasible(pos_term, window):
    isFeasible = False
    for key in pos_term:
        minPos = window[0]
        maxPos = window[1]
        for pos in pos_term[key]:
            if(pos >= minPos and pos <= maxPos):
                isFeasible = True
                break
            else:
                isFeasible = False
        if(isFeasible == False):
            return isFeasible
    return isFeasible

#If no. of terms present = 1, then minWin = 1
#If no. of terms present = 0, then minWin = sys.maxint
#If no. of terms present > 1, then minWin = shortest doc. segment that covers each terms (present) atleast once        
def cal_minWindow(pos_term):    
    x = 0
    y = 0
    window = (x, y)
    windows = []
    minWindow = sys.maxint
    
    if(len(pos_term) == 0):
        return minWindow
    if(len(pos_term) == 1):
        return 1
    
    #Calculate maximum position among all terms
    maxValue = 0
    i = 0
    for key in pos_term:
        pos_term[key].sort()
        value = int(max(pos_term[key]))
        if(i == 0):
            maxValue = value
        else:
            if(value > maxValue):
                maxValue = value
        i=i+1

    #Calculate all possible window                      
    while(y <= maxValue and x <= maxValue):
        if(isFeasible(pos_term, window) == True):
            windows.append(window)
            x = x+1
            window = (x, y)
        else:
            y = y+1
            window = (x, y)

    #Calculate minimum possible window    
    minWindow = 0
    for i in range(len(windows)):
        if(len(windows) == 0):
            break
        win = windows[i][1] - windows[i][0] + 1
        if(i == 0):
            minWindow = win
        else:
            if(win < minWindow):
                minWindow = win
                
    return minWindow 

#Span window: length of the shortest document segment that covers all query term occurrences in a document, 
#including repeated occurrences.
def calc_span(termList, pos_term):
    minPos = sys.maxint
    maxPos = 0
    noTotalTermOccur = 0
    noTermOccur = 0
    for term in termList:
        if term in pos_term:
            if(min(pos_term[term]) < minPos):
                minPos = min(pos_term[term])
            if(max(pos_term[term]) > maxPos):
                maxPos = max(pos_term[term])
            noTermOccur = noTermOccur + 1
            noTotalTermOccur = noTotalTermOccur + len(pos_term[term])

    window = maxPos - minPos
            
    if(minPos == sys.maxint and maxPos == 0):
        window = sys.maxint
    elif(window == 0):
        window = 1
    else:
        window = window + 1
    return [window, noTermOccur, noTotalTermOccur]

#MinDist: smallest distance value of all pairs of unique matched query terms. 
#AveDist: the average distance value of all pairs of unique matched query terms. 
#MaxDist: the largest distance value of all pairs of unique matched query terms.
def calc_pairSpan(pos_term):
    positions = []
    i = 0
    for term in pos_term:
        if(i == 0):
            positions = [pos_term[term]]
        else:
            positions.append(pos_term[term])
        i = i+1
    
    posDict = {}
    minDist = sys.maxint
    maxDist = 0
    avgDist = 0
    totalDist = 0
    count = 0
    if(len(positions) == 0):
        maxDist = sys.maxint
        avgDist = sys.maxint
    elif(len(positions) == 1):
        minDist = 1
        maxDist = 1
        avgDist = 1
    else:
        for i in range(0, len(positions)):
            posDict["1"] = positions[i]
            for j in range(i + 1, len(positions)):
                posDict["2"] = positions[j]
                window = cal_minWindow(posDict)
                if(window < minDist):
                    minDist = window
                if(window > maxDist):
                    maxDist = window
                totalDist = totalDist + window
                count = count + 1
        avgDist = totalDist/count
    
    return [minDist, maxDist, avgDist]

#get features for given term and document
#bm25_total, bm25_max, bm25_min, tfidf_total, tfidf_max, tfidf_min, noTermOccur, minWin
def getfeatures(idocid, numDocs, doclen, avglen, term, totalPostings, docPostings):
    bm25_total = 0
    bm25_max = 0
    bm25_min = sys.maxint
    tfidf_total = 0
    tfidf_max = 0
    tfidf_min = sys.maxint
    pos_term = {}
    noTermOccur = 0
    for term in termList:
        df = 0
        ctf = 0
        tf = 0
        if term in totalPostings:
            df = totalPostings[term][0]
            ctf = totalPostings[term][1]
        if term in docPostings:
            if idocid in docPostings[term]:
                tf = docPostings[term][idocid][0]
                pos_term[term] = docPostings[term][idocid][1]
                noTermOccur = noTermOccur + 1
        bm25 = calc_bm25(numDocs, doclen, avglen, df, ctf, tf)
        if (bm25 < bm25_min):
            bm25_min = bm25
        if (bm25 > bm25_max):
            bm25_max = bm25
        bm25_total = bm25_total + bm25
        
        tfidf = calc_tfidf(numDocs, df, tf)
        if (tfidf < tfidf_min):
            tfidf_min = tfidf
        if (tfidf > tfidf_max):
            tfidf_max = tfidf
        tfidf_total = tfidf_total + tfidf
    minWin = cal_minWindow(pos_term)
    
    return [bm25_total, bm25_max, bm25_min, tfidf_total, tfidf_max, tfidf_min, noTermOccur, minWin, pos_term]  


if __name__ == "__main__":  
    trainingData1 = open('train_span.txt', 'w')
    trainingData2 = open('train_MinCover.txt', 'w')
    trainingData3 = open('train_MinDist.txt', 'w')
    trainingData4 = open('train_MaxDist.txt', 'w')
    trainingData5 = open('train_AvgDist.txt', 'w')
    
    numDocs_title, avglen_title, numDocs_body, avglen_body = getDataStats()
    titleQueries = getQueries(sys.argv[1])
    
    previousQid = ""
    isKeyDifferent = False
    
    totalPostings_title = {}
    totalPostings_body = {}
    docPostings_title = {}
    docPostings_body = {}
    termList = []
    j = 1
    qrels = sys.stdin.read().strip().split('\n')
    for line in qrels:
        if(len(line.split()) == 6):
            queryid, rel_score, edocid, idocid, doclen_title, doclen_body = line.split()
            doclen_title = int(doclen_title)
            doclen_body = int(doclen_body)
            
            #Get posting of query terms if query is different from last one
            if(queryid == previousQid):
                isKeyDifferent = False
            if(queryid != previousQid and previousQid != ""):
                isKeyDifferent = True
            if(isKeyDifferent == True or previousQid == "" ):
                print j
                j = j + 1
                totalPostings_title = {}
                totalPostings_body = {}
                docPostings_title = {}
                docPostings_body = {}
                termList = []
                for term in titleQueries[queryid]:
                    termList.append(term)
                    docPostings_title[term] = {}
                    query_doc_postings(term, "title", totalPostings_title, docPostings_title)
                    docPostings_body[term] = {}
                    query_doc_postings(term, "body", totalPostings_body, docPostings_body)
            
    
            
            #features
            bm25_title, bm25_max_title, bm25_min_title, tfidf_title, tfidf_max_title, tfidf_min_title, \
                            noTermOccurInTitle, minWin_title, pos_term_title = getfeatures(idocid, numDocs_title, doclen_title, avglen_title, 
                                                           termList, totalPostings_title, docPostings_title)
            bm25_body, bm25_max_body, bm25_min_body, tfidf_body, tfidf_max_body, tfidf_min_body, \
                            noTermOccurInBody, minWin_body, pos_term_body = getfeatures(idocid, numDocs_body, doclen_body, avglen_body, \
                                                                           termList, totalPostings_body, docPostings_body)
            
            sum_bm25 = bm25_title + bm25_body
            sum_tfidf = tfidf_title + tfidf_body
            
            #Span       
            windowStats_title1 = calc_span(termList, pos_term_title)
            span_title = windowStats_title1[0]
            noTermOccurInTitle = windowStats_title1[1] 
            noTotalTermOccurInTitle = windowStats_title1[2]
            
            windowStats_body1 = calc_span(termList, pos_term_body)
            span_body = windowStats_body1[0]
            noTermOccurInBody = windowStats_body1[1]  
            noTotalTermOccurInBody = windowStats_body1[2]
    
    
            #Min Coverage: length of the shortest document segment that covers each query term at least once in a document.
            #same as minWin
            minCov_title = minWin_title
            minCov_body = minWin_body
    
    
            #Pairwise distance
            windowStats_title3 = calc_pairSpan(pos_term_title)
            minDist_title = windowStats_title3[0]
            maxDist_title = windowStats_title3[1]
            avgDist_title = windowStats_title3[2]
            
            windowStats_body3 = calc_pairSpan(pos_term_body)
            minDist_body = windowStats_body3[0]
            maxDist_body = windowStats_body3[1]
            avgDist_body = windowStats_body3[2]
            
            line = str(rel_score) + " " + "qid:" + str(int(queryid)) \
                      + " 1:" + str(bm25_title) \
                      + " 2:" + str(bm25_min_title) \
                      + " 3:" + str(bm25_max_title) \
                      + " 4:" + str(bm25_title/len(termList)) \
                      + " 5:" + str(bm25_body) \
                      + " 6:" + str(bm25_min_body) \
                      + " 7:" + str(bm25_max_body) \
                      + " 8:" + str(bm25_body/len(termList)) \
                      + " 9:" + str(sum_bm25) \
                      + " 10:" + str(tfidf_title) \
                      + " 11:" + str(tfidf_min_title) \
                      + " 12:" + str(tfidf_max_title) \
                      + " 13:" + str(tfidf_title/len(termList)) \
                      + " 14:" + str(tfidf_body) \
                      + " 15:" + str(tfidf_min_body) \
                      + " 16:" + str(tfidf_max_body) \
                      + " 17:" + str(tfidf_body/len(termList)) \
                      + " 18:" + str(sum_tfidf)
            
            trainingData1.write(line + " 19:" + str(span_title) + " 20:" + str(span_body) + " # " + str(edocid) + '\n')
            trainingData2.write(line + " 19:" + str(minCov_title) + " 20:" + str(minCov_body) + " # " + str(edocid) + '\n')
            trainingData3.write(line + " 19:" + str(minDist_title) + " 20:" + str(minDist_body) + " # " + str(edocid) + '\n')
            trainingData4.write(line + " 19:" + str(maxDist_title) + " 20:" + str(maxDist_body) + " # " + str(edocid) + '\n')
            trainingData5.write(line + " 19:" + str(avgDist_title) + " 20:" + str(avgDist_body) + " # " + str(edocid) + '\n')
            
            previousQid = queryid
    trainingData1.close()
    trainingData2.close()
    trainingData3.close()
    trainingData4.close()
    trainingData5.close()

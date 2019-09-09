import re
import sys
import xml.etree.ElementTree as ET

if __name__ == "__main__":
    root = ET.Element('add')
    root.text = '\n'    # newline before the 'doc' element

    isField = False
    with open(sys.argv[1]) as f:
        i = 0
        for doc in f:
            trecData = ET.SubElement(root, 'doc')
            trecData.text = '\n'    # newline before the collected element ('docno', 'title', 'body' )
            trecData.tail = '\n'  # empty line after the 'doc' element
            
            if doc.isspace():
                trecData = ET.SubElement(root, 'doc')
                trecData.text = '\n'
                trecData.tail = '\n'
                
            fields = re.split(r'\t+', doc.rstrip('\t'))
            e = ET.SubElement(trecData, 'docid')
            e.text = fields[0]
            e.tail = '\n'
            
            if (len(fields) == 3 and fields[2] != '\n'):
                e = ET.SubElement(trecData, 'title')
                e.text = fields[1]
                e.tail = '\n'
                e = ET.SubElement(trecData, 'body')
                e.text = fields[2].rstrip('\n')
                e.tail = '\n'
            
            #if docid and title are present and body is empty
            elif(len(fields) == 3 and fields[2] == '\n'):
                e = ET.SubElement(trecData, 'title')
                e.text = fields[1].rstrip('\n')
                e.tail = '\n'

            #if only docid and body are present
            elif (len(fields) == 2 and fields[1] != '\n'):
                e = ET.SubElement(trecData, 'body')
                e.text = fields[1].rstrip('\n')
                e.tail = '\n'
            
            #if only docid is present
            elif (len(fields) == 2 and fields[1] == '\n'):
                continue
            i = i + 1
            

    # Display for debugging            
    #ET.dump(root)

    # Include the root element to the tree and write the tree
    # to the file.
    tree = ET.ElementTree(root)
    tree.write('trec45.xml', encoding='utf-8', xml_declaration=True)

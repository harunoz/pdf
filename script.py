import os
import jsonpickle
import glob
import io
import random

### Class Import
from RawData import RawData

### Function Import
from ai_helper import saveStringFile
from ai_helper import loadStringFile
from ai_helper import readFiles

### pdfminer Imports
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

### Resources
# https://stackoverflow.com/questions/17098675/searching-text-in-a-pdf-using-python
# https://pypi.org/project/pdfminer/#description
# https://www.geeksforgeeks.org/working-with-pdf-files-in-python/
# https://pdfminersix.readthedocs.io/en/latest/tutorial/composable.html
# https://stackoverflow.com/questions/14209214/reading-the-pdf-properties-metadata-in-python
# https://www.blog.pythonlibrary.org/2018/05/03/exporting-data-from-pdfs-with-python/
# https://pdfminersix.readthedocs.io/en/latest/
# https://buildmedia.readthedocs.org/media/pdf/pdfminer-docs/latest/pdfminer-docs.pdf
# https://pdfminer-docs.readthedocs.io/programming.html
# https://www.guru99.com/python-check-if-file-exists.html

### JSON Resources
# https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
# https://jsonpickle.github.io/

### Parsing Resources
# https://stackoverflow.com/questions/16523767/what-is-this-cid51-in-the-output-of-pdf2txt


## Main Program Logic and Processing

def processPDF(filepath):
    head, tail = os.path.split(filepath)        ## Fetch the filename and path itself
    readData = readText(filepath)

    ## First fetch the raw data
    rawData = RawData(
        pages= readData["pages"],
        id=tail, 
        metadata=readData["metadata"], 
        outline= readData["outline"]
    )

    saveStringFile(jsonpickle.encode(rawData), "processed/raw/"+ tail + "_raw.txt")
    saveStringFile(readData["text"][0], "processed/rawtext/"+ tail + "_rawtext.txt")

def readText(filepath):   
    output = {} # Output list, [pages, metadata, outline, raw text]
    text = []  
    output_string = StringIO()
    outlines = []

    output["pages"] = 0
    output["metadata"] = ""
    output["text"] = ""
    output["outline"] = []

    #read each pdf file
    with open(filepath, 'rb') as in_file:
        #parse the file
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        output["metadata"] = str(doc.info)
        rsrcmgr = PDFResourceManager()
        #convert to text reading page by pages
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Try to get the outlines
        pdfOutline = []
        try:
            outlines = doc.get_outlines()
            for (level,title,dest,a,se) in outlines:
                pdfOutline.append(level + "," + title)
        except:
            pass
        output["outline"] = pdfOutline

        for page in PDFPage.create_pages(doc):
            output["pages"] = output["pages"] + 1                               # A little sloppy. There has to be a better function somewhere...
            interpreter.process_page(page)
    #extracted text appending to the TEXT list defined above
    text.append(output_string.getvalue())
    output["text"] = text

    return output


# Initialize the python program
def init():

    ## First step, generate RawData PDF objects of every pdf
    count = 1

    files = readFiles("papers\*\*.pdf")

    random.shuffle(files)



    for document in files:
        ## Process all files, into raw and metadata
        print(str(count) + "/" + str(len(files)) + " | processing: " + document)
        head, tail = os.path.split(document)

        try:
            if (os.path.exists("processed/raw/"+ tail + "_raw.txt") and os.path.exists("processed/rawtext/"+ tail + "_rawtext.txt")):
                print("Processed file already exists: " + document)
            else:
                processPDF(document)      
        except Exception as e:
            print("Exception occurred with: " + document + " | Log saved to /logs")
            saveStringFile(str(e), "logs/" + tail + ".log")

        ## Clean files

        count = count + 1

init()

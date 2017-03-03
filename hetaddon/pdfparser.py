from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import *
import tempfile
from typing import List


class PdfParser:
    def __init__(self, document):
        self.file = tempfile.SpooledTemporaryFile(max_size=document.size, mode="rb")
        self.file.write(document.content)
        parser = PDFParser(self.file)
        self.document = PDFDocument(parser)
        if not self.document.is_extractable:
            raise PDFTextExtractionNotAllowed


    def get_pages(self) -> List[LTPage]:
        # Create a PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()
        # Create a PDF device object.
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # Process each page contained in the document.
        pages = []
        for page in PDFPage.create_pages(self.document):
            interpreter.process_page(page)
            page_layout = device.get_result()
            pages.append(page_layout)
        return pages

    def get_outlines(self):
        outlines = self.document.get_outlines()
        for (level,title,dest,a,se) in outlines:
            print(level, title, dest)

    def close_file(self):
        self.file.close()
import sys, os, tempfile, pdb, traceback, pytesseract
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes

#sudo -H pip3 install pytesseract pdf2image
#sudo apt install poppler-utils tesseract-ocr

class OCR_PDF_FromMemory:
    def __init__(self, pdf_data, dpi=200):
        self.pdf_data = pdf_data
        self.dpi = dpi
        self.__enter__()
    
    # Methods for this to work using with keyword:
    def __enter__(self):
        self.create_temporary_dir()
        self.split_pages()
        return self
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            exit(-1)
        self.cleanup()
    
    # Simple set-ups and tear-downs:
    def create_temporary_dir(self):
        self.tempdir = tempfile.TemporaryDirectory()
    
    def cleanup(self):
        self.tempdir.cleanup()
    
    # Other set-ups and tear-downs:
    def split_pages(self):
        self.page_data = convert_from_bytes(
            self.pdf_data,
            dpi=self.dpi,
            )
    
    def extract_text(self, page_num, x1, y1, w, h):
        the_page = self.page_data[page_num]
        # Cut the page:
        real_dimms = (x1, y1, x1+w, y1+h)
        region = the_page.crop(real_dimms)
        region_filename = os.path.join(
            self.tempdir.name,
            "pag%d_%d_%d_%d_%d.jpg" % ((page_num,)+real_dimms) )
        region.save(region_filename, 'JPEG')
        # Recognize characters and retur them:
        recog_bytes = pytesseract.image_to_string(region_filename)
        return recog_bytes

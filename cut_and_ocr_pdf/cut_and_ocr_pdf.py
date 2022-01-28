import sys, os, tempfile, pdb, traceback, pytesseract
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes

#sudo -H pip3 install pytesseract pdf2image
#sudo apt install poppler-utils tesseract-ocr

# This library needs a temporary directory, at least for caching and debugging:
KNOWN_DIR               = "/home/jj/temp_ocr/"
PAGE_FILENAME_TEMPLATE  = "Page_%03d.jpeg"
DEBUG                   = True
DEFAULT_DPI             = 100

def deltree(pathnm):
    if os.path.isfile(pathnm):
        os.unlink(pathnm)
    elif os.path.isdir(pathnm):
        for subitem in os.listdir(pathnm):
            deltree(os.path.join(pathnm, subitem))
        os.rmdir(pathnm)

class OCR_PDF_FromMemory:
    tempdir         = False
    workdir_name    = False
    
    def __init__(self, pdf_data, dpi=DEFAULT_DPI):
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
        if not KNOWN_DIR:
            self.tempdir = tempfile.TemporaryDirectory()
            self.workdir_name = self.tempdir.name
        else:
            self.workdir_name = KNOWN_DIR
            if os.path.exists(self.workdir_name):
                deltree(self.workdir_name)
            os.mkdir(self.workdir_name)
    
    def cleanup(self):
        if self.tempdir:
            self.tempdir.cleanup()
    
    # Other set-ups and tear-downs:
    def split_pages(self):
        self.page_data = convert_from_bytes(
            self.pdf_data,
            dpi=self.dpi,
            )
        if DEBUG:
            for (pagnum, pagdata) in enumerate(self.page_data):
                pagdata.save(os.path.join(self.workdir_name, PAGE_FILENAME_TEMPLATE%(pagnum)))
    
    # Getters and setters:
    def get_page_dimms(self, page_num):
        pdb.set_trace()
        return (0, 0)
    
    # Juicy methods:
    def extract_text_bypoints(self, page_num, x1, x2, y1, y2):
        the_page = self.page_data[page_num]
        # Cut the page:
        real_dimms = (x1, y1, x2, y2)
        region = the_page.crop(real_dimms)
        region_filename = os.path.join(
            self.workdir_name,
            "pag%d_%d_%d_%d_%d.jpg" % ((page_num,)+real_dimms) )
        region.save(region_filename, 'JPEG')
        # Recognize characters and retur them:
        recog_bytes = pytesseract.image_to_string(region_filename)
        return recog_bytes
    
    def extract_text_bybox(self, page_num, x1, y1, w, h):
        return self.extract_text_bypoints(
            page_num,
            x1 = x1,
            x2 = x1+w,
            y1 = y1,
            y2 = y1+h)

class OCR_PDF_FromFile(OCR_PDF_FromMemory):
    def __init__(self, pdf_filename, dpi=DEFAULT_DPI):
        with open(pdf_filename, "rb") as filehand:
            pdf_data = filehand.read()
        super(OCR_PDF_FromFile, self).__init__(pdf_data, dpi)

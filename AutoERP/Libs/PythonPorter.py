import os, re, pdb, subprocess
from io import StringIO

class BinaryFileException(BaseException):
    pass

class PythonPorter:
    macroes_dikt = {}
    
    def __init__(self, macrodir, sourcedir, destdir, filename_regex="(.*\.py|.*\.xml|.*\.csv|.*\.po|.*\.pot)$"):
        self.macrodir       = macrodir
        self.sourcedir      = sourcedir
        self.destdir        = destdir
        self.filename_regex = re.compile(filename_regex, flags=0)
    
    def load_macros(self):
        # Load list of macros:
        all_macro_keys = os.listdir(self.macrodir)
        self.macroes_dikt = {}
        # Load all macroes on-at-a-time:
        for this_macro_key in all_macro_keys:
            macro_filepath = os.path.join(self.macrodir, this_macro_key)
            macrofileh = open(macro_filepath, "r")
            this_macro_value = macrofileh.read().strip()
            self.macroes_dikt[this_macro_key] = this_macro_value
            macrofileh.close()
    
    def apply_macroes_to_file(self, filename):
        if not self.filename_regex.search(filename):
            raise BinaryFileException()
        srcfile = open(filename, "r")
        srctxt = srcfile.read()
        srcfile.close()
        # Apply all macroes:
        dsttxt = srctxt
        for macrokey in self.macroes_dikt.keys():
            dsttxt = dsttxt.replace(macrokey, self.macroes_dikt[macrokey])
        return dsttxt
    
    def preprocess_find_output(self, find_output):
        haldir = [
            re.sub("^"+self.sourcedir+"/*", "", dirpath)
            for dirpath in find_output.strip().split()
            ]
        return haldir
    
    def find_dirs(self):
        find_output = subprocess.check_output([ "find", self.sourcedir, "-type", "d" ])
        #, in_stream=StringIO(postgres_input)
        haldir = self.preprocess_find_output(find_output.decode())
        return haldir
    
    def find_files(self):
        find_output = subprocess.check_output([ "find", self.sourcedir, "-type", "f" ])
        #, in_stream=StringIO(postgres_input)
        halfile = self.preprocess_find_output(find_output.decode())
        return halfile
    
    def filter_matching(self, fileslist):
        halmatching = [ dirpath for dirpath in fileslist if self.filename_regex.search(dirpath) ]
        return halmatching
    
    def filter_non_matching(self, fileslist):
        halnotmatching = [ dirpath for dirpath in fileslist if not self.filename_regex.search(dirpath) ]
        return halnotmatching
    
    def copy_dir_structure(self):
        haldirs = self.find_dirs()
        subprocess.check_output(["mkdir", "-p", self.destdir])
        for thisdir in haldirs:
            thisdir_relative = re.sub("^"+self.sourcedir+"/*", "", thisdir)
            subprocess.check_output(["sudo", "rm", "-rf", os.path.join(self.destdir, thisdir_relative)])
        for thisdir in haldirs:
            thisdir_relative = re.sub("^"+self.sourcedir+"/*", "", thisdir)
            subprocess.check_output([ "mkdir", os.path.join(self.destdir, thisdir_relative) ])
    
    def transfer_file(self, filename):
        real_src_path = os.path.join(self.sourcedir, filename)
        real_dst_path = os.path.join(self.destdir, filename)
        subprocess.check_output([ "cp", real_src_path, real_dst_path ])
    
    def preproccess_and_transfer_file(self, filename):
        real_src_path = os.path.join(self.sourcedir, filename)
        real_dst_path = os.path.join(self.destdir, filename)
        #pdb.set_trace()
        try:
            proproc_out = self.apply_macroes_to_file(real_src_path)
        except UnicodeDecodeError:
            print("Wrong charset for file '%s': not utf-8"%(real_src_path,))
            exit(-1)
        dstfile = open(real_dst_path, "w")
        dstfile.write(proproc_out)
        dstfile.close()
    
    def do_preprocess_directory(self):
        self.copy_dir_structure()
        halfiles = self.find_files()
        yesmatching_files = self.filter_matching(halfiles)
        nonmatching_files = self.filter_non_matching(halfiles)
        # Preproccess matching files:
        for thefile in yesmatching_files:
            #pdb.set_trace()
            self.preproccess_and_transfer_file(thefile)
        # Copy nonmathcing files as is:
        for thefile in nonmatching_files:
            self.transfer_file(thefile)

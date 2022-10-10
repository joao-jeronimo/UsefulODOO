import os, re, pdb, subprocess
from io import StringIO

class BinaryFileException(Exception):
    pass

class PythonPorter:
    macroes_dikt = {}
    
    def __init__(self, macrodir, sourcedir, destdir, filename_regex="/[^/.][^/]*(.*\.py|.*\.xml|.*\.csv|.*\.po|.*\.pot)$"):
        self.macrodir       = macrodir
        self.sourcedir      = sourcedir
        self.destdir        = destdir
        self.filename_regex = re.compile(filename_regex, flags=0)
    
    #############################################
    ##### Loading and applying macroes: #########
    #############################################
    def load_macros(self):
        # Load list of macros:
        all_macro_keys = [
            macroname
            for macroname in os.listdir(self.macrodir)
            if not macroname.startswith('.')
            ]
        self.macroes_dikt = {}
        # Load all macroes on-at-a-time:
        for this_macro_key in all_macro_keys:
            macro_filepath = os.path.join(self.macrodir, this_macro_key)
            macrofileh = open(macro_filepath, "r")
            this_macro_value = macrofileh.read().strip()
            self.macroes_dikt[this_macro_key] = this_macro_value
            macrofileh.close()
    
    def apply_macroes_to_string(self, srctxt):
        """
        Applies every macro to the passed string.
        Every macro is applied in order. After last macro is applied, if macro expansion was
        performed at least one time, then the macro expansion is started over again. The
        process is repeated until there is one round without any expansion.
        """
        dsttxt = srctxt
        while True:
            n_replacements = 0
            for macrokey in self.macroes_dikt.keys():
                new_dsttxt = dsttxt.replace(macrokey, self.macroes_dikt[macrokey])
                if dsttxt != new_dsttxt:
                    n_replacements += 1
                dsttxt = new_dsttxt
            if n_replacements == 0:
                break
        return dsttxt
    
    def apply_macroes_to_file(self, filename):
        """
        Reads a file and applies every macro to it.
        """
        # Passed filename must fall within macro expansion scope
        # regex. If not, raise exception:
        if not self.filename_regex.search(filename):
            raise BinaryFileException()
        # Read source file:
        with open(filename, "r") as srcfile:
            srctxt = srcfile.read()
        # Apply all macroes - many time until no replacements rests:
        return self.apply_macroes_to_string(srctxt)
    
    ###################################################################################
    ##### Finding and filtering files ad folders to run the preprocessor on:    #######
    ###################################################################################
    def preprocess_find_output(self, find_output):
        """
        Transforms the absolute paths returned by Unix "find" into paths that
        are relative to self.sourcedir.
        TODO: This does not currently tolerate dirnames or filenames with spaces!
        """
        haldir = [
            re.sub("^"+self.sourcedir+"/*", "", dirpath)
            for dirpath in find_output.strip().split()
            ]
        return haldir
    
    def find_dirs(self):
        """
        Find every subdir of self.sourcedir (does not include self.sourcedir
        itself in the list). Returns a list of relative paths.
        """
        find_output = subprocess.check_output([
            "find", self.sourcedir,
            "-mindepth", "1",
            "-type", "d",
            ])
        haldir = self.preprocess_find_output(find_output.decode())
        return haldir
    def find_files(self):
        """
        The same as find_dirs(), but returns file paths instead of subdirectory paths.
        """
        find_output = subprocess.check_output([
            "find", self.sourcedir,
            "-mindepth", "1",
            "-type", "f",
            ])
        halfile = self.preprocess_find_output(find_output.decode())
        return halfile
    
    def filter_matching(self, fileslist):
        halmatching = [ dirpath for dirpath in fileslist if self.filename_regex.search(dirpath) ]
        return halmatching
    def filter_non_matching(self, fileslist):
        halnotmatching = [ dirpath for dirpath in fileslist if not self.filename_regex.search(dirpath) ]
        return halnotmatching
    
    def compute_absolute_paths(self, filename):
        """
        Compute source and destination absolute paths for filename.
        """
        real_src_path = os.path.join(self.sourcedir, filename)
        real_dst_path = os.path.join(
            self.destdir,
            # Apply macroes to the destination relative file path:
            self.apply_macroes_to_string(filename),
            )
        return (real_src_path, real_dst_path)
    
    ################################################
    ##### Cloning directory structures:      #######
    ################################################
    def copy_dir_structure(self):
        # Find every relative paths of the packet to port:
        alldirs_relative = self.find_dirs()
        # Make the root dir of the final destination, if it does not already exist:
        subprocess.check_output(["mkdir", "-p", self.destdir])
        # Macro-substitute every directory path to create:
        destination_dirs_relative = [
            self.apply_macroes_to_string(onedir_relative)
            for onedir_relative in alldirs_relative
            ]
        # Build full destination paths:
        destination_dirs_absolute = [
            os.path.join(self.destdir, thisdir_relative)
            for thisdir_relative in destination_dirs_relative
            ]
        # Remove original directories at the destination:
        for thisdir_absolute in destination_dirs_absolute:
            subprocess.check_output([
                "sudo", "rm", "-rf", thisdir_absolute,
                ])
        # Create new destinations directories:
        for thisdir_absolute in destination_dirs_absolute:
            subprocess.check_output([
                "mkdir", thisdir_absolute,
                ])
    
    ########################################################################################
    ##### Individual file processing - both with macro expsansion and without it:    #######
    ########################################################################################
    def transfer_file(self, filename):
        """
        Call this for every file that shall NOT undergo macro substitution.
        """
        (real_src_path, real_dst_path) = self.compute_absolute_paths(filename)
        subprocess.check_output([ "cp", real_src_path, real_dst_path ])
    
    def preproccess_and_transfer_file(self, filename):
        """
        Call this for every file that must undergo macro substitution.
        """
        (real_src_path, real_dst_path) = self.compute_absolute_paths(filename)
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

# -*- coding: utf8 -*-
import subprocess

def run_into_string( arglist ):
   progres = str(subprocess.Popen( arglist, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read(), "utf-8")
   return progres

def decrypt_into_string( filenm, password ):
   progres = str(subprocess.Popen( [ "openssl", "aes-128-cbc", "-d", "-k", password, "-in", filenm],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read(),
                     "utf-8")
   return progres

def runprog_shareout(arglist):
    theprog = subprocess.Popen( arglist )
    return theprog.wait()

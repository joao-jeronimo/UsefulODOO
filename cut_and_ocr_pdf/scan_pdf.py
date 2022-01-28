import re, pdb

class OCRPattern:
    def __init__(self, name, detectionPolicy="firstmatch"):
        (self.name, self.detectionPolicy) = (name, detectionPolicy)
    
    #pagenum, x1, y1, x2, y2, w, h
    def getPageNum(self, **kwparams):
        raise NotImplementedError()
    def getX1(self, **kwparams):
        raise NotImplementedError()
    def getY1(self, **kwparams):
        raise NotImplementedError()
    def getX2(self, **kwparams):
        raise NotImplementedError()
    def getY2(self, **kwparams):
        raise NotImplementedError()
    def getW(self, **kwparams):
        raise NotImplementedError()
    def getH(self, **kwparams):
        raise NotImplementedError()
    
    def validatePattern(self, text, **kwparams):
        raise NotImplementedError()
    
    def find(self, scanner):
        valid_matches = []
        (xi, yi) = (0, 0)
        while self.getX1()+xi+self.getW() <= self.getX2():
            while self.getY1()+yi+self.getH() <= self.getY2():
                # Calc coords to detect:
                detect_x1 = self.getX1()+xi
                detect_y1 = self.getY1()+yi
                # Try to detect:
                possible_match = scanner.ocrpdf.extract_text_bybox(self.getPageNum(), detect_x1, detect_y1, self.getW(), self.getH())
                if self.validatePattern(possible_match):
                    valid_matches.append(possible_match)
                # Increment y index var:
                yi += 1
            # Increment x index var:
            xi += 1
        # Return the longest match:
        if  self.detectionPolicy == "firstmatch":
            return valid_matches[0]
        elif self.detectionPolicy == "longestmatch":
            max_match_len = max([len(mat) for mat in valid_matches])
            return [mat for mat in valid_matches if len(mat)==max_match_len][0]
        else:
            raise BaseException("Unknown detection policy %s."%self.detectionPolicy)

class OCRStaticPattern(OCRPattern):
    def __init__(self, name, pageNum, x1, y1, x2, y2, w, h, pattern_regex, detectionPolicy="firstmatch"):
        super(OCRStaticPattern, self).__init__(name, detectionPolicy)
        self.static_parameters = {
            'pageNum': pageNum,
            'x1':x1,'y1':y1,'x2':x2,'y2':y2,
            'w':w,'h':h,
            'pattern_regex': pattern_regex,
            }
    
    #x1, y1, x2, y2, w, h
    def getPageNum(self, **kwparams):
        return self.static_parameters['pageNum']
    def getX1(self, **kwparams):
        return self.static_parameters['x1']
    def getY1(self, **kwparams):
        return self.static_parameters['y1']
    def getX2(self, **kwparams):
        return self.static_parameters['x2']
    def getY2(self, **kwparams):
        return self.static_parameters['y2']
    def getW(self, **kwparams):
        return self.static_parameters['w']
    def getH(self, **kwparams):
        return self.static_parameters['h']
    
    def validatePattern(self, text, **kwparams):
        return re.search(self.static_parameters['pattern_regex'], text, flags=0)

class RigidPDFScanner:
    def __init__(self, ocrpdf):
        self.ocrpdf = ocrpdf
    
    patterns = {}
    
    def addPattern(self, pattern):
        self.patterns[pattern.name] = pattern
    
    def findPattern(self, name):
        return self.patterns[name].find(self)

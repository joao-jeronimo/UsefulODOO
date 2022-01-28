import re, pdb

class OCRPattern:
    def __init__(self, name, detection_policy="firstmatch", pattern_detect=None, pattern_regex=None):
        (self.name, self.detection_policy) = (name, detection_policy)
        if (pattern_detect is not None and pattern_regex is not None) or (pattern_detect is None and pattern_regex is None):
            raise BaseException("You need to provide exactly one pattern_detect or a pattern_regex.")
        if pattern_regex is not None:
            pattern_detect = (lambda text: re.search(pattern_regex, text, flags=0))
        self.pattern_detect = pattern_detect
    
    #x1, y1, x2, y2, w, h
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
    
    def find(self, scanner):
        valid_matches = []
        (xi, yi) = (0, 0)
        while self.getX1()+xi+self.getW() <= self.getX2():
            while self.getY1()+yi+self.getH() <= self.getY2():
                # Calc coords to detect:
                detect_x1 = self.getX1()+xi
                detect_y1 = self.getY1()+yi
                # Try to detect:
                possible_match = scanner.ocrpdf.extract_text_bybox(0, detect_x1, detect_y1, self.getW(), self.getH())
                if self.pattern_detect(possible_match):
                    valid_matches.append(possible_match)
                # Increment y index var:
                yi += 1
            # Increment x index var:
            xi += 1
        # Return the longest match:
        if  self.detection_policy == "firstmatch":
            return valid_matches[0]
        elif self.detection_policy == "longestmatch":
            max_match_len = max([len(mat) for mat in valid_matches])
            return [mat for mat in valid_matches if len(mat)==max_match_len][0]
        else:
            raise BaseException("Unknown detection policy %s."%self.detection_policy)

class OCRStaticPattern(OCRPattern):
    def __init__(self, name, x1, y1, x2, y2, w, h, detection_policy="firstmatch", pattern_detect=None, pattern_regex=None):
        super(OCRStaticPattern, self).__init__(name, detection_policy, pattern_detect, pattern_regex)
        self.static_parameters = {
            'x1'    : x1,
            'y1'    : y1,
            'x2'    : x2,
            'y2'    : y2,
            'w'     : w,
            'h'     : h,
            }
    
    #x1, y1, x2, y2, w, h
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

class RigidPDFScanner:
    def __init__(self, ocrpdf):
        self.ocrpdf = ocrpdf
    
    patterns = {}
    
    def addPattern(self, pattern):
        self.patterns[pattern.name] = pattern
    
    def findPattern(self, name):
        return self.patterns[name].find(self)

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
    
    def find(self, scanner, **kwparams):
        valid_matches = []
        (xi, yi) = (0, 0)
        while self.getX1(**kwparams)+xi+self.getW(**kwparams) <= self.getX2(**kwparams):
            while self.getY1(**kwparams)+yi+self.getH(**kwparams) <= self.getY2(**kwparams):
                # Calc coords to detect:
                detect_x1 = self.getX1(**kwparams)+xi
                detect_y1 = self.getY1(**kwparams)+yi
                # Try to detect:
                possible_match = scanner.ocrpdf.extract_text_bybox(self.getPageNum(**kwparams), detect_x1, detect_y1, self.getW(**kwparams), self.getH(**kwparams))
                if self.validatePattern(possible_match, **kwparams):
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

class OCRIndexedPattern(OCRStaticPattern):
    def __init__(self, name, pageNum, x1, y1, x2, y2, w, h, pattern_regex, detectionPolicy="firstmatch"):
        super(OCRIndexedPattern, self).__init__(name, pageNum, x1, y1, x2, y2, w, h, pattern_regex, detectionPolicy)
        self.static_parameters.update({
            #'w':w,'h':h,
            #'pattern_regex': pattern_regex,
            })
    
    #x1, y1, x2, y2, w, h
    def getPageNum(self, **kwparams):
        return super(OCRIndexedPattern, self).getPageNum(**kwparams)
    def getX1(self, **kwparams):
        return super(OCRIndexedPattern, self).getX1(**kwparams)
    def getY1(self, **kwparams):
        return super(OCRIndexedPattern, self).getY1(**kwparams)
    def getX2(self, **kwparams):
        return super(OCRIndexedPattern, self).getX2(**kwparams)
    def getY2(self, **kwparams):
        return super(OCRIndexedPattern, self).getY2(**kwparams)
    def getW(self, **kwparams):
        return super(OCRIndexedPattern, self).getW(**kwparams)
    def getH(self, **kwparams):
        return super(OCRIndexedPattern, self).getH(**kwparams)
    
    def validatePattern(self, text, **kwparams):
        return super(OCRIndexedPattern, self).validatePattern(text, **kwparams)

class RigidPDFScanner:
    def __init__(self, ocrpdf):
        self.ocrpdf = ocrpdf
    
    patterns = {}
    
    def addPattern(self, pattern):
        self.patterns[pattern.name] = pattern
    
    def findPattern(self, name, **kwparams):
        return self.patterns[name].find(self, **kwparams)

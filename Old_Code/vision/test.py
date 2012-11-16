#!/usr/bin/env python
import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
import cv

def is_rect_nonzero(r):
    (_,_,w,h) = r
    return (w > 0) and (h > 0)

class CamShiftDemo:

    def __init__(self):
        self.capture = cv.CaptureFromCAM(0)
        cv.NamedWindow( "CamShiftDemo", 1 )
        self.storage = cv.CreateMemStorage(0)
        self.cascade = cv.Load("/usr/local/share/opencv/haarcascades/haarcascade_mcs_upperbody.xml")
        self.last_rect = ((0, 0), (0, 0))

    def run(self):
        hist = cv.CreateHist([180], cv.CV_HIST_ARRAY, [(0,180)], 1 )
        backproject_mode = False
        i = 0
        while True:
            i = (i + 1) % 12

            newFrameImage = cv.QueryFrame( self.capture )
            newFrameImageGS = cv.CreateImage ((320, 240), cv.IPL_DEPTH_8U, 1)
            for row in range(0,newFrameImage.height):
                 for col in range(0,newFrameImage.width):
                     newFrameImageGS[row,col] = (newFrameImage[row,col][0] * 0.114 + newFrameImage[row,col][1] * 0.587 +  newFrameImage[row,col][2] * 0.299) 
            if i == 0:
                found=cv.ExtractSURF(newFrameImageGS, None, cv.CreateMemStorage(), (0, 30000, 3, 1))
                #found = cv.HaarDetectObjects(frame, self.cascade, self.storage, 1.2, 2, 0, (20, 20))
                for p in found:
                    # print p
                    self.last_rect = (p[0][0], p[0][1]), (p[0][2], p[0][3])
                    print self.last_rect

            cv.Rectangle( frame, self.last_rect[0], self.last_rect[1], cv.CV_RGB(255,0,0), 3, cv.CV_AA, 0 )
            cv.ShowImage( "CamShiftDemo", frame )

            c = cv.WaitKey(7) % 0x100
            if c == 27:
                break

if __name__=="__main__":
    demo = CamShiftDemo()
    demo.run()
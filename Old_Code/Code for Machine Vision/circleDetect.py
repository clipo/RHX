import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
import cv

class Target:
    
    #def __init__(self):
        #self.capture = cv.CaptureFromCAM(1)
        #cv.NamedWindow("Target", 1)

    def run(self):
        im = cv.LoadImage('test.jpg')
        #im = cv.QueryFrame(self.capture)
        cv.ShowImage("picture",im)
        gray = cv.CreateImage(cv.GetSize(im), 8, 1)
        edges = cv.CreateImage(cv.GetSize(im), 8, 1)

        cv.CvtColor(im, gray, cv.CV_BGR2GRAY)
        #cv.Canny(gray, edges, 20, 55, 3)

        storage = cv.CreateMat(im.width, 1, cv.CV_32FC3)
        cv.HoughCircles(edges, storage, cv.CV_HOUGH_GRADIENT, 5, 25, 200, 10)

        for i in xrange(storage.width - 1):
            radius = storage[i, 2]
            center = (storage[i, 0], storage[i, 1])
            print ("radius:",radius,"center:",center)
            print (radius, center)

            cv.Circle(im, center, radius, (0, 0, 255), 3, 8, 0)

            cv.NamedWindow('Circles')
            cv.ShowImage('Circles', im)
            cv.WaitKey(0)
        cv.ShowImage('output',im)
        x=0
        while x==0:
        # Listen for ESC key
            c = cv.WaitKey(7) % 0x100
            if c == 27:
                x=1
                break


if __name__=="__main__":
    t = Target()
    t.run()

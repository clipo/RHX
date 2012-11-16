import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
import cv

size=(640,480)
hsv_frame = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)
thresholded = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
thresholded2 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
hsv_min = cv.Scalar(0, 50, 170, 0)
hsv_max = cv.Scalar(10, 180, 256, 0)
hsv_min2 = cv.Scalar(170, 50, 170, 0)
hsv_max2 = cv.Scalar(256, 180, 256, 0)
capture = cv.CaptureFromCAM(1)

def detect_and_draw( img ):

    storage = cv.CreateMat(img.width, 1, cv.CV_32FC3)      
    #cv.CvtColor(img,hsv_frame, cv.CV_BGR2HSV)
    cv.InRangeS(hsv_frame, hsv_min, hsv_max, thresholded)
    cv.InRangeS(hsv_frame, hsv_min2, hsv_max2, thresholded2)
    cv.Or(thresholded, thresholded2, thresholded)
    cv.HoughCircles(thresholded, storage, cv.CV_HOUGH_GRADIENT, 1, thresholded.height/4, 100, 40, 20, 200)
    Radius = 0
    x = 0
    y = 0

    for i in range(storage.width):

            print i
            if storage[i,2] >Radius:
                Radius = storage[i, 2]
                x = storage[i, 0]
                y = storage[i, 1]
                center=(x,y)
                print x,y,Radius
            else:
                print "no circle"

                cv.Circle(thresholded, center,Radius, (0, 0, 255), 3, 8, 0)


    cv.ShowImage( "result", thresholded)

if __name__ == '__main__':

    # Start capturing
    capture = cv.CaptureFromCAM(0)    
    # Create the output window
    cv.NamedWindow("result",1)
    while True:
        frame = cv.QueryFrame( capture )
        detect_and_draw(frame)
        c = cv.WaitKey(7)
        if c==27: # Escape pressed
            break

import cv2

from src import driving, imageProcessing, vision

ThrowSpeed = 200

def measurement():

    cv2.namedWindow("Processed")
    obj1 = driving.serialCom()
    image_thread = vision.imageCapRS2()
    knownWidth = 18
    focallength = (59 * 151) / knownWidth
    distances = []
    finaldistance = 0

    while True:

        depth_frame, frame = image_thread.getFrame()
        ballCnts, basketCnts = imageProcessing.getContours(frame)

        if len(basketCnts) > 0:

            basketX, basketY, w, h = imageProcessing.detectObj(frame, basketCnts, False)
            distance = imageProcessing.calc_distance(w)
            #print("Distance: ", distance)
            print(basketX, basketY, h, w)
            if(len(distances) > 15):
                distances.pop(0)
                distances.append(distance)
                finaldistance = sum(distances)/len(distances)
            else:
                distances.append(distance)

            if(finaldistance != 0):
                print("DISTANCE: ", round(finaldistance, 2))

        cv2.imshow('Processed', frame)

        k = cv2.waitKey(1) & 0xFF
        if k == ord("t"):
            print("Throw")
            obj1.startThrow(ThrowSpeed)
        elif k == ord("r"):
            print("Stop throw")
            obj1.stopThrow()
        elif k == ord("q"):
            print("Break")
            break

    image_thread.setStopped(False)
    obj1.setStopped(False)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    measurement()

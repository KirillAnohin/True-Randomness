import cv2

from src import serialCom, imageProcessing, vision

ThrowSpeed = 200


def measurement():
    global ThrowSpeed

    cv2.namedWindow("Processed")
    # obj1 = serialCom.serialCom()
    image_thread = vision.imageCapRS2()
    distances = []
    finaldistance = 0

    while True:

        frame = image_thread.getFrame()
        ballCnts, basketCnts = imageProcessing.getContours(frame, "magenta")

        cv2.imshow('Processed', frame)

        if len(basketCnts) > 0:

            basketX, basketY, w, h = imageProcessing.detectObj(
                frame, basketCnts, False)
            distance = imageProcessing.calc_distance(w)
            print(basketX, basketY, h, w)
            if (len(distances) > 15):
                distances.pop(0)
                distances.append(distance)
                finaldistance = sum(distances)/len(distances)
            else:
                distances.append(distance)

            if (finaldistance != 0):
                print("DISTANCE: ", round(finaldistance, 2))
                print("Speed: ", ThrowSpeed)

        cv2.imshow('Processed', frame)

        k = cv2.waitKey(1) & 0xFF
        # if k == ord("t"):
        #     print("Throw")
        #     obj1.startThrow(ThrowSpeed)
        # elif k == ord("r"):
        #     print("Stop throw")
        #     obj1.stopThrow()
        # elif k == ord("l"):
        #     print("lowering by 1")
        #     ThrowSpeed -= 1
        # elif k == ord("h"):
        #     print("increasing by 1")
        #     ThrowSpeed += 1
        if k == ord("q"):
            print("Break")
            break

    # obj1.setStopped(False)
    # obj1.stopThrow()
    image_thread.setStopped(False)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    measurement()

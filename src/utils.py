def throwStrength(distance, throwStrengths):
    distance = distance - 10
    for pair in throwStrengths:
        if distance == pair[0]:
            print("found equal distance")
            return pair[1]
        if distance < pair[0] and throwStrengths.index(pair) != 0:
            previous = throwStrengths[throwStrengths.index(pair) - 1]
            return previous[1] + (pair[1] - previous[1]) / 2
        elif throwStrengths.index(pair) == 0 and distance < pair[0]:
            return throwStrengths[0][1]
    return 250

def readThrowerFile(failname):
    fail = open(failname)
    andmed = []
    for rida in fail:
        jupp = rida.strip().split(",")
        distance = float(jupp[0])
        speed = float(jupp[1])
        andmed.append((distance, speed))
    fail.close()
    return andmed
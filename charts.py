from matplotlib import pyplot as plt

# TODO: Doesnt work if a dwell isnt long enough to trigger, skips over the rest of the data and doesnt label it because it couldnt move on to the next setpoint (it thinks that its the end of the data)

# Setup variables (CAN CHANGE THESE FOR TUNING SCRIPT)
setpointTemperatureTriggersInOrder = [-70, 0, 75, 350]

stabilityToleranceAllowable = 2
stabilityConsecutivePointsToTrigger = 5 # If its at the setpoint within tolerance 5 times in a row, it will trigger that it is stable

unstabilityToleranceAllowable = 2
unstabilityConsecutivePointsToTrigger = 2 # If its out of tolerance 2 times in a row, it will trigger that it's unstable/changing (using 1 also works but it might break with different/more dynamic data, not sure)


# Misc vars and funcs that the script uses
allStableCoords = []
allUnstableCoords = []

fakeXDataArray = []
fakeYDataArray = [-70,-55,-35,0,1,0,-2,0,1,0,2,0,0,0,1,1,0,0,-1,20,30,40,50,60,70,73,75,74,75,76,75,74,75,76,75,74,100,130,170,180,250,300,345,350,345,346,349,350,350,349,351,352,350,341,300,250,200,150,100,50,0,-50,-65,-70,-71,-70,-72,-70,-69,
                  -70,-55,-35,0,1,0,-2,0,1,0,2,0,0,0,1,1,0,0,-1,20,30,40,50,60,70,73,75,74,75,76,75,74,75,76,75,74,100,130,170,180,250,300,345,350,345,346,349,350,350,349,351,352,350,341,300,250,200,150,100,50,0,-50,-65,-70,-71,-70,-72,-70,-69]

def createFakeXData(maxIndex):
    for xPoint in range(0, maxIndex):
        fakeXDataArray.append(xPoint)

createFakeXData(len(fakeYDataArray))

# Done
def getIndexAtStabilityCoords(yDataArray, targetSetpoint, tolerance, consecutivePointsUntilStability):
    
    consecutivePointsCount = 0

    # Loop thru yData and check the current y point
    for index in range(0, len(yDataArray)):
        currentPoint = yDataArray[index]

        # Check if the current y point is at the target and within tolerance
        if (currentPoint >= targetSetpoint - tolerance) and (currentPoint <= targetSetpoint + tolerance):
            
            # If it's within tolerance, add 1 to the count
            consecutivePointsCount = consecutivePointsCount + 1

            # If it reaches the correct number of points in a row, print and return the coords
            if consecutivePointsCount == consecutivePointsUntilStability:
                print("Found stability point at {}, {}".format(index, currentPoint))
                return (index, currentPoint)
        else:
            consecutivePointsCount = 0

    # If it cant find anything, return nothing
    return (None)

# Done
def getIndexAtUnstabilityCoords(yDataArray, targetSetpoint, tolerance, consecutivePointsUntilUnstability):

    consecutivePointsCount = 0

    # Loop thru yData and check the current y point
    for index in range(0, len(yDataArray)):
        currentPoint = yDataArray[index]

        # print("Current point unstable" + currentPoint)

        # Check if the current y point is outside the target tolerance
        if (currentPoint < targetSetpoint - tolerance) or (currentPoint > targetSetpoint + tolerance):
            # print("Adding unstable point at " + currentPoint)
            # If it's within tolerance, add 1 to the count
            consecutivePointsCount = consecutivePointsCount + 1

            # If it reaches the correct number of points in a row, print and return True and the coords
            if consecutivePointsCount == consecutivePointsUntilUnstability:
                print("Found unstable point at {}, {}".format(index, currentPoint))
                return (index, currentPoint)
        else:
            consecutivePointsCount = 0

    # If it cant find anything, return nothing
    return (None)


# Done
def getStartingStabilityCoords(yDataArray, tolerance, consecutivePointsUntilStability, setpointsToLookFor):
    
    # setup seperate counts
    consecutivePointsCount = []
    for index in range(0, len(setpointsToLookFor)):
        consecutivePointsCount.append(0)

    # Loop thru yData and check the current y point
    for index in range(0, len(yDataArray)):
        currentPoint = yDataArray[index]

        # This will check each temperature trigger until it finds the first one on the graph so you know which part of the cycle you're starting on
        for temperatureIndex in range(0, len(setpointsToLookFor)):

            # Check if the current y point is at the target and within tolerance
            if (currentPoint >= setpointsToLookFor[temperatureIndex] - tolerance) and (currentPoint <= setpointsToLookFor[temperatureIndex] + tolerance):
                
                # If it's within tolerance, add 1 to the count
                consecutivePointsCount[temperatureIndex] = consecutivePointsCount[temperatureIndex] + 1

                # If it reaches the correct number of points in a row, print and return the first temperature index and coords
                if consecutivePointsCount[temperatureIndex] == consecutivePointsUntilStability:
                    print("Found stability point at {}, {}".format(index, currentPoint))
                    return (temperatureIndex, (index, currentPoint))
            else:
                consecutivePointsCount[temperatureIndex] = 0

    return (None)



def findTriggerCoords():

    totalXIndexesDeleted = 0
    dataRemaining = fakeYDataArray
    isAtEndOfData = False

    # Start with searching for a stable section (even if it's already in the stable section at the start of the data)
    temperatureIndex = getStartingStabilityCoords(dataRemaining,stabilityToleranceAllowable,stabilityConsecutivePointsToTrigger,setpointTemperatureTriggersInOrder)[0]
    print('First setpoint index before while {}'.format(temperatureIndex))

    while(isAtEndOfData == False):

        print('Looking for stable temperature = {}'.format(setpointTemperatureTriggersInOrder[temperatureIndex]))
        stableCoords = getIndexAtStabilityCoords(dataRemaining, setpointTemperatureTriggersInOrder[temperatureIndex],stabilityToleranceAllowable,stabilityConsecutivePointsToTrigger)

        if stableCoords == None:
            print("No stable temperature results")
            break
        else:
            adjustedStableResult = (totalXIndexesDeleted + stableCoords[0], stableCoords[1])
            allStableCoords.append(adjustedStableResult)

            # Check if there's enough X values remaining
            if len(dataRemaining) >= stableCoords[0]:

                # Calculate total X indexes that were deleted so it can be ignored going forward
                totalXIndexesDeleted = totalXIndexesDeleted + stableCoords[0]
                
                # Use negative indexing to ignore section of data that we just went through
                takeLastSection = stableCoords[0] - len(dataRemaining)
                dataRemaining = fakeYDataArray[takeLastSection:]

                print(dataRemaining)
            else:
                isAtEndOfData = True
                break

        print('Looking for unstable/changing temperature = {}'.format(setpointTemperatureTriggersInOrder[temperatureIndex]))
        unstableCoords = getIndexAtUnstabilityCoords(dataRemaining, setpointTemperatureTriggersInOrder[temperatureIndex],unstabilityToleranceAllowable,unstabilityConsecutivePointsToTrigger)

        if unstableCoords == None:
            print("No unstable temperature results")
            break
        else:
            adjustedUnstableResult = (totalXIndexesDeleted + unstableCoords[0], unstableCoords[1])
            allUnstableCoords.append(adjustedUnstableResult)

            if len(dataRemaining) >= unstableCoords[0]:

                totalXIndexesDeleted = totalXIndexesDeleted + unstableCoords[0]
                takeLastSection = unstableCoords[0] - len(dataRemaining)
                dataRemaining = fakeYDataArray[takeLastSection:]

                print(dataRemaining)
            else:
                isAtEndOfData = True
                break

        # If it can't find stable or unstable results, the data has probably already been processed and its at the end
        if stableCoords == None and unstableCoords == None:
            isAtEndOfData = True
            break

        # Reset the temperature index so it can keep looping through it
        if temperatureIndex >= len(setpointTemperatureTriggersInOrder) - 1:
            temperatureIndex = 0
            print("Reset temp index")
        else:
            temperatureIndex = temperatureIndex + 1
            
    print("All Stable coords ")
    print(allStableCoords)
    print("All unstable coords ")
    print(allUnstableCoords)

findTriggerCoords()

plt.title("TAIWANNUMBAWAN")
plt.xlabel('Time (s)')
plt.ylabel('Temperature (F)')
plt.plot(fakeXDataArray,fakeYDataArray, color='green')
plt.grid(True)

# Plot all the textboxes with the coords that it found where it switched to stable or unstable conditions
def plotTexts():
    for point in allStableCoords:
        plt.text(point[0], point[1], '{}, {}'.format(point[0], point[1]), color='blue')
    
    for point in allUnstableCoords:
        plt.text(point[0], point[1], '{}, {}'.format(point[0], point[1]), color='red')

plotTexts()
plt.show()
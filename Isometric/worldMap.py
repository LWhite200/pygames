curMap = [[]]        # 2d array  | integers + letter  ' 32f or 99w
curObjects = [[]]    # hash map  | x,y,type,item_id,number
curWalls = []        # hash map  | (x,y)

start = [
    ["2w|n|", "2w|n|", "2w|n|", "2w|n|", "2w|n|", "2w|n|", "2w|n|", "2w|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["2w|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["2w|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["2w|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|"],
    ["2w|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["2w|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["2w|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["2w|n|", "1f|n|", "1f|n|", "6f|n|", "6f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["6f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["6f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|"],
    ["6f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|", "1f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|", "6f|n|"],
]
    
# Reads the array and separates information
def getMap(mapName):
    global curMap, curObjects, curWalls
    curMap = globals().get(mapName, None)  # global 2d array of the same name
    res = []  # Initialize res as an empty list

    for i in range(len(curMap)):
        row = []  # Initialize a new row
        for j in range(len(curMap[0])):
            # string "2w|n|"
            curString = curMap[i][j].split("|")
            row.append(curString[0])  # Append the first element of curString to the row

            if "d" in curString[0]:  # Check if "d" is in the first part of the string
                curWalls.append((i, j))  # Add the coordinate to curWalls

            if curString[1] != 'n':  # If the second part is not 'n'
                curObjects.append(curString[1])  # Append the second element (type) to curObjects
        
        res.append(row)  # After processing each row, append it to the res 2D array

    return res


def getCollision(x, y):
    # Check if (x, y) is in the list of curWalls
    if (x, y) in curWalls:
        return True
    else:
        return False


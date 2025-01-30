# Only have 0, 1, 2 tiles for now. 0 is nothing, 1 is grass, 2 is a wall and or tree
# warp zones = 44

# the object names will be capitalized while the grid's name will not be

startingArea = "warpTest"
sAs = 0

Areas = []

class Area:
    def __init__(self, name, warp):
        self.name = name
        self.warp = warp  # tuple, first one is the place where it is a warp
                          # while the second is a tuple with the name of area and their warp zone

    def sendWarp(self, number):
        if self.warp[number]:  # Checking if a warp exists for that index
            return self.warp[number][1]  # return the name of the target area

# Test grids
test = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 2, 1, 1, 1, 1, 2, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 2, 1, 1, 1, 1, 2, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 11, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
]

warptest = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 1, 1, 1, 1, 1, 1, 2, 2],
    [2,11, 1, 1, 1, 1, 1, 1,22, 2],
    [2, 2, 1, 1, 1, 1, 1, 1, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
]

Test2 = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2,11, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1,22, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1,33, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
]

# takes the name and its zone to see where it warps to
# then returns the new area name and the warp tile number
def getNameWarp(curName, curPosition):
    # Look for the area object that matches curName
    for area in Areas:
        if area.name.lower() == curName.lower():  # Match area name (case insensitive)
            # Iterate through the warp list of the area
            for warp in area.warp:
                if warp[0] == curPosition:  # If the current position matches a warp
                    print(f"Warp found: {warp}")  # Debug statement
                    return (warp[1][0].lower(), warp[1][1])  # Return the tuple with the new area name and new tile number
    print(f"No warp found for {curName} at position {curPosition}")  # Debug statement
    return curName, curPosition  # Return the current name and position if no warp is found

# Returns the grid of a certain name
def getArea(cur):
    grids = {
        "test": test,
        "warptest": warptest,
        "test2": Test2,  # Add the Test2 grid
    }
    cur = cur.lower()  # Convert to lowercase to match key names
    return grids.get(cur, [])  # Default to an empty list if not found

# Returns the position player warped or started on
def getPosition(cur, next):
    grid = getArea(cur.lower())  # Convert string to grid

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == next:
                return (i, j)  # Return (i, j) as the position of the "next" value

# Load the area objects    
def main():
    Areas.append(Area("WARPTEST", [
        (11, ("Test2", 11)), 
        (22, ("warptest", 11))
    ]))
    Areas.append(Area("Test2", [
        (11, ("warptest", 22)), 
        (22, ("test", 11)), 
        (33, ("warptest", 11))
    ]))
    Areas.append(Area("test", [
        (11, ("warptest", 22))
    ]))

if __name__ == "__main__":
    main()
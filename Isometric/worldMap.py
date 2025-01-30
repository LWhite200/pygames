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
    """
    Returns the grid of a certain name by dynamically accessing the global variables.
    Converts the input string to lowercase to match the grid variable names.
    """
    cur = cur.lower()  # Convert to lowercase to match variable names
    try:
        # Use globals() to dynamically access the grid variable
        grid = globals().get(cur)
        if grid is not None:
            return grid
        else:
            print(f"Grid '{cur}' not found.")
            return []  # Return an empty list if the grid is not found
    except Exception as e:
        print(f"Error accessing grid '{cur}': {e}")
        return []  # Return an empty list in case of any error

# Returns the position player warped or started on
def getPosition(cur, next):
    grid = getArea(cur.lower())  # Convert string to grid

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == next:
                return (i, j)  # Return (i, j) as the position of the "next" value
            
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------

bird = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 11, 1, 2, 2, 2, 2],
    [2, 2, 2, 1, 1, 1, 1, 2, 2, 2],
    [2, 2, 1, 1, 1, 1, 1, 1, 2, 2],
    [2, 2, 1, 1, 1, 1, 1, 1, 2, 2],
    [2, 2, 2, 1, 1, 1, 1, 2, 2, 2],
    [2, 2, 2, 2, 1, 22, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
]

ele = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 11, 1, 1, 2, 2, 1, 1, 1, 2],
    [2, 1, 1, 1, 2, 2, 1, 1, 1, 2],
    [2, 1, 1, 1, 2, 2, 1, 1, 1, 2],
    [2, 2, 2, 1, 1, 1, 1, 2, 2, 2],
    [2, 2, 2, 1, 1, 1, 1, 2, 2, 2],
    [2, 1, 1, 1, 2, 2, 1, 1, 1, 2],
    [2, 1, 1, 1, 2, 2, 1, 1, 1, 2],
    [2, 1, 1, 1, 2, 2, 1, 1, 22, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
]

gir = [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 11, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 22, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
]

def main():
    Areas.append(Area("bird", [(11, ("gir", 22)), (22, ("ele", 11))]))
    Areas.append(Area("ele", [(11, ("bird", 22)), (22, ("gir", 11))]))
    Areas.append(Area("gir", [(11, ("ele", 22)), (22, ("bird", 11))]))




if __name__ == "__main__":
    main()
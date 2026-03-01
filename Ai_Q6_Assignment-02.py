import pygame
import math
import random
import heapq 
import time 

# Initialize Pygame
pygame.init()
winWidth, winHeight = 1000, 700 
sidebarWidth = 300
window = pygame.display.set_mode((winWidth, winHeight))
pygame.display.set_caption("Dynamic Pathfinding Agent")

fontSmall = pygame.font.SysFont('Arial', 14)
fontMed = pygame.font.SysFont('Arial', 18, bold=True)
fontLrg = pygame.font.SysFont('Arial', 24, bold=True)

# Themes
themes = {
    "Light": {"bg": (255, 255, 255), "vis": (180, 160, 255), "front": (255, 255, 0), "path": (0, 255, 0), "wall": (0, 0, 0)},
    "Dark":  {"bg": (50, 50, 50),    "vis": (0, 0, 0),       "front": (255, 165, 0), "path": (0, 255, 255), "wall": (255, 255, 255)},
    "Ocean": {"bg": (173, 216, 230), "vis": (0, 191, 255),   "front": (255, 255, 0), "path": (57, 255, 20), "wall": (0, 0, 0)}
}

colorWall = (100, 108, 128)  
colorDynamicWall = (255, 0, 0) 
colorStart = (0, 0, 255)     
colorGoal = (128, 0, 128)    


class Node:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = sidebarWidth + (col * width) 
        self.y = row * width
        self.width = width
        
        self.isWall = False
        self.isDynamicWall = False 
        self.isStart = False
        self.isGoal = False
        
        self.isVisited = False
        self.isFrontier = False
        self.isPath = False
        
        self.neighbors = [] 

    def draw(self, window, currTheme):
        themeDict = themes[currTheme]
        color = themeDict["bg"]
        
        if self.isDynamicWall: color = colorDynamicWall
        elif self.isWall: color = colorWall
        elif self.isStart: color = colorStart
        elif self.isGoal: color = colorGoal
        elif self.isPath: color = themeDict["path"]
        elif self.isVisited: color = themeDict["vis"]
        elif self.isFrontier: color = themeDict["front"]

        rect = pygame.Rect(self.x, self.y, self.width, self.width)
        pygame.draw.rect(window, color, rect)
        pygame.draw.rect(window, (150, 150, 150), rect, 1) # Border

        if self.isStart:
            text = fontLrg.render("S", True, (255, 255, 255))
            window.blit(text, (self.x + self.width//4, self.y + self.width//6))
        elif self.isGoal:
            text = fontLrg.render("G", True, (255, 255, 255))
            window.blit(text, (self.x + self.width//4, self.y + self.width//6))

    def getNeighbors(self, grid, totalRows, totalCols):
        self.neighbors = []
        if self.row < totalRows - 1 and not grid[self.row + 1][self.col].isWall: 
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].isWall: 
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < totalCols - 1 and not grid[self.row][self.col + 1].isWall: 
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].isWall: 
            self.neighbors.append(grid[self.row][self.col - 1])

# Helper Functions
def makeGrid(rows, cols):
    grid = []
    cellWidth = min((winWidth - sidebarWidth) // cols, winHeight // rows)
    for i in range(rows):
        grid.append([])
        for j in range(cols):
            grid[i].append(Node(i, j, cellWidth))
    return grid

def drawButton(window, x, y, w, h, text, isActive, overrideColor=None):
    color = overrideColor if overrideColor else ((180, 180, 180) if not isActive else (100, 255, 100))
    btnRect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(window, color, btnRect)
    pygame.draw.rect(window, (0, 0, 0), btnRect, 2)
    label = fontSmall.render(text, True, (0, 0, 0) if color != (50,50,50) else (255,255,255))
    window.blit(label, (x + 5, y + 2))
    return btnRect

def calcHeuristic(node1, node2, heurType):
    x1, y1 = node1.row, node1.col
    x2, y2 = node2.row, node2.col
    if heurType == "Manhattan":
        return abs(x1 - x2) + abs(y1 - y2)
    else: 
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def clearVisuals(grid):
    for row in grid:
        for node in row:
            node.isVisited = node.isFrontier = node.isPath = False

def checkReachability(grid, startNode, goalNode, rows, cols):
    queue = [startNode]
    visited = {startNode}
    
    while queue:
        curr = queue.pop(0)
        if curr == goalNode: return True
            
        row, col = curr.row, curr.col
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            newRol, newCol = row + dr, col + dc
            if 0 <= newRol < rows and 0 <= newCol < cols:
                neighbor = grid[newRol][newCol]
                if not neighbor.isWall and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return False

def generateRandomMaze(grid, rows, cols, density):
    for r in grid:
        for node in r:
            node.isWall = node.isStart = node.isGoal = False
            node.isDynamicWall = False 
            node.isVisited = node.isFrontier = node.isPath = False
            
    startRow = random.randint(0, rows // 3)
    startCol = random.randint(0, cols // 3)
    startNode = grid[startRow][startCol]
    
    goalRow = random.randint(rows - (rows // 3) - 1, rows - 1)
    goalCol = random.randint(cols - (cols // 3) - 1, cols - 1)
    goalNode = grid[goalRow][goalCol]
    
    startNode.isStart = True
    goalNode.isGoal = True

    totalNodes = (rows * cols) - 2
    targetWalls = int(totalNodes * density)
    wallsPlaced = 0
    attempts = 0
    maxAttempts = totalNodes * 5

    while wallsPlaced < targetWalls and attempts < maxAttempts:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        node = grid[r][c]

        if not node.isStart and not node.isGoal and not node.isWall:
            node.isWall = True 
            
            if checkReachability(grid, startNode, goalNode, rows, cols):
                wallsPlaced += 1
            else:
                node.isWall = False 
                
        attempts += 1

    return startNode, goalNode


def reconstructPath(cameFrom, current, drawFunc):
    path = []
    while current in cameFrom:
        path.append(current)
        current = cameFrom[current]
    path.append(current) 
    path.reverse()
    
    for node in path:
        if not node.isStart and not node.isGoal:
            node.isPath = True
        drawFunc()
        pygame.time.delay(10) 
        
    return path 


def runAlgorithm(drawFunc, grid, startNode, goalNode, algoType, heurType, delay, rows, cols, metrics, walkedHistory=None):
    clearVisuals(grid)
    
    if walkedHistory:
        for n in walkedHistory:
            if not n.isStart and not n.isGoal:
                n.isPath = True

    for row in grid:
        for node in row:
            node.getNeighbors(grid, rows, cols)
            
    count = 0
    expandedNodes = 0
    openSet = []
    heapq.heappush(openSet, (0, count, startNode)) 
    cameFrom = {}
    gScore = {node: float("inf") for row in grid for node in row}
    gScore[startNode] = 0
    fScore = {node: float("inf") for row in grid for node in row}
    fScore[startNode] = calcHeuristic(startNode, goalNode, heurType)
    openSetHash = {startNode} 
    
    totalTimeInMs = 0.0
    
    while openSet:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return []
                
        t0 = time.perf_counter() 
        
        current = heapq.heappop(openSet)[2]
        openSetHash.remove(current)
        
        if current == goalNode:
            t1 = time.perf_counter()
            totalTimeInMs += (t1 - t0) * 1000
            
            finalPath = reconstructPath(cameFrom, goalNode, drawFunc)
            
            metrics["visited"] += expandedNodes
            metrics["cost"] = len(finalPath) - 1 
            metrics["time"] += totalTimeInMs
            return finalPath
            
        expandedNodes += 1
            
        for neighbor in current.neighbors:
            tempGScore = gScore[current] + 1
            if tempGScore < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tempGScore
                
                if algoType == "A*":
                    fScore[neighbor] = tempGScore + calcHeuristic(neighbor, goalNode, heurType)
                elif algoType == "GBFS":
                    fScore[neighbor] = calcHeuristic(neighbor, goalNode, heurType)
                    
                if neighbor not in openSetHash:
                    count += 1
                    heapq.heappush(openSet, (fScore[neighbor], count, neighbor))
                    openSetHash.add(neighbor)
                    neighbor.isFrontier = True
                    
        t1 = time.perf_counter()
        totalTimeInMs += (t1 - t0) * 1000
        
        drawFunc()
        
        agentRect = pygame.Rect(current.x + 8, current.y + 8, current.width - 16, current.width - 16)
        pygame.draw.ellipse(window, (255, 0, 0), agentRect) 
        pygame.draw.ellipse(window, (0, 0, 0), agentRect, 2) 
        pygame.display.update()

        if current != startNode:
            current.isVisited = True
            current.isFrontier = False
            
        pygame.time.delay(delay) 
        
    return [] 

def executeDynamicPath(drawFunc, grid, initialPath, goalNode, algoType, heurType, delay, rows, cols, isDynamic, metrics):
    path = initialPath
    currIdx = 0
    walkedHistory = [] 

    while currIdx < len(path):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        agentNode = path[currIdx]
        walkedHistory.append(agentNode)

        def drawAgent():
            drawFunc() 
            agentRect = pygame.Rect(agentNode.x + 8, agentNode.y + 8, agentNode.width - 16, agentNode.width - 16)
            pygame.draw.ellipse(window, (255, 0, 0), agentRect) 
            pygame.draw.ellipse(window, (0, 0, 0), agentRect, 2) 
            pygame.display.update()

        drawAgent()
        pygame.time.delay(100) 

        if agentNode == goalNode:
            break 

        if isDynamic and currIdx < len(path) - 2:
            if random.random() < 0.10: 
                blockIdx = random.randint(currIdx + 1, len(path) - 1)
                nodeToBlock = path[blockIdx]
                if not nodeToBlock.isGoal and not nodeToBlock.isWall:
                    nodeToBlock.isWall = True 
                    nodeToBlock.isDynamicWall = True 
                    
                    if checkReachability(grid, agentNode, goalNode, rows, cols):
                        nodeToBlock.isPath = False 
                        drawAgent() 
                        pygame.time.delay(150) 
                    else:
                        nodeToBlock.isWall = False 
                        nodeToBlock.isDynamicWall = False
        
        pathIsBlocked = False
        for i in range(currIdx + 1, len(path)):
            if path[i].isWall:
                pathIsBlocked = True
                break
        
        if pathIsBlocked:
            drawAgent() 
            pygame.time.delay(1000) 
            
           
            newPath = runAlgorithm(drawAgent, grid, agentNode, goalNode, algoType, heurType, max(0, delay//2), rows, cols, metrics, walkedHistory)
            
            if newPath:
                path = newPath 
                currIdx = 0    
                walkedHistory.pop() 
                metrics["cost"] = len(walkedHistory) + len(newPath) - 1
            else:
                break 
        else:
            currIdx += 1

# Main Loop
def main():
    cols, rows = 12, 12 
    currTheme = "Light"
    currTool = "wall" 
    currAlgo = "A*"
    currHeur = "Manhattan"
    speed = 50 
    mazeDensity = 0.3 
    isDynamic = False 
    
    metrics = {"visited": 0, "cost": 0, "time": 0.0}
    
    grid = makeGrid(rows, cols)
    startNode = None
    goalNode = None
    running = True

    def drawAll():
        window.fill((230, 230, 230)) 
        
        window.blit(fontMed.render(f"Grid Size: {cols}x{rows}", True, (0,0,0)), (10, 10))
        btnSizeAdd = drawButton(window, 10, 30, 40, 20, "+", False)
        btnSizeSub = drawButton(window, 60, 30, 40, 20, "-", False)

        window.blit(fontMed.render("Themes:", True, (0,0,0)), (10, 60))
        btnLight = drawButton(window, 10, 80, 70, 20, "Light", currTheme == "Light")
        btnDark = drawButton(window, 90, 80, 70, 20, "Dark", currTheme == "Dark")
        btnOcean = drawButton(window, 170, 80, 70, 20, "Ocean", currTheme == "Ocean")

        window.blit(fontMed.render("Customize Map:", True, (0,0,0)), (10, 110))
        btnStart = drawButton(window, 10, 130, 130, 20, "Set Start (S)", currTool == "start")
        btnGoal = drawButton(window, 150, 130, 130, 20, "Set Goal (G)", currTool == "goal")
        btnWall = drawButton(window, 10, 155, 130, 20, "Draw Wall", currTool == "wall")
        btnErase = drawButton(window, 150, 155, 130, 20, "Erase", currTool == "erase")

        window.blit(fontMed.render("Algorithm:", True, (0,0,0)), (10, 185))
        btnAStar = drawButton(window, 10, 205, 100, 20, "A* Search", currAlgo == "A*")
        btnGBFS = drawButton(window, 120, 205, 100, 20, "Greedy (GBFS)", currAlgo == "GBFS")

        window.blit(fontMed.render("Heuristic:", True, (0,0,0)), (10, 235))
        btnManh = drawButton(window, 10, 255, 120, 20, "Manhattan", currHeur == "Manhattan")
        btnEucl = drawButton(window, 140, 255, 120, 20, "Euclidean", currHeur == "Euclidean")
        
        window.blit(fontMed.render("Speed:", True, (0,0,0)), (10, 285))
        btnSlow = drawButton(window, 10, 305, 80, 20, "Slow", speed == 90)
        btnMed = drawButton(window, 100, 305, 80, 20, "Med", speed == 50)
        btnFast = drawButton(window, 190, 305, 80, 20, "Fast", speed == 20)

        window.blit(fontMed.render(f"Obstacle Density: {int(mazeDensity * 100)}%", True, (0,0,0)), (10, 335))
        btnDensAdd = drawButton(window, 10, 355, 40, 20, "+", False)
        btnDensSub = drawButton(window, 60, 355, 40, 20, "-", False)

        window.blit(fontMed.render("Dynamic Obstacles:", True, (0,0,0)), (10, 385))
        dynText = "ON" if isDynamic else "OFF"
        dynColor = (255,100,100) if isDynamic else (50,50,50)
        btnDynamic = drawButton(window, 10, 405, 80, 20, f"Mode: {dynText}", False, overrideColor=dynColor)

        pygame.draw.rect(window, (200, 200, 200), (10, 440, 280, 80))
        pygame.draw.rect(window, (0, 0, 0), (10, 440, 280, 80), 2)
        window.blit(fontMed.render("Results", True, (0,0,0)), (15, 445))
        window.blit(fontSmall.render(f"Nodes Visited: {metrics['visited']}", True, (0,0,0)), (15, 470))
        window.blit(fontSmall.render(f"Path Cost: {metrics['cost']}", True, (0,0,0)), (15, 485))
        window.blit(fontSmall.render(f"Execution Time: {metrics['time']:.2f} ms", True, (0,0,0)), (15, 500))

        btnRandom = drawButton(window, 40, 530, 220, 25, "  GENERATE RANDOM MAZE", False)
        btnClearGrid = drawButton(window, 40, 560, 220, 25, "      Clear Grid", False)
        btnRun = drawButton(window, 40, 590, 220, 35, "    START ALGORITHM", False)
        btnClearVisuals = drawButton(window, 40, 630, 220, 25, "      Clear Path", False)

        for r in grid:
            for node in r:
                node.draw(window, currTheme)
                
        pygame.display.update()
        
        return {
            "add": btnSizeAdd, "sub": btnSizeSub, "light": btnLight, "dark": btnDark, 
            "ocean": btnOcean, "start": btnStart, "goal": btnGoal, "wall": btnWall, 
            "erase": btnErase, "astar": btnAStar, "gbfs": btnGBFS, "manh": btnManh, 
            "eucl": btnEucl, "slow": btnSlow, "med": btnMed, "fast": btnFast,
            "densAdd": btnDensAdd, "densSub": btnDensSub, "dynamic": btnDynamic,
            "random": btnRandom, "run": btnRun, "clearVisuals": btnClearVisuals,
            "clearGrid": btnClearGrid
        }

    while running:
        buttons = drawAll()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]: 
                pos = pygame.mouse.get_pos()
                x, y = pos

                if x < sidebarWidth:
                    if buttons["start"].collidepoint(pos): currTool = "start"
                    elif buttons["goal"].collidepoint(pos): currTool = "goal"
                    elif buttons["wall"].collidepoint(pos): currTool = "wall"
                    elif buttons["erase"].collidepoint(pos): currTool = "erase"
                    
                    elif buttons["light"].collidepoint(pos): currTheme = "Light"
                    elif buttons["dark"].collidepoint(pos): currTheme = "Dark"
                    elif buttons["ocean"].collidepoint(pos): currTheme = "Ocean"
                    
                    elif buttons["astar"].collidepoint(pos): currAlgo = "A*"
                    elif buttons["gbfs"].collidepoint(pos): currAlgo = "GBFS"
                    
                    elif buttons["manh"].collidepoint(pos): currHeur = "Manhattan"
                    elif buttons["eucl"].collidepoint(pos): currHeur = "Euclidean"
                    
                    elif buttons["slow"].collidepoint(pos): speed = 90
                    elif buttons["med"].collidepoint(pos): speed = 50
                    elif buttons["fast"].collidepoint(pos): speed = 20
                    
                    elif buttons["densAdd"].collidepoint(pos) and mazeDensity < 0.5:
                        mazeDensity = round(mazeDensity + 0.1, 1)
                        pygame.time.delay(100) 
                    elif buttons["densSub"].collidepoint(pos) and mazeDensity > 0.0:
                        mazeDensity = round(mazeDensity - 0.1, 1)
                        pygame.time.delay(100)

                    elif buttons["dynamic"].collidepoint(pos):
                        isDynamic = not isDynamic
                        pygame.time.delay(150) 

                    elif buttons["add"].collidepoint(pos) and cols < 20:
                        cols += 1; rows += 1
                        grid = makeGrid(rows, cols) 
                        startNode = goalNode = None 
                        pygame.time.delay(150)
                    elif buttons["sub"].collidepoint(pos) and cols > 5:
                        cols -= 1; rows -= 1
                        grid = makeGrid(rows, cols)
                        startNode = goalNode = None
                        pygame.time.delay(150)
                        
                    elif buttons["random"].collidepoint(pos):
                        startNode, goalNode = generateRandomMaze(grid, rows, cols, mazeDensity)
                        metrics["visited"] = 0
                        metrics["cost"] = 0
                        metrics["time"] = 0.0
                        
                    elif buttons["clearVisuals"].collidepoint(pos):
                        clearVisuals(grid)
                        metrics["visited"] = 0
                        metrics["cost"] = 0
                        metrics["time"] = 0.0

                    elif buttons["clearGrid"].collidepoint(pos):
                        grid = makeGrid(rows, cols)
                        startNode = goalNode = None
                        metrics["visited"] = 0
                        metrics["cost"] = 0
                        metrics["time"] = 0.0
                        
                    elif buttons["run"].collidepoint(pos):
                        if startNode and goalNode:
                            metrics["visited"] = 0
                            metrics["cost"] = 0
                            metrics["time"] = 0.0
                            
                            calculatedPath = runAlgorithm(lambda: drawAll(), grid, startNode, goalNode, currAlgo, currHeur, speed, rows, cols, metrics)
                            if calculatedPath:
                                executeDynamicPath(lambda: drawAll(), grid, calculatedPath, goalNode, currAlgo, currHeur, speed, rows, cols, isDynamic, metrics)

                else:
                    cellWidth = grid[0][0].width
                    clickedCol = (x - sidebarWidth) // cellWidth
                    clickedRow = y // cellWidth
                    
                    if clickedRow < rows and clickedCol < cols:
                        clickedNode = grid[clickedRow][clickedCol]

                        if currTool == "start":
                            if startNode: startNode.isStart = False 
                            clickedNode.isStart = True
                            clickedNode.isWall = clickedNode.isGoal = False
                            startNode = clickedNode
                        elif currTool == "goal":
                            if goalNode: goalNode.isGoal = False 
                            clickedNode.isGoal = True
                            clickedNode.isWall = clickedNode.isStart = False
                            clickedNode.isDynamicWall = False
                            goalNode = clickedNode
                        elif currTool == "wall":
                            if clickedNode != startNode and clickedNode != goalNode:
                                clickedNode.isWall = True
                                clickedNode.isDynamicWall = False
                        elif currTool == "erase":
                            clickedNode.isWall = False
                            clickedNode.isDynamicWall = False

    pygame.quit()

if __name__ == "__main__":
    main()
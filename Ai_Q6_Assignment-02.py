import pygame
import math
import random
import heapq

pygame.init()
winWidth, winHeight = 1000, 700 
sidebarWidth = 300
window = pygame.display.set_mode((winWidth, winHeight))
pygame.display.set_caption("Dynamic Pathfinding Agent")

fontSmall = pygame.font.SysFont('Arial', 14)
themes = {
    "Light": {"bg": (255, 255, 255), "vis": (180, 160, 255), "front": (255, 255, 0), "path": (0, 255, 0), "wall": (0, 0, 0)},
    "Dark":  {"bg": (50, 50, 50),    "vis": (0, 0, 0),       "front": (255, 165, 0), "path": (0, 255, 255), "wall": (255, 255, 255)},
}
colorWall, colorStart, colorGoal = (100, 108, 128), (0, 0, 255), (128, 0, 128)    

class Node:
    def __init__(self, row, col, width):
        self.row, self.col = row, col
        self.x, self.y = sidebarWidth + (col * width), row * width
        self.width = width
        self.isWall = self.isStart = self.isGoal = False
        self.isVisited = self.isFrontier = self.isPath = False
        self.neighbors = [] 

    def draw(self, window, currTheme):
        themeDict = themes[currTheme]
        color = themeDict["bg"]
        if self.isWall: color = colorWall
        elif self.isStart: color = colorStart
        elif self.isGoal: color = colorGoal
        elif self.isPath: color = themeDict["path"]
        elif self.isVisited: color = themeDict["vis"]
        elif self.isFrontier: color = themeDict["front"]

        rect = pygame.Rect(self.x, self.y, self.width, self.width)
        pygame.draw.rect(window, color, rect)
        pygame.draw.rect(window, (150, 150, 150), rect, 1)

    def getNeighbors(self, grid, totalRows, totalCols):
        self.neighbors = []
        if self.row < totalRows - 1 and not grid[self.row + 1][self.col].isWall: self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].isWall: self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < totalCols - 1 and not grid[self.row][self.col + 1].isWall: self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].isWall: self.neighbors.append(grid[self.row][self.col - 1])

def makeGrid(rows, cols): return [[Node(i, j, min((winWidth - sidebarWidth) // cols, winHeight // rows)) for j in range(cols)] for i in range(rows)]

def calcHeuristic(node1, node2, heurType):
    x1, y1, x2, y2 = node1.row, node1.col, node2.row, node2.col
    if heurType == "Manhattan": return abs(x1 - x2) + abs(y1 - y2)
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def clearVisuals(grid):
    for r in grid:
        for node in r: node.isVisited = node.isFrontier = node.isPath = False

def reconstructPath(cameFrom, current, drawFunc):
    path = []
    while current in cameFrom:
        path.append(current)
        current = cameFrom[current]
        if not current.isStart: current.isPath = True
        drawFunc()
    return path

def runAlgorithm(drawFunc, grid, startNode, goalNode, algoType, heurType, delay, rows, cols):
    clearVisuals(grid)
    for r in grid:
        for node in r: node.getNeighbors(grid, rows, cols)
            
    count = 0
    openSet = []
    heapq.heappush(openSet, (0, count, startNode)) 
    cameFrom = {}
    gScore = {node: float("inf") for r in grid for node in r}
    gScore[startNode] = 0
    fScore = {node: float("inf") for r in grid for node in r}
    fScore[startNode] = calcHeuristic(startNode, goalNode, heurType)
    openSetHash = {startNode} 
    
    while openSet:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return []
                
        current = heapq.heappop(openSet)[2]
        openSetHash.remove(current)
        if current == goalNode: return reconstructPath(cameFrom, goalNode, drawFunc)
            
        for neighbor in current.neighbors:
            tempGScore = gScore[current] + 1
            if tempGScore < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tempGScore
                fScore[neighbor] = tempGScore + calcHeuristic(neighbor, goalNode, heurType) if algoType == "A*" else calcHeuristic(neighbor, goalNode, heurType)
                if neighbor not in openSetHash:
                    count += 1
                    heapq.heappush(openSet, (fScore[neighbor], count, neighbor))
                    openSetHash.add(neighbor)
                    neighbor.isFrontier = True
        drawFunc()
        if current != startNode: current.isVisited = True; current.isFrontier = False
    return []

def main():
    cols, rows, speed, currAlgo, currHeur = 12, 12, 20, "A*", "Manhattan"
    grid = makeGrid(rows, cols)
    startNode = goalNode = None
    running = True

    def drawAll():
        window.fill((230, 230, 230)) 
        btnRun = pygame.Rect(40, 590, 220, 35)
        pygame.draw.rect(window, (180, 180, 180), btnRun)
        window.blit(fontSmall.render("START ALGORITHM", True, (0, 0, 0)), (45, 595))
        for r in grid:
            for n in r: n.draw(window, "Light")
        pygame.display.update()
        return {"run": btnRun}

    while running:
        buttons = drawAll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if pygame.mouse.get_pressed()[0] and buttons["run"].collidepoint(pygame.mouse.get_pos()):
                if startNode and goalNode: runAlgorithm(lambda: drawAll(), grid, startNode, goalNode, currAlgo, currHeur, speed, rows, cols)
    pygame.quit()

if __name__ == "__main__":
    main()
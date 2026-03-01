import pygame
import math
import random

pygame.init()
winWidth, winHeight = 1000, 700 
sidebarWidth = 300
window = pygame.display.set_mode((winWidth, winHeight))
pygame.display.set_caption("Dynamic Pathfinding Agent")

fontSmall = pygame.font.SysFont('Arial', 14)
fontMed = pygame.font.SysFont('Arial', 18, bold=True)

themes = {"Light": {"bg": (255, 255, 255), "vis": (180, 160, 255), "front": (255, 255, 0), "path": (0, 255, 0), "wall": (0, 0, 0)}}
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
        color = themes[currTheme]["bg"]
        if self.isWall: color = colorWall
        elif self.isStart: color = colorStart
        elif self.isGoal: color = colorGoal
        rect = pygame.Rect(self.x, self.y, self.width, self.width)
        pygame.draw.rect(window, color, rect)
        pygame.draw.rect(window, (150, 150, 150), rect, 1)

def makeGrid(rows, cols):
    grid = []
    cellWidth = min((winWidth - sidebarWidth) // cols, winHeight // rows)
    for i in range(rows):
        grid.append([Node(i, j, cellWidth) for j in range(cols)])
    return grid

def drawButton(window, x, y, w, h, text, isActive):
    color = (100, 255, 100) if isActive else (180, 180, 180)
    btnRect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(window, color, btnRect)
    pygame.draw.rect(window, (0, 0, 0), btnRect, 2)
    window.blit(fontSmall.render(text, True, (0, 0, 0)), (x + 5, y + 2))
    return btnRect

def checkReachability(grid, startNode, goalNode, rows, cols):
    queue, visited = [startNode], {startNode}
    while queue:
        curr = queue.pop(0)
        if curr == goalNode: return True
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = curr.row + dr, curr.col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = grid[nr][nc]
                if not neighbor.isWall and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return False

def generateRandomMaze(grid, rows, cols, density):
    for r in grid:
        for node in r: node.isWall = node.isStart = node.isGoal = False
    startNode = grid[random.randint(0, rows//3)][random.randint(0, cols//3)]
    goalNode = grid[random.randint(rows - rows//3 - 1, rows-1)][random.randint(cols - cols//3 - 1, cols-1)]
    startNode.isStart, goalNode.isGoal = True, True

    targetWalls = int((rows * cols - 2) * density)
    wallsPlaced, attempts = 0, 0
    while wallsPlaced < targetWalls and attempts < targetWalls * 5:
        node = grid[random.randint(0, rows-1)][random.randint(0, cols-1)]
        if not node.isStart and not node.isGoal and not node.isWall:
            node.isWall = True
            if checkReachability(grid, startNode, goalNode, rows, cols): wallsPlaced += 1
            else: node.isWall = False 
        attempts += 1
    return startNode, goalNode

def main():
    cols, rows, mazeDensity = 12, 12, 0.3
    currTool = "wall" 
    grid = makeGrid(rows, cols)
    startNode = goalNode = None
    running = True

    def drawAll():
        window.fill((230, 230, 230)) 
        btnStart = drawButton(window, 10, 130, 130, 20, "Set Start (S)", currTool == "start")
        btnGoal = drawButton(window, 150, 130, 130, 20, "Set Goal (G)", currTool == "goal")
        btnWall = drawButton(window, 10, 155, 130, 20, "Draw Wall", currTool == "wall")
        btnErase = drawButton(window, 150, 155, 130, 20, "Erase", currTool == "erase")
        btnRandom = drawButton(window, 40, 530, 220, 25, "  GENERATE RANDOM MAZE", False)
        
        for r in grid:
            for n in r: n.draw(window, "Light")
        pygame.display.update()
        return {"start": btnStart, "goal": btnGoal, "wall": btnWall, "erase": btnErase, "random": btnRandom}

    while running:
        buttons = drawAll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if pygame.mouse.get_pressed()[0]: 
                x, y = pygame.mouse.get_pos()
                if x < sidebarWidth:
                    if buttons["start"].collidepoint(x, y): currTool = "start"
                    elif buttons["wall"].collidepoint(x, y): currTool = "wall"
                    elif buttons["random"].collidepoint(x, y): startNode, goalNode = generateRandomMaze(grid, rows, cols, mazeDensity)
                else:
                    cellW = grid[0][0].width
                    r, c = y // cellW, (x - sidebarWidth) // cellW
                    if r < rows and c < cols:
                        if currTool == "wall": grid[r][c].isWall = True
    pygame.quit()

if __name__ == "__main__":
    main()
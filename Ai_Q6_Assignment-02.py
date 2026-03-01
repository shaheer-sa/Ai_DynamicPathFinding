import pygame
import math

pygame.init()
winWidth, winHeight = 1000, 700 
sidebarWidth = 300
window = pygame.display.set_mode((winWidth, winHeight))
pygame.display.set_caption("Dynamic Pathfinding Agent")

fontSmall = pygame.font.SysFont('Arial', 14)
fontMed = pygame.font.SysFont('Arial', 18, bold=True)

themes = {
    "Light": {"bg": (255, 255, 255), "vis": (180, 160, 255), "front": (255, 255, 0), "path": (0, 255, 0), "wall": (0, 0, 0)}
}
colorWall = (100, 108, 128)  
colorStart = (0, 0, 255)     
colorGoal = (128, 0, 128)    

class Node:
    def __init__(self, row, col, width):
        self.row, self.col = row, col
        self.x = sidebarWidth + (col * width) 
        self.y = row * width
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
        grid.append([])
        for j in range(cols):
            grid[i].append(Node(i, j, cellWidth))
    return grid

def drawButton(window, x, y, w, h, text, isActive):
    color = (100, 255, 100) if isActive else (180, 180, 180)
    btnRect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(window, color, btnRect)
    pygame.draw.rect(window, (0, 0, 0), btnRect, 2)
    window.blit(fontSmall.render(text, True, (0, 0, 0)), (x + 5, y + 2))
    return btnRect

def main():
    cols, rows = 12, 12 
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
        
        for r in grid:
            for node in r:
                node.draw(window, "Light")
        pygame.display.update()
        return {"start": btnStart, "goal": btnGoal, "wall": btnWall, "erase": btnErase}

    while running:
        buttons = drawAll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.mouse.get_pressed()[0]: 
                x, y = pygame.mouse.get_pos()
                if x < sidebarWidth:
                    if buttons["start"].collidepoint(x, y): currTool = "start"
                    elif buttons["goal"].collidepoint(x, y): currTool = "goal"
                    elif buttons["wall"].collidepoint(x, y): currTool = "wall"
                    elif buttons["erase"].collidepoint(x, y): currTool = "erase"
                else:
                    cellW = grid[0][0].width
                    r, c = y // cellW, (x - sidebarWidth) // cellW
                    if r < rows and c < cols:
                        node = grid[r][c]
                        if currTool == "wall": node.isWall = True
                        elif currTool == "erase": node.isWall = False
    pygame.quit()

if __name__ == "__main__":
    main()
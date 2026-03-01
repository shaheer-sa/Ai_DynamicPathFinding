# Dynamic Pathfinding Agent

**Author:** Shaheer Ahmad (24F-0538)  
**Institution:** FAST NUCES  

## Overview
The **Dynamic Pathfinding Agent** is an interactive visualization tool built with Python and Pygame. It demonstrates how artificial intelligence agents navigate complex environments using classic search algorithms. This project not only visualizes static pathfinding but also features a **Dynamic Mode** where the environment changes in real-time, forcing the agent to detect sudden obstacles and instantly recalculate its route.

## Features
* **Algorithms:** A* (A-Star) Search and Greedy Best-First Search (GBFS).
* **Heuristics:** Toggle between Manhattan and Euclidean distance metrics.
* **Random Maze Generator:** Instantly generate solvable, winding mazes based on a user-defined obstacle density (ranging from 0% to 50%).
* **Dynamic Obstacles:** When enabled, sudden obstacles have a chance to spawn directly on the agent's path while it is in transit. The agent will halt, evaluate the blockage, and autonomously recalculate a new path from its current position without losing its walked history.
* **Real-Time Metrics Dashboard:** Tracks and displays:
  * **Nodes Visited:** Total count of expanded nodes during the search.
  * **Path Cost:** The exact length of the final calculated path.
  * **Execution Time:** Pure computational time taken to solve the grid (measured precisely in milliseconds).

## Prerequisites
To run this project, you will need **Python 3.x** installed on your system along with the `pygame` library.

Install the required dependency using pip:
```bash
pip install pygame
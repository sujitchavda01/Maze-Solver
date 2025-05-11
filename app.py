from flask import Flask, render_template, request, jsonify
import numpy as np
import random

app = Flask(__name__)

rows, cols = 21, 21
G = np.full((rows, cols), '#', dtype=str)


def generate_maze():
    global G
    G[:] = '#'
    stack = [(1, 1)]
    G[1, 1] = '-'
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < rows - 1 and 1 <= ny < cols - 1 and G[nx, ny] == '#':
                G[nx - dx // 2, ny - dy // 2] = '-'
                G[nx, ny] = '-'
                stack.append((nx, ny))
                break
        else:
            stack.pop()

    G[1, 0] = '-'
    G[rows - 2, cols - 1] = '-'


def flood_fill_correct_path():
    start_x, start_y = 1, 0
    end_x, end_y = rows - 2, cols - 1
    old_color, correct_color = '-', 'R'

    queue = [(start_x, start_y)]
    parent = {}
    visited = set()
    visited.add((start_x, start_y))

    while queue:
        x, y = queue.pop(0)
        if (x, y) == (end_x, end_y):
            break

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and G[nx, ny] == old_color and (nx, ny) not in visited:
                queue.append((nx, ny))
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)

    path = []
    current = (end_x, end_y)
    while current in parent:
        path.append(current)
        current = parent[current]
    path.append((start_x, start_y))

    for px, py in path:
        G[px, py] = correct_color  # Mark the correct path in red

    return {'correct_path': path[::-1]}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_maze")
def get_maze():
    return jsonify(maze=G.tolist())


@app.route("/toggle_cell", methods=["POST"])
def toggle_cell():
    data = request.json
    i, j = data["i"], data["j"]
    if 0 <= i < rows and 0 <= j < cols:
        G[i, j] = '#' if G[i, j] == '-' else '-'
    return jsonify(success=True)


@app.route("/solve_maze", methods=["POST"])
def solve_maze():
    result = flood_fill_correct_path()
    return jsonify(result)


@app.route("/reset_maze", methods=["POST"])
def reset_maze():
    generate_maze()
    return jsonify(maze=G.tolist())


if __name__ == "__main__":
    generate_maze()
    app.run(debug=True)

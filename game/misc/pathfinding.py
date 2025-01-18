
import pyasge

import game.gameobjects.iceblock
from game.gamedata import GameData

def heuristic(coord_a: pyasge.Point2D, coord_b: pyasge.Point2D):
    # Calculates the rough distance between the two points
    return abs(coord_a.x - coord_b.x) + abs(coord_a.y - coord_b.y)

class PathNode:
    def __init__(self, coord, parent, cost, goal_coord: pyasge.Point2D):
        # Every node stores info on where they are right now, and the previous coordinate they moved from
        self.coord = coord
        self.parent = parent

        self.cost = cost
        self.distance = heuristic(coord, goal_coord)

class Pathfinding:
    def __init__(self, gamedata: GameData, layer, obstacles: list):
        self.data = gamedata
        self.path = []
        self.layer = layer
        self.obstacles = obstacles

    def find_path(self, start_coord: pyasge.Point2D, end_coord:  pyasge.Point2D):
        self.path = []

        open = [PathNode(start_coord, start_coord, 1, end_coord)]
        closed = []

        end_found = False

        while open:
            current_node = open.pop(0)
            closed.append(current_node)

            # Check if we have found our end destination
            if current_node.coord == end_coord:
                end_found = True
                break

            # If not, start checking all the neighbouring tiles
            neighbours = self.get_neighbours(current_node, end_coord)
            for neighbour in neighbours:
                if not self.check_list(closed, neighbour.coord):
                    current_cost = current_node.cost + 1
                    current_distance = heuristic(current_node.coord, end_coord)

                    if not self.check_list(open, neighbour.coord) \
                            or current_cost < neighbour.cost \
                            or current_distance < neighbour.distance:
                        neighbour.cost = current_cost
                        neighbour.parent = current_node
                        open.append(PathNode(neighbour.coord, current_node.coord, 1, end_coord))

        if end_found:
            self.retrace_path(closed, current_node)
        else:
            print("Path not found!")

        pass

    def check_list(self, array, target):
        return next((x for x in array if x.coord == target), None) is not None

    # Find all neighbouring/adjacent tiles for the currently-selected tile
    def get_neighbours(self, node: PathNode, end_coord:  pyasge.Point2D):
        neighbours = [
            PathNode(pyasge.Point2D(node.coord.x + 1, node.coord.y), node, 1, end_coord),
            PathNode(pyasge.Point2D(node.coord.x, node.coord.y + 1), node, 1, end_coord),
            PathNode(pyasge.Point2D(node.coord.x - 1, node.coord.y), node, 1, end_coord),
            PathNode(pyasge.Point2D(node.coord.x, node.coord.y - 1), node, 1, end_coord)
        ]

        neighbour_distances = [
            heuristic(neighbours[0].coord, end_coord),
            heuristic(neighbours[1].coord, end_coord),
            heuristic(neighbours[2].coord, end_coord),
            heuristic(neighbours[3].coord, end_coord)]

        for i in range(4):

            # Check for walls or out-of-bounds areas
            if neighbours[i].coord.x < 0 or neighbours[i].coord.y < 0:
                neighbours[i] = node
            elif neighbours[i].coord.x > self.data.game_res[0] or neighbours[i].coord.y > self.data.game_res[1]:
                neighbours[i] = node
            elif self.data.game_map.is_valid_tile(self.layer, [neighbours[i].coord.x + 0.1, neighbours[i].coord.y + 0.1]) is True:
                neighbours[i] = node

            # Check for obstacles that might not be tiles
            else:
                for obstacle in self.obstacles:
                    if obstacle == game.gameobjects.iceblock.IceBlock:
                        obstacle_pos = self.data.game_map.tile(pyasge.Point2D(obstacle.sprite.x, obstacle.sprite.y))
                        neighbour_tile = self.data.game_map.tile(pyasge.Point2D(neighbours[i].coord.x, neighbours[i].coord.y))

                        if obstacle_pos == neighbour_tile:
                            neighbours[i] = node

        while neighbours.__contains__(node):
            neighbours.remove(node)

        return neighbours

    # Traverse the path backwards if end point has been reached
    def retrace_path(self, closed, end_node: PathNode):
        current_node = end_node

        while current_node.coord is not current_node.parent:
            self.path.append(current_node.coord)
            current_node = next(x for x in closed if x.coord == current_node.parent)

        self.path.append(current_node.coord)
        self.path.reverse()
        pass

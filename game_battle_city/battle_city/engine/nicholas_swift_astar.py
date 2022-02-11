# Credit for this: Nicholas Swift
# as found at https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
from warnings import warn
import heapq
import time

class Node:

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position
    
    def __repr__(self):
      return str(self.position)+" "+str(self.g)+" "+str(self.h)+" "+str(self.f)

    # defining less than for purposes of heap queue
    def __lt__(self, other):
      return self.f < other.f
    
    # defining greater than for purposes of heap queue
    def __gt__(self, other):
      return self.f > other.f

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
        
    return path[::-1]  # Return reversed path

class DebugInfo:
    def __init__(self):
        self.min_x=999
        self.min_y=999
        self.max_x=0
        self.max_y=0

def astar(maze, start, end, exclude_points, ignore_flags):
    #print("astar:",start, end, exclude_points)
    start_time=time.time()
    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    #test_list=[]

    # Heapify the open_list and Add the start node
    heapq.heapify(open_list) 
    heapq.heappush(open_list, start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = (len(maze[0]) * len(maze))

    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
    
    # Loop until you find the end
    while len(open_list) > 0:

        #if dbg_str=="tank00_1":
        #    print("!!!>>>",dbg_str,outer_iterations,len(open_list))

        outer_iterations += 1

        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        '''if outer_iterations > max_iterations:
            # if we hit this point return the path such as it is
            # it will not contain the destination
            warn("giving up on pathfinding too many iterations")
            return None#return_path(current_node)'''

        # Found the goal
        if current_node == end_node:
            #print "Ok:",current_node,"==",end_node,total_iterations_a,total_iterations_b,total_iterations_c
            #print("Ok:",outer_iterations)
            return return_path(current_node)

        # Generate children
        children = []
        
        for offset_position in adjacent_squares: # Adjacent squares            
            # Get node position
            node_position = (current_node.position[0] + offset_position[0], current_node.position[1] + offset_position[1])

            # Make sure within range
            if node_position[0] > (len(maze[0]) - 1) or node_position[0] < 0 or node_position[1] > (len(maze) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[1]][node_position[0]] > 0 and not maze[node_position[1]][node_position[0]] in ignore_flags:
                continue

            if node_position==start:
                #print("exclude point:",node_position)
                continue

            if node_position != end and node_position in exclude_points:
                #print("exclude:",node_position)
                continue

            #if time.time()-start_time>3.0 and dbg_str=="tank00_1":
            #    print("___>>>",dbg_str,current_node.position,node_position)
            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)
            #test_list.append(node_position)

        # Loop through children
        for child in children:
            # Child is on the closed list
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            #if child.f>max_iterations:
            #    return (False,closed_list)

            # Child is already in the open list
            #if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
            #    continue
            child_is_already_in_the_open_list=False
            for open_node in open_list:
                #if dbg_str=="tank00_1":
                    #print(child.position, "==",open_node.position)
                if child.position == open_node.position:# and child.g > open_node.g:
                    child_is_already_in_the_open_list=True
                    break

            if child_is_already_in_the_open_list:
                continue

            # Add the child to the open list
            #if dbg_str=="tank00_1":
                #print("___>>>",dbg_str,current_node.position,child.position)
            heapq.heappush(open_list, child)

    #warn("Couldn't get a path to destination")
    #print("Not found:",outer_iterations,len(open_list),len(closed_list))
    #ret_debug.append({"closed_list":closed_list})
    return None
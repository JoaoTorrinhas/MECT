from collections import defaultdict

class Graph():
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.weights has all the weights between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.edges = defaultdict(list)
        self.weights = {}
    
    def add_edge(self, from_node, to_node, weight):
        # Note: assumes edges are bi-directional
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.weights[(from_node, to_node)] = weight
        self.weights[(to_node, from_node)] = weight
        
#Esta função vai para o mainRob3        
# def dijsktra(graph, initial, end):
#     # shortest paths is a dict of nodes
#     # whose value is a tuple of (previous node, weight)
#     shortest_paths = {initial: (None, 0)}
#     current_node = initial
#     visited = set()
    
#     while current_node != end:
#         visited.add(current_node)
#         destinations = graph.edges[current_node]
#         weight_to_current_node = shortest_paths[current_node][1]

#         for next_node in destinations:
#             weight = graph.weights[(current_node, next_node)] + weight_to_current_node
#             if next_node not in shortest_paths:
#                 shortest_paths[next_node] = (current_node, weight)
#             else:
#                 current_shortest_weight = shortest_paths[next_node][1]
#                 if current_shortest_weight > weight:
#                     shortest_paths[next_node] = (current_node, weight)
        
#         next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
#         if not next_destinations:
#             return "Route Not Possible"
#         # next node is the destination with the lowest weight
#         current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
    
#     # Work back through destinations in shortest path
#     path = []
#     while current_node is not None:
#         path.append(current_node)
#         next_node = shortest_paths[current_node][0]
#         current_node = next_node
#     # Reverse path
#     path = path[::-1]
#     return path

# edges = [
#     ('X', 'A', 7),
#     ('X', 'B', 2),
#     ('X', 'C', 3),
#     ('X', 'E', 4),
#     ('A', 'B', 3),
#     ('A', 'D', 4),
#     ('B', 'D', 4),
#     ('B', 'H', 5),
#     ('C', 'L', 2),
#     ('D', 'F', 1),
#     ('F', 'H', 3),
#     ('G', 'H', 2),
#     ('G', 'Y', 2),
#     ('I', 'J', 6),
#     ('I', 'K', 4),
#     ('I', 'L', 4),
#     ('J', 'L', 1),
#     ('K', 'Y', 5),
# ]
# graph = Graph()

# for edge in edges:
#     graph.add_edge(*edge)
    
# print(dijsktra(graph, 'X', 'Y'))

# edges = [('1', '13', 4), ('2', '1', 2), ('3', '2', 2), ('4', '3', 4), ('5', '4', 8), ('6', '5', 2), ('7', '6', 6), ('8', '7', 2), ('9', '8', 16), ('10', '9', 26), ('11', '10', 20), ('12', '11', 6), ('13', '12', 2), ('3', '2', 6), ('14', '4', 4), ('5', '14', 4), ('7', '6', 2), ('9', '7', 6), ('12', '11', 2), ('14', '13', 12)]
# edges = [('1', '13', 4), ('2', '1', 2), ('3', '2', 2), ('2', '3', 6), ('4', '3', 4), ('5', '4', 8), ('6', '5', 2), ('7', '6', 6), ('8', '7', 2), ('9', '8', 16), ('10', '9', 26), ('11', '10', 20), ('12', '11', 6), ('13', '12', 2), ('14', '4', 4), ('5', '14', 4), ('7', '6', 2), ('9', '7', 6), ('12', '11', 2), ('14', '13', 12)]

# graph = Graph()
# for edge in edges:
#     graph.add_edge(*edge)
    
# print(dijsktra(graph, '1', '8'))
# print(dijsktra(graph, '8', '10'))
# print(dijsktra(graph, '10', '1'))



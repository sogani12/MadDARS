# # Package developed by Colin Dewey for COMP SCI 576

class DirectedGraph:
    """Abstract base class for a directed graph.

    A functional directed graph class can be obtained by inheriting from 
    this class and overriding the methods has_edge and add_edge.  All other
    methods have default implementations, which may not be the most efficient.
    These other methods should also be overriden as appropriate to improve
    efficiency.
    """
    def __init__(self, num_vertices):
        """Constructs a directed graph with num_vertices vertices and zero edges"""
        self._num_vertices = num_vertices
    
    def has_edge(self, i, j):
        """Returns True if the graph contains the directed edge (i, j), False otherwise."""
        raise NotImplementedError
        
    def add_edge(self, i, j):
        """Adds the directed edge (i, j) to the graph."""
        raise NotImplementedError
        
    def out_edges(self, i):
        """Returns a list of directed edges outgoing from vertex i."""
        return [(i, j) for j in range(self._num_vertices) if self.has_edge(i, j)]
    
    def in_edges(self, j):
        """Returns a list of directed edges incoming to vertex j."""
        return [(i, j) for i in range(self._num_vertices) if self.has_edge(i, j)]

    def parents(self, j):
        """Returns a list of the vertices that are parents of vertex j."""
        return [i for i in range(self._num_vertices) if self.has_edge(i, j)]
    
    def children(self, i):
        """Returns a list of the vertices that are children of vertex i."""
        return [j for j in range(self._num_vertices) if self.has_edge(i, j)]
    
    def outdegree(self, i):
        """Returns the outdegree of vertex i."""
        return len(self.out_edges(i))
    
    def indegree(self, i):
        """Returns the indegree of vertex i."""
        return len(self.in_edges(i))
    
    def degree(self, i):
        """Returns the degree of vertex i."""
        return self.indegree(i) + self.outdegree(i)
        
    def add_edges(self, edges):
        """Adds all edges from a list to the graph."""
        for i, j in edges:
            self.add_edge(i, j)
            
    def num_vertices(self):
        """Returns the number of vertices in the graph."""
        return self._num_vertices

    def num_edges(self):
        """Returns the number of edges in the graph."""
        return len(tuple(self.edges()))
    
    def edges(self):
        """Returns an iterator over the edges of the graph."""
        for i in range(self._num_vertices):
            for edge in self.out_edges(i):
                yield edge
    
    def reorder(self, order):
        """Reorders the vertices of the graph
        
        Args:
            order: a list of the (old) vertex indices in the new order
        """
        raise NotImplementedError
        
    def add_vertex(self):
        """Adds a new vertex to the graph and returns its index."""
        self._num_vertices += 1
        return self._num_vertices - 1

    def topological_order(self):
        """Returns a list of vertex indices in a topological order."""
        order = []
        visited = [False] * self.num_vertices()
        visiting = [False] * self.num_vertices()
        
        def visit(i):
            if visited[i]: return
            if visiting[i]: raise Exception("Graph is not a DAG")
            visiting[i] = True
            for j in self.children(i):
                visit(j)
            visited[i] = True
            order.append(i)
        
        for i in range(self.num_vertices()):
            if not visited[i]:
                visit(i)
        return list(reversed(order))
                
    def __str__(self):
        """Returns a string representation of the graph, so that it may be printed."""
        return "DirectedGraph with %d vertices and %d edge(s):\n%s" % (self.num_vertices(),
                                                                       self.num_edges(),
                                                                       sorted(self.edges()))

class AdjacencyListDirectedGraph(DirectedGraph):
    """An implementation of a Directed Graph that uses adjacency lists to store edges."""
        
    def __init__(self, num_vertices):
        super().__init__(num_vertices)
        self._out_lists = [[] for i in range(num_vertices)]
        self._in_lists = [[] for i in range(num_vertices)]
    
    def add_edge(self, i, j):
        self._out_lists[i].append(j)
        self._in_lists[j].append(i)
    
    def has_edge(self, i, j):
        return j in self._out_lists[i]
        
    def out_edges(self, i):
        return [(i, j) for j in self._out_lists[i]]
        
    def in_edges(self, j):
        return [(i, j) for i in self._in_lists[j]]

    def parents(self, j):
        return self._in_lists[j]
    
    def children(self, i):
        return self._out_lists[i]    
    
    def indegree(self, i):
        return len(self._in_lists[i])
        
    def outdegree(self, i):
        return len(self._out_lists[i])
    
    def add_vertex(self):
        self._out_lists.append([])
        self._in_lists.append([])
        return super().add_vertex()
        
    def reorder(self, order):
        index_map = [None] * len(order)
        for new_index, old_index in enumerate(order):
            index_map[old_index] = new_index
        self._out_lists = reordered_list(map_index_lists(self._out_lists, index_map), order)
        self._in_lists = reordered_list(map_index_lists(self._in_lists, index_map), order)

class VertexLabeledDirectedGraph(DirectedGraph):
    """A mixin class that allows for vertices in a directed graph to have labels."""
    
    def __init__(self, num_vertices):
        # call the next constructor in Python's Method Resolution Order
        super().__init__(num_vertices)
        self._vertex_labels = [None] * num_vertices

    def set_vertex_label(self, i, label):
        """Adds a label to vertex i."""
        self._vertex_labels[i] = label
       
    def vertex_label(self, i):
        """Returns the label of vertex i or None if it is not assigned a label"""
        return self._vertex_labels[i]
    
    def add_vertex(self):
        self._vertex_labels.append(None)
        return super().add_vertex()
        
    def reorder(self, order):
        super().reorder(order)
        self._vertex_labels = reordered_list(self._vertex_labels, order)

def reordered_list(lst, order):
    return [lst[i] for i in order]

def map_index_list(lst, index_map):
    return [index_map[index] for index in lst]

def map_index_lists(index_lists, index_map):
    return [map_index_list(lst, index_map) for lst in index_lists]

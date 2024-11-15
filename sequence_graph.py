## Package developed by Colin Dewey for COMP SCI 576

import graph
import toyplot
import numpy
import random

class SequenceGraph(graph.VertexLabeledDirectedGraph, graph.AdjacencyListDirectedGraph):
    """A graph representing multiple possible sequences.
    
    A sequence graph is a directed acylic graph (a directed graph without cycles)
    with each vertex labeled with a single character.  To be valid, its vertices must
    be in topological order.
    """
    
    def is_valid(self):
        """Returns True if this graph is a valid SequenceGraph"""
        return (self.num_vertices() >= 2 and 
                self.is_in_topological_order() and 
                self.is_labeled())
 
    def is_in_topological_order(self):
        """Returns True if the vertices of the graph are in a topological order"""
        return all(all(j < i for j in self.parents(i)) for i in range(self.num_vertices()))
    
    def is_labeled(self):
        """Returns True if all vertices are labeled with a single character,
           with the exception of the start and end vertices, which should not be labeled"""
        return (self.vertex_label(0) is None and 
                self.vertex_label(self.num_vertices() - 1) is None and
                all(self.vertex_label(i) and len(self.vertex_label(i)) >= 1 
                    for i in range(1, self.num_vertices() - 1)))
          
    def topological_string(self):
        """Returns a string of the vertex labels, assuming vertices are in topological order."""
        assert self.is_in_topological_order()
        return ''.join(self.vertex_label(i) for i in range(1, self.num_vertices() - 1))

    def max_vertex_depth(self):
        """Returns the max depth of each vertex as a list.
        
        Assumes vertices are in topological order."""
        depth = [0] * self.num_vertices()
        for i in range(1, self.num_vertices()):
            depth[i] = max(depth[k] + 1 for k in self.parents(i))

        return depth             
        
    def plot(self, curved_edges = False):
        """Plots the graph."""
        edges = numpy.array(list(self.edges()))
        singletons = [i for i in range(self.num_vertices()) if self.degree(i) == 0]
        labels = [self.vertex_label(i) if self.vertex_label(i) else "" for i in range(self.num_vertices())]
        
        depth = self.max_vertex_depth()
        
        ycoords = [None] * self.num_vertices()
        
        depth_counts = [0] * (max(depth) + 1)
        for i, d in enumerate(depth):
            ycoords[i] = depth_counts[d]
            depth_counts[d] += 1
            
        for i in range(self.num_vertices()):
            ycoords[i] -= (depth_counts[depth[i]] / 2)

        vcoordinates = numpy.ma.masked_all((self.num_vertices(), 2))
        vcoordinates[:,0] = depth
        vcoordinates[:,1] = ycoords
        
        if curved_edges:
            layout = toyplot.layout.IgnoreVertices(edges=toyplot.layout.CurvedEdges(curvature=0.5))
        else:
            layout = toyplot.layout.IgnoreVertices()

        canvas, axes, mark = toyplot.graph(
            edges,
            singletons,
            ecolor="black",
            tmarker=">",
            vcolor="white",
            vmarker="o",
            vlabel=labels,
            layout=layout,
            vsize=40,
            height=100 + (40 * max(depth_counts) * 2),
            width=100 + (40 * max(depth) * 2),
            vcoordinates=vcoordinates,
            vstyle={"stroke": "black"})

        # keep vertices from falling outside of the canvas
        axes.padding=50
        

class VariantGraph(SequenceGraph):
    """A SequenceGraph representing variants with respect to a reference sequence.
    
    This class aids in construction of a SequenceGraph given a reference sequence
    and a series of variants that are added one by one.  After all variants have
    been added, the method reorder_topological should be called to make the graph
    a valid SequenceGraph, which can then be used for alignment.
    """
    
    def __init__(self, ref_sequence, reference_id = "R"):
        """Initialize the graph with a reference sequence, ref_sequence.
        
        The origin of each position in the reference sequence will be 
        assigned to the value of reference_id."""
        super().__init__(len(ref_sequence.split(",")) + 2)
        self._ref_sequence = ref_sequence.split(",")
        self._origin = [None] * self.num_vertices()
        
        # set the labels and origins of the reference sequence vertices
        for i, c in enumerate(ref_sequence.split(",")):
            self.set_vertex_label(i + 1, c)
            self._origin[i + 1] = reference_id
            
        # initialize chain of edges through reference vertices
        for i in range(self.num_vertices() - 1):
            self.add_edge(i, i + 1)
            
    def add_vertex(self):
        """Add a vertex to the graph"""
        self._origin.append(None)
        return super().add_vertex()
    
    def reorder(self, order):
        """Reorder the vertices according to order (a list of vertex indices)"""
        super().reorder(order)
        self._origin = graph.reordered_list(self._origin, order)

    def reorder_topological(self):
        """Reorders the vertices of this graph in a topological order"""
        self.reorder(self.topological_order())
         
    def vertex_origin(self, i):
        """Returns the origin id of vertex i"""
        return self._origin[i]
        
    def add_substitution_variant(self, ref_position, variant_char, variant_id="V"):
        """Add a substitution variant to the graph.
        
        Args:
            ref_position: The 1-based position of the variant in the reference sequence
            variant_char: The mutant character
            variant_id: The origin ID of the variant.
        """
        self.add_complex_variant(ref_position, 1, variant_char, variant_id)
        
    def add_deletion_variant(self, ref_position, deletion_length):
        """Add a deletion variant to the graph.
        
        Args:
            ref_position: The 1-based position of the start of the deletion in the reference sequence
            deletion_length: The number of characters deleted.
        """
        self.add_complex_variant(ref_position, deletion_length, "", variant_id = "V")
        
    def add_insertion_variant(self, ref_position, variant_string, variant_id = "V"):
        """Add an insertion variant to the graph.
        
        Args:
            ref_position: The 1-based position in the reference sequence immediately following the insertion
            variant_string: The inserted sequence.
            variant_id: The origin ID of the variant.
        """
        self.add_complex_variant(ref_position, 0, variant_string, variant_id)
        
    def add_complex_variant(self, ref_position, ref_length, variant_string, variant_id = "V"):
        """Adds a general variant that replaces a substring of the reference with different string.
        
        If the variant is a simple substitution, deletion, or insertion, 
        the more specific methods above should be used.
        
        Args:
            ref_position: The 1-based position in the reference sequence at the start of the reference substring
            ref_length: The length of the reference substring.
            variant_string: The variant string to replace the reference substring.
            variant_id: The origin ID of the variant.
        """       
        assert((0 < ref_position <= len(self._ref_sequence) + 1) and
               (ref_length <= (len(self._ref_sequence) - ref_position + 1)))
        i = ref_position - 1
        for c in variant_string.split(","):
            j = self.add_vertex()
            self.set_vertex_label(j, c)
            self._origin[j] = variant_id
            self.add_edge(i, j)
            i = j
        self.add_edge(i, ref_position + ref_length)
        
def random_sequence_graph(num_chars, alphabet = "ACGT", edge_prob = 0.25):
    """Generates a random SequenceGraph.
    
    Args:
        num_chars: The number of labeled vertices in the graph
        alphabet: A string giving the possible characters for the vertex labels.
        edge_prob: The probability of the presence of an edge between each pair of vertices.
    """
    g = SequenceGraph(num_chars + 2)

    for i in range(g.num_vertices()):
        for j in range(i + 1, g.num_vertices()):
            if random.random() < edge_prob:
                g.add_edge(i, j)
    
    for i in range(1, g.num_vertices() - 1):
        c = random.choice(alphabet)
        g.set_vertex_label(i, c)
        if g.indegree(i) == 0:
            g.add_edge(0, i)
        if g.outdegree(i) == 0:
            g.add_edge(i, g.num_vertices() - 1)
    
    return g
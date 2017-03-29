import sys
import igraph

class DepGraph:
    def __init__(self):
        self.__graph = igraph.Graph(directed=True)
        self.__finalized = False

    def __repr__(self):
        return repr(self.__graph)
        
    def __len__(self):
        return len(self.__graph.vs)

    def __str__(self):
        return str(self.__graph)
    
    def __contains__(self, name):
        if len(self) == 0:
            return False
        return name in self.__graph.vs["name"]
        
    def __get_parents(self, vertex):
        if vertex not in self:
            raise ValueError("The name passed to get_parents does not exist on the graph")
        
        return [self.__graph.vs[vid]["name"] for vid in self.__graph.neighbors(vertex, mode=igraph.IN)]

    def add_dependency(self, from_vertex, to_vertex):
        assert(not self.__finalized)
        if from_vertex not in self or to_vertex not in self:
            raise ValueError("The name passed to add_dependency does not exist on the graph")

        self.__graph.add_edge(from_vertex, to_vertex)

    def add_node(self, name, parent_names):
        assert(not self.__finalized)
        if not isinstance(name, str):
            msg = repr(name) + " does not have type 'str'"
            raise ValueError(msg)

        if name not in self:
            self.__graph.add_vertex(name)
        
        existing_parents = self.__get_parents(name)
        range_of_parents = (parent for parent in parent_names if parent not in existing_parents)
        for parent in range_of_parents:
            if parent == name:
                raise ValueError("Node name must not appear in the parent_names")
            
            if parent not in self:
                self.add_node(parent, [])
                
            self.add_dependency(parent, name)
            
    def finalize(self):
        assert(not self.__finalized)
        if not self.__graph.is_dag():
            raise ValueError("The generated graph is not a DAG!\n" + str(g))

        self.__finalized = True
    
    def is_ready(self):
        return self.__finalized

    def get_parents(self, vertex):
        assert(self.__finalized)
        return self.__get_parents(vertex)
        
    def get_children(self, vertex):
        assert(self.__finalized)
        if vertex not in self:
            raise ValueError("The name passed to get_children does not exist on the graph")
        
        return [self.__graph.vs[vid]["name"] for vid in self.__graph.neighbors(vertex, mode=igraph.OUT)]
        
    def get_num_children(self, vertex):
        assert(self.__finalized)
        if vertex not in self:
            raise ValueError("The name passed to get_children does not exist on the graph")
        
        return len(self.__graph.neighbors(vertex, mode=igraph.OUT))

    def remove_dependency(self, vertex, dependency):
        assert(self.__finalized)
        if vertex not in self or dependency not in self:
            raise ValueError("The vertex and dependency passed to remove_dependency must exist on the graph")
            
        self.__graph.delete_edges([(dependency, vertex)])
        
    def get_topological_ordering(self):
        assert(self.__finalized)
        return [self.__graph.vs[vid]["name"] for vid in self.__graph.topological_sorting(mode=igraph.OUT)]
        
    def plot(self, filename):
        
        def choose_colour(label):
            if label.endswith(".h") or label.endswith(".hpp"):
                return "blue"
            elif label.endswith(".c") or label.endswith(".cpp"):
                return "red"
            elif '.' in label:
                return "black"
            else:
                return "gray"
    
        if not isinstance(filename, str) or not filename.endswith(".png"):
            raise ValueError("Filename must be of type 'str' and must end with '.png'")
    
        # no point
        if len(self) == 0:
            return
    
        layout = self.__graph.layout("fr")
        labels = self.__graph.vs['name']
        
        opts = dict()
        opts["vertex_size"] = 20
        opts["vertex_color"] = [choose_colour(label) for label in labels]
        opts["vertex_label"] = labels
        opts["vertex_shape"] = "circle"
        opts["vertex_label_color"] = "black"
        opts["vertex_label_size"] = 20
        opts["vertex_label_dist"] = 2
        opts["layout"] = layout
        opts["bbox"] = (900, 900)
        opts["margin"] = 50
        opts["target"] = filename
        igraph.plot(self.__graph, **opts)

    def get_raw(self):
        return self.__graph
        

if __name__ == "__main__":
    try:
        g = DepGraph()
        g.add_node('a', [])
        g.add_node('b', ['a'])
        g.add_node('c', ['a'])
        g.add_node('c', ['a'])
        g.add_node('c', ['a'])
        g.add_node('c', ['a'])
        g.add_node('d', ['b', 'c'])
        g.finalize()
        print(g)
        print(g.is_ready())
        print(g.get_topological_ordering())
        
        g = DepGraph()
        g.add_node('containers.h', ['array', 'vector', 'iostream', 'io.h'])
        g.add_node('io.h', ['iostream', 'fstream'])
        g.add_node('main.cpp', ['containers.h', 'io.h', 'fstream'])
        g.finalize()
        print(g)
        print(g.is_ready())
        print(g.get_topological_ordering())
    except Exception as e:
        print(repr(e))
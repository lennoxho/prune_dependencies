import sys
import networkx as nx

class DepGraph:
    def __init__(self):
        self.__graph = nx.DiGraph()
        self.__finalized = False

    def __repr__(self):
        return repr(self.__graph)
        
    def __len__(self):
        return len(self.__graph)

    def __str__(self):
        return str(self.__graph.edges())
    
    def __contains__(self, name):
        return name in self.__graph
        
    def __get_parents(self, name):
        if name not in self:
            raise ValueError("The name passed to get_parents does not exist on the graph")
        
        return self.__graph.predecessors(name)

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
            self.__graph.add_node(name)
        
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
        if not nx.is_directed_acyclic_graph(self.__graph):
            raise ValueError("The generated graph is not a DAG!\n" + str(g))

        self.__finalized = True
    
    def is_ready(self):
        return self.__finalized

    def get_parents(self, name):
        assert(self.__finalized)
        return self.__get_parents(name)
        
    def get_children(self, name):
        assert(self.__finalized)
        if name not in self:
            raise ValueError("The name passed to get_children does not exist on the graph")
        
        return self.__graph.successors(name)
        
    def get_num_children(self, name):
        assert(self.__finalized)        
        return len(self.get_children(name))

    def remove_dependency(self, name, dependency):
        assert(self.__finalized)
        if not self.__graph.has_edge(dependency, name):
            raise ValueError("The name and dependency passed to remove_dependency must exist on the graph")
            
        self.__graph.remove_edge(dependency, name)
        
    def get_topological_ordering(self):
        assert(self.__finalized)
        return nx.topological_sort(self.__graph)
        
    def plot(self, filename):
        pass

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
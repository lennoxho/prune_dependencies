from DepGraph import *

def get_parent_dependencies_and_decrement(graph, map_of_dependencies, node):
    parents = graph.get_parents(node)
    
    dependencies = set()
    for parent in parents:
        assert(parent in map_of_dependencies)
        parent_entry = map_of_dependencies[parent]
        
        assert(parent_entry[2] > 0)
        parent_entry[2] -= 1
        
        dependencies = dependencies.union(parent_entry[0].union(parent_entry[1]))
        
        if parent_entry[2] == 0:
            parent_entry[0] = None
        
    return [set(parents), dependencies]
    
def get_unnecessary_dependencies(graph):
    map_of_dependencies = dict()
    topological_ordering = graph.get_topological_ordering()
    
    for node in topological_ordering:
        parents, parent_dependencies = get_parent_dependencies_and_decrement(graph, map_of_dependencies, node)

        # O(len(parents))
        current_node_necessary_dependencies = parents - parent_dependencies
        current_node_unnecessary_dependencies = parents - current_node_necessary_dependencies

        map_of_dependencies[node] = [parent_dependencies | parents,
                                     current_node_unnecessary_dependencies,
                                     graph.get_num_children(node)]

    # sanity check
    for node in map_of_dependencies:
        assert(map_of_dependencies[node][2] == 0)
                                     
    return map_of_dependencies

if __name__ == "__main__":
    g = DepGraph()
    g.add_node('containers.h', ['array', 'vector', 'iostream', 'io.h'])
    g.add_node('io.h', ['iostream', 'fstream'])
    g.add_node('main.cpp', ['containers.h', 'io.h', 'fstream'])
    g.finalize()
    
    g.plot("before.png")
    
    unnecessary_dependencies = get_unnecessary_dependencies(g)
    for node in unnecessary_dependencies:
        deps = unnecessary_dependencies[node][1]
        print(node + " -> " + str(deps))
        
        for unnecessary_dep in deps:
            g.remove_dependency(node, unnecessary_dep)

    g.plot("after.png")
from NetworkxDepGraph import *
from SimpleIncludeParser import *

def get_includes(file_list, args):
    include_parser = IncludeParser(strict=False)
    
    include_dict = dict()
    for file in file_list:
        include_dict[os.path.basename(file)] = include_parser.get_includes(file, [], args)
        
    return include_dict
    
def assemble_graph(include_dict):
    g = DepGraph()
    
    for file in include_dict:
        g.add_node(file, include_dict[file])

    g.finalize()
    return g

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

def get_file_list(filename):
    file_list = []

    hfile = open(filename)
    for line in hfile:
        line = line.strip()
        if line != "":
            file_list.append(line)
            
    return file_list
    
if __name__ == "__main__":
    file_list = get_file_list("file_list.conf")

    include_dict = get_includes(file_list, [])
    g = assemble_graph(include_dict)
    
    g.plot("before.png")
    
    unnecessary_dependencies = get_unnecessary_dependencies(g)
    for node in unnecessary_dependencies:
        deps = unnecessary_dependencies[node][1]
        print(node + " -> " + str(deps))
        
        for unnecessary_dep in deps:
            g.remove_dependency(node, unnecessary_dep)

    g.plot("after.png")
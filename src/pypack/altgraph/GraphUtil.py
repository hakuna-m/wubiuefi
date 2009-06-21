'''
Utility classes and functions
'''

from altgraph.compat import *
from altgraph import Graph
import random

def generate_random_graph(node_num, edge_num, self_loops=False, multi_edges=False):
    '''
    Generates and returns a L{Graph.Graph} instance with C{node_num} nodes
    randomly connected by C{edge_num} edges.
    '''
    g = Graph.Graph()
    nodes = range(node_num)

    for node in nodes:
        g.add_node(node)

    while 1:
        head = random.choice(nodes)
        tail = random.choice(nodes)

        # loop defense
        if head == tail and not self_loops:
            continue

        # multiple edge defense
        if g.edge_by_node(head,tail) and not multi_edges:
            continue

        # add the edge
        g.add_edge(head, tail)
        if g.number_of_edges() >= edge_num:
            break

    return g

def generate_scale_free_graph(steps, growth_num, self_loops=False, multi_edges=False):
    '''
    Generates and returns a L{Graph.Graph} instance that will have C{steps*growth_num} nodes
    and a scale free (powerlaw) connectivity. Starting with a fully connected graph with C{growth_num} nodes
    at every step C{growth_num} nodes are added to the graph and are connected to existing nodes with
    a probability proportional to the degree of these existing nodes.
    '''
    graph = Graph.Graph()

    # initialize the graph
    store = []
    for i in range(growth_num):
        store   += [ i ] * (growth_num - 1)
        for j in range(i + 1, growth_num):
            graph.add_edge(i,j)

    # generate
    for node in range(growth_num, (steps-1) * growth_num):
        graph.add_node(node)
        while ( graph.out_degree(node) < growth_num ):
            nbr = random.choice(store)

            # loop defense
            if node == nbr and not self_loops:
                continue

            # multi edge defense
            if graph.edge_by_node(node, nbr) and not multi_edges:
                continue

            graph.add_edge(node, nbr)


        for nbr in graph.out_nbrs(node):
            store.append(node)
            store.append(nbr)

    return graph

def filter_stack(graph, head, filters):
    visited, removes, orphans = set([head]), set(), set()
    stack = deque([(head, head)])
    get_data = graph.node_data
    get_edges = graph.out_edges
    get_tail = graph.tail

    while stack:
        last_good, node = stack.pop()
        data = get_data(node)
        if data is not None:
            for filtfunc in filters:
                if not filtfunc(data):
                    removes.add(node)
                    break
            else:
                last_good = node
        for edge in get_edges(node):
            tail = get_tail(edge)
            if last_good is not node:
                orphans.add((last_good, tail))
            if tail not in visited:
                visited.add(tail)
                stack.append((last_good, tail))

    orphans = [(last_good, tail) for (last_good, tail) in orphans if tail not in removes]

    return visited, removes, orphans



if __name__ == '__main__':

    import Dot

    g = generate_scale_free_graph(steps=10, growth_num=4)

    d = Dot.Dot(g)

    d.all_node_style(width=1, shape='circle', style='filled', fillcolor='white')

    d.display()
    d.save_img()

    print g

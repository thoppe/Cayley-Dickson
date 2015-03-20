import networkx as nx
import pandas as pd
import numpy as np
import itertools
import src.cayley_dickson as KD

import graph_tool as gt
import graph_tool.draw as gtd

order = 2

def KD_table(order):
    reals = [1,]
    X = pd.DataFrame(1, index=reals,columns=reals)
    for n in range(order):
        X = KD.KD_construction(X.index)
    return X

def construct_group(order):
    C = KD_table(order)
    members = list(C) + [-x for x in C]
    N = members[0].terms*2
    G = np.zeros((N,N),dtype=int)
    for a,b in itertools.product(members,repeat=2):
        G[a.group_index(),b.group_index()] = (a*b).group_index()
    return G, members

color_set = ['r','g','b']     

def cayley_graph(G):
    '''From the Cayley multiplication table, determine the
    a group by right multiplying generators starting at index 1,
    e.g. the first non-real term.'''

    N = len(G)

    def edge_matrix(idx):
        ex = np.zeros(G.shape,dtype=int)
        for k in range(len(G)):
            ex[k][G[k][idx]] = 1
        return ex

    C = []
    for k in range(1,N):
        C.append(edge_matrix(k))
        g = nx.from_numpy_matrix(sum(C))
        if nx.is_connected(g):
            break

    # Determine the loop structure
    g_loop = nx.from_numpy_matrix(C[0])
    loops = sorted(list(nx.connected_components(g_loop)))
    
    # loops always come in groups of four
    square = np.array([[-1,-1.0],[-1,1],[1,1],[1,-1]])*(1/np.sqrt(2))

    g = gt.Graph(directed=True)
    g.add_vertex(N)

    pos = g.new_vertex_property("vector<double>")
    for k,loop in enumerate(loops):
        for idx,r in zip(loop,square):
            pos[g.vertex(idx)] = r*(k+1)
            print idx, r+k

    for k,c in enumerate(C):
        edges = zip(*np.where(c))
        print edges
        for e1,e2 in edges:
            print e1,e2
            g.add_edge(e1,e2)
    return g, pos

G,members = construct_group(order)
g,pos = cayley_graph(G)

#pos = gtd.sfdp_layout(g,multilevel=True)
#pos = gtd.fruchterman_reingold_layout(g)
#pos = gtd.arf_layout(g)
#pos = gtd.radial_tree_layout(g,1)

gtd.graph_draw(g,pos=pos,
               vertex_text=g.vertex_index, 
               vertex_font_size=18,)

#import pylab as plt
#nx.draw_graphviz(g)
#plt.show()

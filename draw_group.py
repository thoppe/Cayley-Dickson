import networkx as nx
import pandas as pd
import numpy as np
import itertools
import src.cayley_dickson as KD

import graph_tool as gt
import graph_tool.draw as gtd

import argparse

edge_color_set = ['r','g','b','k']


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

def draw_cayley_graph(G):
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
    loops = [np.roll(x,k) for k,x in enumerate(loops)]
    
    # loops always come in groups of four
    square = np.array([[-1,-1.0],[-1,1],[1,1],[1,-1]])*(1/np.sqrt(2))

    g = gt.Graph(directed=True)
    g.add_vertex(N)

    pos = g.new_vertex_property("vector<double>")
    for k,loop in enumerate(loops):
        for idx,r in zip(loop,square):
            pos[g.vertex(idx)] = r*(k+1)


    edge_color = g.new_edge_property("string")
    print "{} generators found for the group".format(len(C))
                
    for k,c in enumerate(C):
        edges = zip(*np.where(c))
        for e1,e2 in edges:
            ex = g.add_edge(e1,e2)
            edge_color[ex] = edge_color_set[k]

    gtd.graph_draw(g,pos=pos,
                   vertex_text=g.vertex_index, 
                   vertex_font_size=18,
                   edge_color=edge_color)


if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument('--f_png', type=str,default="g{order}.png")
    parser.add_argument('-n', '--order', type=int,default=2)
    args = parser.parse_args()

    G,members = construct_group(args.order)
    draw_cayley_graph(G)



import networkx as nx
import pandas as pd
import numpy as np
import itertools
import src.cayley_dickson as KD

import graph_tool as gt
import graph_tool.draw as gtd

import argparse

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
    return G, C, members

def draw_cayley_graph(order):
    '''From the Cayley multiplication table, determine the
    a group by right multiplying generators starting at index 1,
    e.g. the first non-real term.'''

    G,KD_system,members = construct_group(order)
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

    pos   = g.new_vertex_property("vector<double>")
    label = g.new_vertex_property("string")
    for k,loop in enumerate(loops):
        for idx,r in zip(loop,square):
            v = g.vertex(idx)
            name = KD.cayley_index_name(members[idx])
            if name is None: name = idx

            pos[v]   = r*(k+1)
            label[v] = name

    edge_color = g.new_edge_property("vector<double>")
    print "{} generators found for the group".format(len(C))
                
    for k,c in enumerate(C):
        edges = zip(*np.where(c))
        for e1,e2 in edges:
            ex = g.add_edge(e1,e2)
            edge_color[ex] = edge_color_set[k]

    gtd.graph_draw(g,pos=pos,
                   vertex_text=label,
                   vertex_font_size=18,
                   edge_color=edge_color,
                   vertex_size=30)

brewer_set1_colors = [
    (0.89411765336990356, 0.10196078568696976, 0.10980392247438431,.9), 
    (0.21602460800432691, 0.49487120380588606, 0.71987698697576341,.9), 
    (0.30426760128900115, 0.68329106055054012, 0.29293349969620797,.9), 
    (0.60083047361934883, 0.30814303335021526, 0.63169552298153153,.9), 
    (1.0, 0.50591311045721465, 0.0031372549487095253,.9), 
    (0.99315647868549117, 0.9870049982678657, 0.19915417450315812,.9), 
    (0.65845446095747107, 0.34122261685483596, 0.1707958535236471,.9), 
    (0.95850826852461868, 0.50846600392285513, 0.74492888871361229,.9)
]
edge_color_set = brewer_set1_colors


if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument('--f_png', type=str,default="g{order}.png")
    parser.add_argument('-n', '--order', type=int,default=2)
    args = parser.parse_args()

    draw_cayley_graph(args.order)



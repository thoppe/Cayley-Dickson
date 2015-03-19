import pandas as pd
import numpy as np
import src.cayley_dickson as KD
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--blank_negatives', action='store_true')
parser.add_argument('--diverging_colormap', action='store_false')
parser.add_argument('--f_png', type=str,default="K{order}.png")
parser.add_argument('--dont_save', action='store_true')
parser.add_argument('--dont_show', action='store_true')
parser.add_argument('-n', '--order', type=int,default=2)
args = parser.parse_args()

def KD_table(order):
    reals = [1,]
    X = pd.DataFrame(1, index=reals,columns=reals)
    for n in range(order):
        X = KD.KD_construction(X.index)
    return X

def identify_table(X):
    IDX = range(1,len(X)+1)
    lookup = dict(zip(IDX,X.index))
    Z = pd.DataFrame(index=X.index,columns=X.columns)

    for idx,val in lookup.items():
        Z[X==( val)] =  idx
        Z[X==(-val)] = -idx

    return Z.values.astype(float)

C = KD_table(args.order)
Z = identify_table(C)
N = Z.shape[0]

if args.order<=2:
    print C

import pylab as plt
import matplotlib as mpl
import seaborn as sns
sns.set_style("white")
rect  = mpl.patches.Rectangle

palette_name = "RdBu_r"
#palette_name = "hls"


fig, ax = plt.subplots(figsize=(5,5))

if args.diverging_colormap:
    pal = sns.color_palette(palette_name, 2*N+1)
else:
    pal = sns.color_palette(palette_name, N)

for (i,j),z in np.ndenumerate(Z):
    loc   = (j, N-i-1)

    if args.diverging_colormap:
        color = pal[int(z)+N]
    else:
        color = pal[int(abs(z))-1]

    if args.blank_negatives:
        lw = 0.5
    else:
        lw = 1

    R = rect(loc,1,1,snap=False,
             edgecolor=color,
             facecolor=color,lw=lw,zorder=1)
    ax.add_patch(R)

for (i,j),z in np.ndenumerate(Z):
    loc   = (j, N-i-1)
    gc = (0.05,)*3
    if args.blank_negatives and z<0:
        R = rect(loc,1,1,lw=1.5,
                 facecolor=gc,edgecolor=gc,zorder=2)
        ax.add_patch(R)
        print i,j,z,loc

ax.set_xlim(0,N)
ax.set_ylim(0,N)
ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])

plt.tight_layout()

if not args.dont_save:
    f_png = args.f_png.format(order=args.order)
    plt.savefig(f_png)

if not args.dont_show:
    plt.show()


        


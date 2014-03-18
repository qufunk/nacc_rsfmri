#!/usr/bin/python

import numpy as np
import networkx as nx
import tempfile
import subprocess as sub
import matplotlib.pyplot as plt
from itertools import combinations

# our imports
from utils import run_cmd

#########################################
# Heatmap
#########################################

# creates square heatmap (row/col labels are same)
# * current setup highlights positive-only relationships
def heatmap(matrix, labels=None, limits=[0,1], cm=plt.cm.YlGn_r):
    # limits
    mn,mx = limits

    # Plot it out
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(matrix, cmap=cm, alpha=0.95, vmin=mn, vmax=mx)

    # Format
    fig = plt.gcf()
    fig.set_size_inches(12, 10)

    # turn off the frame
    ax.set_frame_on(False)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(matrix.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(matrix.shape[1]) + 0.5, minor=False)

    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    # Set the labels
    if labels is None: labels = matrix.index

    # note I could have used nba_sort.columns but made "labels" instead
    ax.set_xticklabels(labels, minor=False)
    ax.set_yticklabels(labels, minor=False)

    # rotate the
    plt.xticks(rotation=90)

    ax.grid(False)

    # Turn off all the ticks
    ax = plt.gca()

    # insert color bar
    plt.colorbar(heatmap)

    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False

    return fig


#########################################
# Network Graphs
#########################################

# return graph object
def generate_network_graph(matrix, thresh, nodes, attributes={}):
    G = nx.Graph()
    # add nodes
    for node in nodes: G.add_node(node)
    # add links
    for a,b in combinations(range(matrix.shape[0]), r=2):
        if matrix[a,b] <= thresh: continue
        G.add_edge(nodes[a],
                   nodes[b],
                   {attr: d[a,b] for attr,d in attributes.iteritems()},
                   weight = matrix[a,b])
    # return graph
    return G


# return figure of graph
def plot_network_graph(G,
               weight='weight',
               edge_color_attr='weight',
               node_color_attr=None,
               cm=plt.cm.Reds,
               node_cm=plt.cm.OrRd,
               vmin=.1,
               vmax=.4,
               layout=None):

    edgecolor = [G.edge[a][b][edge_color_attr] for a,b in G.edges()]

    fig = plt.figure(figsize=(18,12))

    if not layout:
        layout = nx.spring_layout(G)

    nx.draw(G,
            pos=layout,
            node_size=2500,
            node_color='w',
            font_size=10,
            edge_color=edgecolor,
            edge_cmap=cm,
            edge_vmin=vmin,
            edge_vmax=vmax,
            width=3)

    return fig


def snapshot_overlay(underlay, overlay, out_file, min=.1, max=.5):
    # first, generate a combined volume (overlay and underlay)
    tmp_vol = tempfile.mktemp(suffix='.nii.gz')
    cmd = 'overlay 0 1 {underlay} -a {overlay} {min} {max} {output}' \
            .format( underlay = underlay,
                     overlay  = overlay,
                     min      = min,
                     max      = max,
                     output   = tmp_vol)
    run_cmd(cmd)

    # take axial, sagittal, coronal views
    tmp_img = tempfile.mktemp(suffix='.png')
    cmd='slicer {input} -a {output} -t'.format(input=tmp_vol, output=tmp_img)
    run_cmd(cmd)

    # scale the image (default is too small)
    cmd='convert {input} -scale 300% -trim {output}'.format(input=tmp_img, output=out_file)
    run_cmd(cmd)


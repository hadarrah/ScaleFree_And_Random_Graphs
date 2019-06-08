#! /usr/bin/env python

import networkx as nx
import pandas as pd
import math
import random
NODES = 1079
P = 0.01

def generate_xlsx(x_list, y_list, x_name, y_name, graph_name, xlsx_file, title):
    # this part of code was taken from:
    # https://www.geeksforgeeks.org/python-working-with-pandas-and-xlsxwriter-set-3/
    data_dict = {x_name: x_list, y_name: y_list}
    df_toExport = pd.DataFrame(data_dict)

    writer = pd.ExcelWriter(xlsx_file, engine='xlsxwriter')
    df_toExport.to_excel(writer, sheet_name=graph_name)
    workbook = writer.book
    worksheet = writer.sheets[graph_name]
    chart = workbook.add_chart({'type': 'line'})
    # [sheetname, first_row, first_col, last_row, last_col].
    chart.add_series({
        'categories': [graph_name, 1, 1, len(x_list), 1],
        'values': [graph_name, 1, 2, len(x_list), 2],
    })
    chart.set_title({'name': title})
    # Configure the chart axes.
    chart.set_y_axis({'major_gridlines': {'visible': False}})
    chart.set_y_axis({'name': y_name})
    chart.set_x_axis({'name': x_name, 'label_position': 'low'})

    # Turn off chart legend. It is on by default in Excel.
    chart.set_legend({'position': 'none'})

    # Insert the chart into the worksheet.
    worksheet.insert_chart('D2', chart)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

def create_pk_degree_dictionary(total_deg_dist, specific_deg_dist):
    general_dict = {}
    cluster1_dict = {}
    cluster2_dict = {}

    for vertex in total_deg_dist:
        # general degree distribution
        if (total_deg_dist[vertex] not in general_dict):
            general_dict[total_deg_dist[vertex]] = 1
        else:
            general_dict[total_deg_dist[vertex]] += 1

    for vertex in specific_deg_dist:
        # cluster 1 degree distribution
        if (vertex <= math.ceil(NODES / 2) and specific_deg_dist[vertex] not in cluster1_dict):
            cluster1_dict[specific_deg_dist[vertex]] = 1
        elif (vertex <= math.ceil(NODES / 2)):
            cluster1_dict[specific_deg_dist[vertex]] += 1
        # cluster 2 degree distribution
        if (vertex > math.ceil(NODES / 2) and specific_deg_dist[vertex] not in cluster2_dict):
            cluster2_dict[specific_deg_dist[vertex]] = 1
        elif (vertex > math.ceil(NODES / 2)):
            cluster2_dict[specific_deg_dist[vertex]] += 1
    return general_dict, cluster1_dict, cluster2_dict


def create_xy_axis_list(dict, total_nodes):
    x = []
    y = []
    for degree in sorted(dict.keys()):
        x.append(degree)
        y.append(dict[degree] / total_nodes)
    return x, y


if __name__ == "__main__":

    #############################################
    #                  variables                #
    #############################################

    sf_edges = 0             # counter of generated edges in scale-free graph
    er_edges = 0             # counter of generated edges in random graph
    total_deg_dist = {}      # dictionary for general degree distribution: key=degree, value=number of instance with related degree
    specific_deg_dist = {}   # dictionary for sub-graph degree distribution: key=degree, value=number of instance with related degree
    edges = []               # edges general list
    x_list = []              # values list for x axis in general degree distribution graph
    x_dict = {}              # temp dictionary for Pk calculation in general degree distribution graph: key=degree, value=number of vertex with this degree
    y_list = []              # values list for y axis in general degree distribution graph
    x_list_c1 = []           # values list for x axis in cluster 1 (scale-free) degree distribution graph
    x_dict_c1 = {}           # temp dictionary for Pk calculation in cluster 1 degree distribution graph: key=degree, value=number of vertex with this degree
    y_list_c1 = []           # values list for y axis in cluster 1 (scale-free) degree distribution graph
    x_list_c2 = []           # values list for x axis in cluster 2 (random) general degree distribution graph
    x_dict_c2 = {}           # temp dictionary for Pk calculation in cluster 2 degree distribution graph: key=degree, value=number of vertex with this degree
    y_list_c2 = []           # values list for y axis in cluster 2 (random) general degree distribution graph

    #############################################
    #               Graphs generator            #
    #############################################

    # build random sub-graph
    er = nx.generators.random_graphs.erdos_renyi_graph(math.floor(NODES/2), P)

    # build scale-free sub-graph
    # i found out that m=3 will grant me similar amount of nodes between the 2 clusters
    sf = nx.barabasi_albert_graph(math.ceil(NODES / 2), 3)

    #############################################
    #        Generate .net and .clu files       #
    #############################################

    with open("mynet.net", "w+") as net_file, open("myclusters.clu", "w+") as clu_file:
        net_file.write("*Vertices {}\n".format(NODES))
        clu_file.write("*Vertices {}\n".format(NODES))
        net_file.write("*Edges\n")

        # start for scale-free nodes
        for edge in sf.edges():
            new_edge = list(edge)
            new_edge[0] = new_edge[0] + 1   # start from 1 and not from 0
            new_edge[1] = new_edge[1] + 1   # start from 1 and not from 0

            # ignore possible duplication edges or self edge from the module
            if (new_edge in edges):
                continue
            if (new_edge[0] == new_edge[1]):
                continue

            net_file.write("{ver1} {ver2}\n".format(ver1=new_edge[0], ver2=new_edge[1]))
            sf_edges += 1
            # add randomly edge to node in the random cluster in order to make sure "internal edges=external edges"
            random_node = random.randint(math.ceil(NODES/2)+1, NODES)
            net_file.write("{ver1} {ver2}\n".format(ver1=new_edge[0], ver2=random_node))
            edges.append(new_edge)

            # update degree distribution for 2 vertexes in sub-graph perspective
            if (new_edge[0] in specific_deg_dist):
                specific_deg_dist[new_edge[0]] += 1
            else:
                specific_deg_dist[new_edge[0]] = 1
            if (new_edge[1] in specific_deg_dist):
                specific_deg_dist[new_edge[1]] += 1
            else:
                specific_deg_dist[new_edge[1]] = 1

            # update degree distribution for 2 vertexes in total graph perspective
            if (new_edge[0] in total_deg_dist):
                total_deg_dist[new_edge[0]] += 2
            else:
                total_deg_dist[new_edge[0]] = 2
            if (random_node in total_deg_dist):
                total_deg_dist[random_node] += 1
            else:
                total_deg_dist[random_node] = 1

        # add for random nodes
        for edge in er.edges():
            new_edge = list(edge)
            new_edge[0] = new_edge[0] + 1 + math.ceil(NODES/2)  # start from the last indexing of sf
            new_edge[1] = new_edge[1] + 1 + math.ceil(NODES/2)  # start from the last indexing of sf

            # ignore possible duplication edges or self edge from the module
            if (new_edge in edges):
                continue
            if (new_edge[0] == new_edge[1]):
                continue

            net_file.write("{ver1} {ver2}\n".format(ver1=new_edge[0], ver2=new_edge[1]))
            er_edges += 1
            edges.append(new_edge)

            # update degree distribution for 2 vertexes in sub-graph perspective
            if (new_edge[0] in specific_deg_dist):
                specific_deg_dist[new_edge[0]] += 1
            else:
                specific_deg_dist[new_edge[0]] = 1
            if (new_edge[1] in specific_deg_dist):
                specific_deg_dist[new_edge[1]] += 1
            else:
                specific_deg_dist[new_edge[1]] = 1

            # update degree distribution for 2 vertexes in total graph perspective
            if (new_edge[0] in total_deg_dist):
                total_deg_dist[new_edge[0]] += 1
            else:
                total_deg_dist[new_edge[0]] = 1
            if (new_edge[1] in total_deg_dist):
                total_deg_dist[new_edge[1]] += 1
            else:
                total_deg_dist[new_edge[1]] = 1

        print("Edges sf: {}\nEdges er: {}".format(sf_edges, er_edges))

        # cluster assignment
        for node in sf.nodes():
            clu_file.write("1\n")  # assign to cluster 1 scale-free

        for node in er.nodes():
            clu_file.write("2\n")  # assign to cluster 2 random

        #############################################
        # export degree distribution to xlsx file   #
        #############################################

        # get the temporary degree distribution dictionary
        x_dict, x_dict_c1, x_dict_c2 = create_pk_degree_dictionary(total_deg_dist, specific_deg_dist)

        # x and y axis creation
        x_list, y_list = create_xy_axis_list(x_dict, NODES)
        x_list_c1, y_list_c1 = create_xy_axis_list(x_dict_c1, math.ceil(NODES / 2))
        x_list_c2, y_list_c2 = create_xy_axis_list(x_dict_c2, math.floor(NODES / 2))

        # generate xlsx files
        generate_xlsx(x_list, y_list, "Degree K", "Pk", "degree_distribution", "degree_distribution.xlsx", "General Degree Distribution")
        generate_xlsx(x_list_c1, y_list_c1, "Degree K", "Pk", "degree_distribution_c1", "degree_distribution_c1.xlsx", "Scale Free Degree Distribution")
        generate_xlsx(x_list_c2, y_list_c2, "Degree K", "Pk", "degree_distribution_c2", "degree_distribution_c2.xlsx", "Random Degree Distribution")





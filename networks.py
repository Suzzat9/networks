import igraph
from igraph import Graph
from numpy import genfromtxt
import matplotlib.pyplot as plt
import math
import pandas as pd

file = 'data/adj_allVillageRelationships_HH_vilno_2.csv'

leader_data = pd.read_stata("data/panel.dta", index_col="village")

class Vill_Net:
    '''
    Class for networks of villages. 

    Attributes -
    ._g - igraph object of the network
    ._p_rate - percent of households enrolled
    in microfinance
    ._num_nodes - number of households
    ._evcent_round - list of eigen_vector 
    centrality values (used in mf_takeup)

    Methods-
    mf_takeup: Adding take_up attribute (0 or 1)
    to a household
    plot_graph: plot the network showing the households
    currently participating in microfinance
    '''

    def __init__(self, adjmat, villno):

        '''

        Initiliazation of the Vill_Net class

        Inputs:
        adjmat (str): File path of the adjacency matrix of the village (csv)
        to read in
        villno: Village number (int)
        '''

        data = genfromtxt(adjmat, delimiter=',', skip_header = 0)
        self._g = Graph.Adjacency(data)
        self._p_rate = leader_data.loc[villno]["dynamicMF_simulated"]
        self._num_nodes = len(list(self._g.vs()))

        evcent = self._g.evcent()
        self._evcent_round = [round(ev, 4) for ev in evcent]
        self._g.vs["ev_centrality"] = self._evcent_round

        # For visualization
        layout = self._g.layout('kk')
        self.visual_style = {}
        self.visual_style["vertex_size"] = 4
        self.visual_style["edge_width"] = 0.1
        self.visual_style["edge_arrow_width"] = 0.1
        self.visual_style["layout"] = layout
        


    def mf_takeup(self, time_period):
        '''
        Add a take_up attribute to every node in the village,
        where for a specific percent of take up X in time 
        period Y, X * total_number of nodes take up microfinance
        in period Y. Take up is according to the following process-
        Assuming nodes with higher eigen vector centrality are
        more likely to hear about microfinance, rank nodes according
        to EV centrality and choose the highest X * total_nodes 
        for take_up

        Inputs-
        time_period - (int)- time period to specify take-up
        '''
        
        try:
            take_up_num = int(math.floor(self._num_nodes * self._p_rate.iloc[time_period]))
        except IndexError:
            print("time period does exist")

        ev_sorted = sorted(self._evcent_round, reverse = True)
        take_up = ev_sorted[0:take_up_num + 1]

        for v in range(self._num_nodes):
            if self._g.vs[v]["ev_centrality"] in take_up:
                self._g.vs[v]["take_up"] = 1
            else:
                self._g.vs[v]["take_up"] = 0
        
        color_dict = {1: "red", 0: "blue"}
        self.visual_style["vertex_color"] = [color_dict[take_up] for take_up in self._g.vs["take_up"]]
    
    def plot_graph(self, show = True):
        '''
        Plot the network graph in its current
        state, green nodes are ones that have 
        taken up MF
        '''

        fig, ax = plt.subplots()
        plt.axis('off')
        igraph.plot(self._g, **self.visual_style, target=ax)
        if show:
            plt.show()
    
    def plot_multiple(self):
        '''
        Plot the microfinance take up of 
        a village for all time periods
        '''

        self.visual_style["vertex_size"] = 2
        self.visual_style["edge_width"] = 0.05
        self.visual_style["edge_arrow_width"] = 0.05

        rows = math.ceil(len(self._p_rate)/3)

        for i in range(len(self._p_rate)):

            self.mf_takeup(i)
            if i <= 2:
                j = 0
                k = i
            elif i > 2 and i <= 5:
                j = 1
                k = i - 3
            elif i > 5 and i <= 8:
                j = 2
                k = i - 6
            else:
                j = 3
                k = i - 9
            plt.figure(0)
            ax = plt.subplot2grid((rows, 3), (j, k))
            plt.axis('off')
            plt.title(str('time-' + str(i)))
            igraph.plot(self._g, **self.visual_style, target=ax)
        
        plt.show()
            
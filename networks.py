from igraph import Graph
from numpy import genfromtxt
import math
import pandas as pd
import plotly.graph_objects as go


leader_data = pd.read_stata("data/panel.dta", index_col="village")

class Vill_Net:
    '''
    Class visualizing the social network of a village. 

    --Attributes--
    ._g : igraph object of the network
    ._p_rate : percent of households enrolled
    in microfinance
    ._num_nodes : number of households
    ._evcent_round : list of eigen_vector 
    centrality values (used in mf_takeup)

    --Methods--
    mf_takeup: Adding take_up attribute (0 or 1)
    to each household (node) in the village
    plot_graph: plot the village network showing the households
    currently participating in microfinance
    gen_plots: plot the village network for all time periods and
    output a list of plots
    '''

    def __init__(self, adjmat: str, villno: int) -> None:

        '''
        Initiliazation of the Vill_Net class
        Inputs:
        adjmat: File path of the adjacency matrix of the village (csv)
        to read in
        villno: Village number (int) (currently only have data for villages 1, 2, 3)

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
        self.visual_style["layout"] = layout
        

    def mf_takeup(self, time_period: int):
        '''
        Add a take_up attribute to every node in the village as follows -

        For a specific percent of take up X in time 
        period Y, X * total_number of nodes take up microfinance
        in period Y. Take up is according to the following process-
        Assuming nodes with higher eigen vector centrality are
        more likely to hear about microfinance, rank nodes according
        to EV centrality and choose the highest X * total_nodes. These
        nodes will get a take_up value = 1.

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
    
    def plot_graph(self, title: str):
        '''
        Plot the network graph in its current
        state, red nodes are ones that have 
        taken up microfinance

        title: title of the graph
        '''

        labels=list(self._g.vs.indices)
        E=[e.tuple for e in self._g.es]
        layt=self._g.layout('kk')

        # Build layout
        Xn=[layt[k][0] for k in range(self._num_nodes)]
        Yn=[layt[k][1] for k in range(self._num_nodes)]
        Xe=[]
        Ye=[]
        for e in E:
            Xe+=[layt[e[0]][0],layt[e[1]][0], None]
            Ye+=[layt[e[0]][1],layt[e[1]][1], None]
        
        trace1=go.Scatter(x=Xe,
               y=Ye,
               mode='lines',
               line= dict(color='rgb(210,210,210)', width=1),
               hoverinfo='none'
               )
        trace2=go.Scatter(x=Xn,
               y=Yn,
               mode='markers',
               name='ntw',
               marker=dict(symbol='circle-dot',
                                        size=5,
                                        color=self.visual_style["vertex_color"],
                                        line=dict(color='rgb(50,50,50)', width=0.5)
                                        ),
               text=labels,
               hoverinfo='text'
                )
        axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
          zeroline=False,
          showgrid=False,
          showticklabels=False,
          title='')
        # Build layout
        layout=go.Layout(title=title,
        font= dict(size=10),
        showlegend=False,
        autosize=False,
        width=300,height=300,margin=dict(b=20,l=5,r=5,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hovermode='closest',
        )
        data=[trace1, trace2]
        fig=go.Figure(data=data, layout=layout)

        return fig
    
    def gen_plots(self):
        '''
        Plot the network and output a list of graphs for all time
        periods
        '''

        plots = []

        for i in range(len(self._p_rate)):
            self.mf_takeup(i)
            fig = self.plot_graph(title=str("time period-" + str(i)))
            plots.append(fig)
        
        return plots

            
# -*- coding: utf-8 -*-
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
class Tree_plotter:
    """
    Class for plotting the tree graph
    """
    def __init__(self, *args, **kwargs):
        self.source_df = None
        self.df = None
        self.groups_df = None
       
        #Showing of labels - possible "all", "results", "none"
        self.show_labels = "all"
        #Showing paths - possible "all", "results", "none"
        self.show_paths = "all"
        #Display style - 
        self.display_style = "gradient-colour"
        #List of currently shown paths
        self.visible_paths=[]
        self.fig = None


    def draw_plot(self, graph_type):
        #Get the name of the field with values from uploaded dataframe
        if self.df is None:
            self.var = "value"
            self.full_df["value"] = 0
        else:
            self.var = self.df.columns[1]
            self.full_df = pd.merge(
                self.source_df,
                self.df,
                how="left",
                left_on="id.uniprot",
                right_on="id")
        self.graph_type = graph_type     

        #Labels visibility logic
        if self.show_labels == "all":
            self.full_df["id_label"] = self.full_df["id.base"]
        if self.show_labels == "results":
            self.full_df["id_label"] = [row["id.base"] if row[self.var] > 0 else None for i, row in self.full_df.iterrows()]
        if self.show_labels == "none":
            self.full_df["id_label"] = None

        if self.display_style == "group-colour":
            self.full_df[self.var] = self.full_df[self.var].fillna(0)
            scatter_colour = "group"
            scatter_size = self.var
            scatter_size_max = None
        if self.display_style == "gradient-colour":
            self.full_df["marker_size"] = 15
            scatter_colour = self.var
            scatter_size = "marker_size"
            scatter_size_max = 15
        
        fig = px.scatter(self.full_df, x="node.x", y="node.y",
                    color=scatter_colour,
                    size=scatter_size,
                    size_max=scatter_size_max,
                    text="id_label",
                    hover_data=["id.base", "id.uniprot"])
        
        fig.update_layout(clickmode='event+select')
        
        self.groups_df = pd.read_csv("data/{}_group_labels.tsv".format(self.graph_type), sep='\t')
        for i, group in self.groups_df.iterrows():
            fig.add_annotation(x=group["x"], y=group["y"],
                text="<b>{}</b>".format(group["label"]),
                font_color=group["color"],
                font_size=group["size"],
                showarrow=False)

#        fig.add_trace(
#            go.Scatter(x=df["text.x"],y=df["text.y"],text=df["id"],mode="text")
#            )
        fig.update_layout(yaxis_visible=False, yaxis_showticklabels=False)
        fig.update_layout(xaxis_visible=False, xaxis_showticklabels=False)
        #fig.update_layout(xaxis_range=[0,2000])
        #fig.update_layout(yaxis_range=[0,2000])
        fig.update_layout(plot_bgcolor= 'rgba(0, 0, 0, 0)', paper_bgcolor= 'rgba(0, 0, 0, 0)')
        if self.show_paths == "none":
            pass
        else:
            if self.show_paths == "all":
                self.full_df["branch.opacity"] = 1
                path_df=self.full_df[["branch.coords", "branch.col", "branch.opacity"]]
            if self.show_paths == "results":
                self.full_df["branch.opacity"] = [1 if ((x[self.var] is not None) and (x[self.var] > 0)) else 0.3 for i, x in self.full_df.iterrows()]
                path_df=self.full_df[["branch.coords", "branch.col", "branch.opacity"]]
            fig.update_layout(
                shapes=[dict(type="path",path=branch["branch.coords"],fillcolor=branch["branch.col"], line_color=branch["branch.col"], opacity=branch["branch.opacity"]) for i, branch in path_df.iterrows()])
            fig.update_shapes(layer="below")
        self.visible_paths = list(self.full_df["group"].drop_duplicates().reset_index()["group"])
        
        #Labels positions
        def assign_textposition(node_x, node_y, text_x, text_y):
            x_offset = text_x - node_x
            y_offset = text_y - node_y
            if (-1 < x_offset) & (x_offset < 1):
                x_pos = "center"
            elif x_offset <= 0:
                x_pos = "left"
            elif x_offset >= 0:
                x_pos = "right"
        
            if (-1 < y_offset) & (y_offset < 1):
                y_pos = "middle"
            elif x_offset <= 0:
                y_pos = "bottom"
            elif x_offset >= 0:
                y_pos = "top"
        
            return y_pos+" "+x_pos
        
        self.full_df["textposition"] = [assign_textposition(row["node.x"],row["node.y"],row["text.x"],row["text.y"]) for i, row in self.full_df.iterrows()]
        fig.update_traces(textposition=self.full_df["textposition"], selector=dict(type='scatter'))
        
        self.fig = fig

    def update_plot(self):
        self.draw_plot(self.graph_type)
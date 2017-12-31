# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 18:13:49 2017

@author: coach
"""


import pandas as pd
pd.options.mode.chained_assignment = None
from bokeh.io import show, curdoc
from bokeh.models import *
from bokeh.plotting import figure
from bokeh.layouts import column, widgetbox, row
from bokeh.sampledata.us_states import data as state_locs
import numpy as np
from operator import itemgetter
from bokeh.palettes import OrRd as orrd
import os
from math import pi

blues = orrd[8]


#For executing from command line as a package
"""current_file = os.path.abspath(os.path.dirname('cleaned.csv'))

csv_filename = os.path.join(current_file, 'CFS_app/cleaned.csv')"""

#For executing in iPython shell or from command line as a .py file
csv_filename = 'cleaned.csv'


data = pd.read_csv(csv_filename, index_col=0)

data.reset_index(inplace=True, drop=True)


axis_vals = {'Shipment Weight (lbs)':'SHIPMT_WGHT', 'Shipment Value (USD)':'SHIPMT_VALUE', 'Shipment Distance (mi)':'SHIPMT_DIST_ROUTED'}

short_desc = []
for v in data.SCTG.unique():
    short = v[:25] + '...'
    short_desc.append(short)
    
states = []
for state in data.ORIG_STATE.unique():
    if state not in states and state != '00':
        states.append(state)
for state in data.DEST_STATE.unique():
    if state not in states and state != '00':
        states.append(state)
states = states[1:]




def make_chloro_source(data):
    values = []
    weights = []
    states_list = list(data['ORIG_STATE'].unique()) + list(data['DEST_STATE'].unique())
    states_two = []
    for state in states_list:
        if state not in states_two and state != '00':
            states_two.append(state)
    
    for state in states:
        if state in states_two:
            value1 = np.nan_to_num(data[data['ORIG_STATE'] == state]['SHIPMT_VALUE'].sum())
            value2 = np.nan_to_num(data[data['DEST_STATE'] == state]['SHIPMT_VALUE'].sum())
            value = value1 + value2
            values.append(value)
            print(state, value1, type(value1), value2, type(value2), value, type(value))
            weight1 = np.nan_to_num(data[data['ORIG_STATE'] == state]['SHIPMT_WGHT'].sum())
            weight2 = np.nan_to_num(data[data['DEST_STATE'] == state]['SHIPMT_WGHT'].sum())
            weight = weight1 + weight2
            weights.append(weight)
        else:
            values.append(0)
            weights.append(0)
            

    m = [x for x in np.linspace(min(values), max(values), num=8, endpoint=True)]
    
    colors = []
    
    for v in values:
        if v <= m[0]:
            colors.append(blues[7])
        elif v <= m[1] and v > m[0]:
            colors.append(blues[6])
        elif v <= m[2] and v > m[1]:
            colors.append(blues[5])
        elif v <= m[3] and v > m[2]:
            colors.append(blues[4])
        elif v <= m[4] and v > m[3]:
            colors.append(blues[3])
        elif v <= m[5] and v > m[4]:
            colors.append(blues[2])
        elif v <= m[6] and v > m[5]:
            colors.append(blues[1])
        elif v <= m[7] and v > m[6]:
            colors.append(blues[0])
        else:
            colors.append('black') 
    
    state_xs = [state_locs[code]['lons'] for code in states]
    state_ys = [state_locs[code]['lats'] for code in states]
    
    for i,v in enumerate(state_xs):
        new_v = []
        for idx,val in enumerate(v):
            if val > -150:
                new_v.append(val - 40)
            else:
                new_v.append(val)
        state_xs[i] = new_v
    
    chloro_data = dict(
            state_xs=state_xs,
            state_ys=state_ys,
            name=[state for state in states],
            values=np.asarray(values),
            weights=np.asarray(weights),
            colors=colors)
    
    return chloro_data

  

def make_source(data):
    
    indices = []
    for i,v in enumerate(data.ORIG_STATE):
        if v in origin_select.value:
            indices.append(i)
    data = data.iloc[indices]
    indices = []
    for i,v in enumerate(data.DEST_STATE):
        if v in dest_select.value:
            indices.append(i)
    data = data.iloc[indices]
    indices = []
    for i,v in enumerate(data.MODE):
        if v in mode_select.value:
            indices.append(i)
    data = data.iloc[indices]
    indices = []
    for i,v in enumerate(data.HAZMAT):
        if v in hazmat_select.value:
            indices.append(i)
    data = data.iloc[indices]
    indices = []
    for i,v in enumerate(data.SCTG):
        if v in sctg_select.value:
            indices.append(i)
    data = data.iloc[indices]
    total_data = data #This is used to create the barplot_source
    data = data.drop_duplicates(keep='first') #This is used to create the primary source for the scatter plot
       
    
    #update source for chloropleth map
    chloro_data = make_chloro_source(data)
    chloro_source.data = chloro_data
    
    #update primary source for scatter plot
    source.data = dict(
            x=data[axis_vals[x_axis_select.value]],
            y=data[axis_vals[y_axis_select.value]],
            ORIG_STATE = data['ORIG_STATE'],
            DEST_STATE = data['DEST_STATE'],
            NAICS = data['NAICS'],
            MODE = data['MODE'],
            HAZMAT = data['HAZMAT'],
            SCTG = data['SCTG'],
            SHIPMT_WGHT = data['SHIPMT_WGHT'],
            SHIPMT_VALUE = data['SHIPMT_VALUE'],
            SHIPMT_DIST_ROUTED = data['SHIPMT_DIST_ROUTED']
            )
    
    plot.xaxis.axis_label = x_axis_select.value
    if x_axis_select.value == 'Shipment Value (USD)':
        plot.xaxis.formatter = NumeralTickFormatter(format='$0a')
    elif x_axis_select.value == 'Shipment Distance (mi)':
        plot.xaxis.formatter = NumeralTickFormatter(format='0,0')
    else:
        plot.xaxis.formatter = NumeralTickFormatter(format='0a')
    plot.yaxis.axis_label = y_axis_select.value
    if y_axis_select.value == 'Shipment Value (USD)':
        plot.yaxis.formatter = NumeralTickFormatter(format='$0a')
    elif y_axis_select.value == 'Shipment Distance (mi)':
        plot.yaxis.formatter = NumeralTickFormatter(format='0,0')
    else:
        plot.yaxis.formatter = NumeralTickFormatter(format='0a')
    
    #create data for bar plot
    mode_count = {}
    for mode in total_data.MODE.unique():
        total = len(total_data[total_data['MODE'] == mode])
        value = total_data[total_data['MODE'] == mode]['SHIPMT_VALUE'].sum()
        weight = total_data[total_data['MODE'] == mode]['SHIPMT_WGHT'].sum()
        mode_count[mode] = {'Total':total, 'Value':value, 'Weight':weight}
    
    bar_data = pd.DataFrame()
    bar_data['MODE'] = mode_count.keys()
    bar_data['COUNT'] = [d['Total'] for d in list(mode_count.values())]
    bar_data['VALUE'] = [d['Value'] for d in list(mode_count.values())]
    bar_data['WEIGHT'] = [d['Weight'] for d in list(mode_count.values())]
    
    bar_source.data = dict(
            MODE=bar_data['MODE'],
            y=bar_data[radio_labels[radio_group.active]],
            COUNT=bar_data['COUNT'],
            VALUE=bar_data['VALUE'],
            WEIGHT=bar_data['WEIGHT'])
    
    barplot.yaxis[0].axis_label = "Aggregate {}".format(radio_labels[radio_group.active])
    barplot.title.text = "Aggregate {} of Commodity by Mode of Transport".format(radio_labels[radio_group.active])
    if barplot.yaxis[0].axis_label == 'Aggregate VALUE':
        barplot.yaxis.formatter = NumeralTickFormatter(format='$ 0 a')
    else:
        barplot.yaxis.formatter = NumeralTickFormatter(format='0,0a')
        
    #create data for second bar plot
    sctg_count = {}
    for sctg in total_data.SCTG.unique():
        total = len(total_data[total_data['SCTG'] == sctg])
        value = total_data[total_data['SCTG'] == sctg]['SHIPMT_VALUE'].sum()
        weight = total_data[total_data['SCTG'] == sctg]['SHIPMT_WGHT'].sum()
        sctg_count[sctg] = {'Total':total, 'Value':value, 'Weight':weight}

    bar2_data = pd.DataFrame()
    bar2_data['SCTG'] = sctg_count.keys()
    bar2_data['COUNT'] = [d['Total'] for d in list(sctg_count.values())]
    bar2_data['VALUE'] = [d['Value'] for d in list(sctg_count.values())]
    bar2_data['WEIGHT'] = [d['Weight'] for d in list(sctg_count.values())]
    bar2_data['Short'] = ''
    for i,v in enumerate(bar2_data['SCTG']):
        bar2_data['Short'].iloc[i] = v[:25] + '...'
     
    bar2_source.data = dict(
            SCTG=bar2_data['SCTG'],
            y=bar2_data[radio_labels[radio_group.active]],
            COUNT=bar2_data['COUNT'],
            VALUE=bar2_data['VALUE'],
            WEIGHT=bar2_data['WEIGHT'],
            Short=bar2_data['Short'])
    
    barplot2.yaxis[0].axis_label = "Aggregate {}".format(radio_labels[radio_group.active])
    barplot2.title.text = "Aggregate {} by Commodity".format(radio_labels[radio_group.active])
    if barplot2.yaxis[0].axis_label == 'Aggregate VALUE':
        barplot2.yaxis.formatter = NumeralTickFormatter(format='$ 0 a')
    else:
        barplot2.yaxis.formatter = NumeralTickFormatter(format='0,0a')
        

def make_scatter_plot(source):
    hover = HoverTool(tooltips=[('Value', '$@SHIPMT_VALUE{0,0}'), ('Weight', '@SHIPMT_WGHT{0,0} lbs'), ('Origin', '@ORIG_STATE'), ('Destination', '@DEST_STATE'), ('Distance', '@SHIPMT_DIST_ROUTED mi'), ('HAZMAT', '@HAZMAT'), ('Mode', '@MODE'), ('Type Goods', '@SCTG'), ('NAICS', '@NAICS')])
    plot = figure(plot_width=750, plot_height=650, tools=[hover, WheelZoomTool(), PanTool(), ResetTool(),BoxZoomTool(), SaveTool()])
    plot.title.text = "Alaska's Commodity Flows - 2012 CFS"
    plot.title.align = 'center'
    plot.title.text_font_size = '14pt'
    plot.xaxis.axis_label = 'Shipment Value (USD)'
    plot.yaxis.axis_label = 'Shipment Weight (lbs)'
    plot.circle(x='x', y='y', source=source)
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_alpha = 0.6
    plot.ygrid.grid_line_dash = [6,4]
            
    return plot

def make_barplot(source):
    hover = HoverTool(tooltips=[('Total Value', '$@VALUE{0,0}'), ('Total Weight', '@WEIGHT{0,0} lbs')])
    barplot = figure(x_range=sorted(data['MODE'].unique()), y_range=DataRange1d(), plot_height=350, plot_width=1050, tools=[hover, BoxZoomTool(), ResetTool(), SaveTool()])
    barplot.title.text = "Aggregate {} of Commodity by Mode of Transport".format(radio_labels[radio_group.active])
    barplot.title.align = 'center'
    barplot.title.text_font_size = '14pt'
    barplot.xaxis.axis_label = "Mode of Transport"
    barplot.yaxis.axis_label = "Aggregate {}".format(radio_labels[radio_group.active])
    barplot.yaxis.formatter = NumeralTickFormatter(format='$ 0 a')
    barplot.vbar(x='MODE', width=0.5, bottom=0, top='y', source=bar_source)
    barplot.xaxis.major_label_orientation = pi/4
    barplot.xgrid.grid_line_color = None
    barplot.ygrid.grid_line_alpha = 0.6
    barplot.ygrid.grid_line_dash = [6,4]
    
    return barplot

def make_commodity_barplot(source):
    hover = HoverTool(tooltips=[('Total Value', '$@VALUE{0,0}'), ('Total Weight', '@WEIGHT{0,0} lbs'), ('Type Goods', '@SCTG')])
    barplot2 = figure(x_range=sorted(short_desc), y_range=DataRange1d(), plot_height=350, plot_width=1050, tools=[hover, BoxZoomTool(), ResetTool(), SaveTool()])
    barplot2.title.text = "Aggregate {} by Commodity".format(radio_labels[radio_group.active])
    barplot2.title.align = 'center'
    barplot2.title.text_font_size = '14pt'
    barplot2.xaxis.axis_label = "Commodity"
    barplot2.yaxis.axis_label = "Aggregate {}".format(radio_labels[radio_group.active])
    barplot2.yaxis.formatter = NumeralTickFormatter(format='$ 0 a')
    barplot2.vbar(x='Short', width=0.5, bottom=0, top='y', source=bar2_source)
    barplot2.xaxis.major_label_orientation = pi/4
    barplot2.xgrid.grid_line_color = None
    barplot2.ygrid.grid_line_alpha = 0.6
    barplot2.ygrid.grid_line_dash = [6,4]
    
    return barplot2

def make_chloropleth(source):
    hover = HoverTool(tooltips=[('State','@name'), ('Total Value', '$@values{0,0}'), ('Total Weight','@weights{0,0} lbs')])
    p = figure(title="Chloropleth Map of AK Trade Relationships", plot_width=1400, plot_height=700, tools=[hover])
    p.title.align = 'center'
    p.title.text_font_size = '14pt'
    p.patches('state_xs', 'state_ys', source=source, fill_color='colors', fill_alpha=0.5, line_color='black')
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.xaxis.axis_line_color = None
    p.yaxis.axis_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.xaxis.major_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = None
    p.xaxis[0].major_label_text_color = None
    p.yaxis[0].major_label_text_color = None
    p.background_fill_color = 'lightblue'
    
    return p
 

  
#Selection widgets
origin_select = MultiSelect(value=['AK'], title='Shipment Origin (State)', options=sorted(list(data.ORIG_STATE.unique())))
dest_select = MultiSelect(value=['AK'], title='Shipment Destination (State)', options=sorted(list(data.DEST_STATE.unique())))
mode_select = MultiSelect(value=sorted(list(data.MODE.unique())), title='Mode of Transportation', options=sorted(list(data.MODE.unique())))
sctg_select = MultiSelect(value=[sorted(list(data.SCTG.unique()))[0]], title='Type of Commodity', options=sorted(list(data.SCTG.unique())))
hazmat_select = MultiSelect(value=sorted(list(data.HAZMAT.unique())), title='HAZMAT', options=sorted(list(data.HAZMAT.unique())))
x_axis_select = Select(title='X Axis Value', value='Shipment Value (USD)', options=['Shipment Value (USD)', 'Shipment Weight (lbs)', 'Shipment Distance (mi)'])
y_axis_select = Select(title='Y Axis Value', value='Shipment Weight (lbs)', options=['Shipment Value (USD)', 'Shipment Weight (lbs)', 'Shipment Distance (mi)'])
radio_labels = ['VALUE', 'WEIGHT', 'COUNT']
radio_group = RadioButtonGroup(labels=radio_labels, active=0)

controls = [x_axis_select, y_axis_select, origin_select, dest_select,
            mode_select, sctg_select, hazmat_select]

for control in controls:
    control.on_change('value', lambda attr, old, new: make_source(data))
    



source = ColumnDataSource(data=dict(x=[], y=[], ORIG_STATE=[],
                                    DEST_STATE=[], MODE=[],
                                    HAZMAT=[], SCTG=[], SHIPMT_VALUE=[],
                                    SHIPMT_WGHT=[], SHIP_DIST_ROUTED=[]))

bar_source = ColumnDataSource(data=dict(MODE=[], y=[], COUNT=[], VALUE=[], WEIGHT=[]))
bar2_source = ColumnDataSource(data=dict(SCTG=[], y=[], COUNT=[], VALUE=[], WEIGHT=[], Short=[]))
chloro_source = ColumnDataSource(dict(state_xs=[], state_ys=[], name=[], values=[], weights=[], colors=[]))


widgets = widgetbox(*controls)

plot = make_scatter_plot(source)
barplot = make_barplot(bar_source)
barplot2 = make_commodity_barplot(bar2_source)
chloro = make_chloropleth(chloro_source)

make_source(data)

radio_group.on_change('active', lambda attr, old, new: make_source(data))


layout = column(row(widgets, plot, chloro), row(radio_group, barplot, barplot2))

curdoc().add_root(layout)
show(layout)         
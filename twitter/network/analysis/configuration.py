'''
VMP 2022-03-07: 
plot aesthetics 
'''

# imports 
import matplotlib.pyplot as plt 
import seaborn as sns 

# aesthetics
def plot_configuration(): 
    # gender colors 
    c_gender = {
        'Male': 'tab:blue', 
        'Female': 'tab:orange',
        'Unknown': 'tab:gray'}

    # query colors 
    c_bropenscience = {
        'node_color': "#ffbb00",
        'edge_color': "#ffcf4d"
    }

    # seaborn style 
    sns.set(style='ticks', font_scale=1.3)
    ms = 2 # marker 

    # for just one panel
    # figure(figsize=(11.69, 8.27)) -- for A4
    figsize = (4.5, 3.2)
    dpi = 300

    return ms, figsize, dpi, c_gender, c_bropenscience



from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

def Show_Schedule(Sequence):
    
    #Number of machines
    n_m = (Sequence.nunique()).loc['mid']
    #Dataframe of each machine with his task
    df_ms = dict(tuple(Sequence.groupby("mid")))
    #list of machines_id
    mls = Sequence['mid'].unique()
    
    horizon = (Sequence.max()).loc['end']
    
    plt.figure(figsize=(30, 20))
    
    ax = plt.gca().axes
    
    #add patch at position d and m
    
    for machine in range(n_m):
        for task in range(len(df_ms[mls[machine]])):
            if df_ms[mls[machine]].iloc[task,1] == 0:
                ax.add_patch(Rectangle((df_ms[mls[machine]].iloc[task,8]+.3,machine+.1),width=df_ms[mls[machine]].iloc[task,10],height=.8,color='cornflowerblue'))
                ax.add_patch(Rectangle((df_ms[mls[machine]].iloc[task,8]+.3,machine+.1),width=df_ms[mls[machine]].iloc[task,10],height=.8,fill=False,color='k'))
                order_id = '%i' %df_ms[mls[machine]].iloc[task,2]
                plt.text(df_ms[mls[machine]].iloc[task,8]+2, machine+.5, int(df_ms[mls[machine]].iloc[task,0]) , 
                                        horizontalalignment='center',
                                        verticalalignment='center')
            if df_ms[mls[machine]].iloc[task,1] == 1:
                ax.add_patch(Rectangle((df_ms[mls[machine]].iloc[task,8]+.3,machine+.1),width=df_ms[mls[machine]].iloc[task,10],height=.8,color='green'))
                ax.add_patch(Rectangle((df_ms[mls[machine]].iloc[task,8]+.3,machine+.1),width=df_ms[mls[machine]].iloc[task,10],height=.8,fill=False,color='k'))
                #plt.text(df_ms[mls[machine]].iloc[task,8]+1, machine+.5, "CIP", 
                                        #horizontalalignment='center',
                                        #verticalalignment='center')
                
    plt.yticks(np.arange(0, n_m)+.5, list(map(int, mls.tolist())))
    
    plt.xticks(np.arange(0, horizon, step=10))
    
    plt.xlim(0, horizon)
    
    plt.ylim(0, n_m)
    
    plt.gca().invert_yaxis()
    
    # remove borders and ticks
    
    plt.grid(b = True,color='gray', linestyle=':', linewidth=.5)
    for spine in plt.gca().spines.values():
    
        spine.set_visible(False)
    
    #plt.tick_params(top=False, bottom=False, left=False, right=False)
    font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 25}
    mpl.rc('font', **font)
    plt.ylabel('Machine_id')
    plt.xlabel('Time')
    plt.show()
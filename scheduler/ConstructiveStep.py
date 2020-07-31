
import pandas as pd
import numpy as np 

def Mduration_Calc_single(T_single,T_multi):
    # Create a list with the machines and the accumulated time already scheduled
    Machine_list = np.unique(np.concatenate((T_multi['mid'].unique(),
                                    T_single['mid'].unique()),axis=0))
    
    M_duration = pd.DataFrame({'mid':Machine_list,
                       'dt':np.zeros(len(Machine_list),dtype=int)})
    T_single = T_single.sort_values(by=['mid','stp']) 
    for task in range(len(T_single)):
        if (T_single.iloc[task,4] != T_single.iloc[task-1,4] or task == 0):
            machine = T_single.iloc[task-1,4]
            i_machine = M_duration.index[
                M_duration['mid'] == machine][0]
            M_duration.iloc[i_machine,1] = T_single[(
                                T_single.mid == machine)].loc[:,'dt'].sum()
    return M_duration

def Assign_multi_to_T(T_single,T_multi,M_duration):
    #selection of the best option for the multistage steps based on working time scheduled
    
    #list of tasks selected and tasks posible.
    Tselected = []
    Tpos = []    
    
    T_multi.sort_values(by=['tid','opt'])
    
    #make separate frames for each multistage task
    tunique = T_multi['tid'].unique()
    for tid in tunique:
        subT_multi = T_multi[(T_multi.tid == tid)]
        options = subT_multi['opt'].unique()
        munique = subT_multi['mid'].unique()
        horizon =    10000000
        for opt in options:
            
            optsubT = subT_multi[(subT_multi.opt == opt)]
            
            #Check the current option
            newM_duration = M_duration.copy(deep = True)
            for task in range(len(optsubT)):
                
                #update the M_duration list fir this option
                machine = optsubT.iloc[task,4]
                i_machine = M_duration.index[
                         M_duration['mid'] == machine][0]
                newM_duration.iloc[i_machine,1] += optsubT.iloc[task,10]
            
            # the feature check to decide with option is better: 
            # for all the machines it stores the horizon in between the
            # machines that can be decided for this option. This horizon is 
            # subhorizon and its charecteristic for each option
            horizon_option = 0
            for machine in munique:
                i_machine = M_duration.index[
                         M_duration['mid'] == machine][0]
                #store maximum
                if newM_duration.iloc[i_machine,1] > horizon_option:
                    horizon_option = newM_duration.iloc[i_machine,1]
                                       
            #new solution found. we store the option with less subhorizon
            if horizon_option < horizon:
                horizon = horizon_option
                bestM_duration = newM_duration
                setgoodtasks = optsubT
                
            
            #update the M_duration list and
            #append the set of tasks found to the T_single list when all the options are 
            #explored:
            if opt == options[-1] : 
                #information stored for the generative step
                Tselected.append([tid,setgoodtasks.iloc[0,12],setgoodtasks.iloc[0,3]])
                
                #update the problem with the option selected
                
                M_duration = bestM_duration
                for i in range(len(setgoodtasks)):
                    setgoodtasks.iloc[i,0] = setgoodtasks.iloc[i,13]
                
                del setgoodtasks['opt']
                del setgoodtasks['realtid']
                T_single = T_single.append(setgoodtasks)
                horizon = 10000000
            
            #creation of list of possible tasks
            fo = optsubT.iloc[0,3]
            Pos = np.array([tid,opt,fo,0])
            if len(Tpos) == 0:
                Tpos = Pos
            else:
                Tpos = np.vstack((Tpos,Pos))  
                
    T_single.sort_values(by=['ddt','stp'])
    T = T_single
    
    Tselected = np.array(Tselected)
    Tselected = pd.DataFrame(data=Tselected,columns=['tid','opt','foid'])
    Tpos = pd.DataFrame(data=Tpos,columns=['tid','opt','foid','R'])
    return T ,Tselected ,Tpos

def Contructivestep(T_single,T_multi):
    #constructive_step:
    if T_multi.empty != True:
        M_duration = Mduration_Calc_single(T_single,T_multi)
        [T,Tselected,Tpos] = Assign_multi_to_T(T_single,T_multi,M_duration)
    else:
        print('No Multistage detected with current machines. \n')
        print('No constructive step needed.')
        T = T_single
        Tselected = T_single
        Tpos = 0
    
    return T,Tselected,Tpos
    
            
    
    
            
       
            
            



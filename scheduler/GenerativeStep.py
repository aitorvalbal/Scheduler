import numpy as np
import random
import time
import pandas as pd

import scheduler.ModelSolver as ms
import scheduler.PostProcessing as post


def Evaluate(Sequence, weights ,oldhorizon,oldcost,oldmachinesused,oldhourslate,lasts_foid):
    #Evaluation of the sequence given t
    horizon = Sequence['end'].max()
    cost = Sequence['c'].sum()
    machinesused = len(Sequence['mid'].unique()) 
    hours_late = hourslate(Sequence,lasts_foid)
    print('actual hours late:', hours_late)
    print('old hours late:', oldhourslate)
    score = weights[0] * horizon/oldhorizon + weights[1] * cost/oldcost + weights[2]* (machinesused/oldmachinesused) + weights[3]*(hours_late/(oldhourslate))
    return score

def Weight_Norm(weights):
    #Weight normalization at the start of the proces
    weights = np.array(weights)
    if sum(weights) == 1:
        return weights
    else:
        weights = weights/sum(weights)
        return weights

def Solve_option(T,Ma,Subsequence,info,Fo):
    #Problem solver for each exploration
    Sequence = ms.Solveproblem(T,Subsequence,info,Ma,Fo)
    
    if info['cip_tasks']==1:
        [Sequence, model, horizon] = post.Add_Cip_to_solution(Sequence,Ma)
        Sequence = post.Second_Solver(Sequence,Subsequence,model,info,horizon)
    
    return Sequence

def Select_nodes(Tselected,Tpos, maxnodes,nodemem):
    #Selection of the nodes to explore
    
    tidunique = Tpos['tid'].unique()
    ListNodes = []
    
    for task in range(len(Tselected)): 
            tid = Tselected.iloc[task,0]
            opt = Tselected.iloc[task,1]
            
            Filter = 'tid!=' + str(tid) + '| opt!=' + str(opt) #Create the query 
            #Tpos contains the decisions that can be made
            Tpos = Tpos.query(Filter)
            
    pos_options = len(Tpos) #Number of options different to the previous solution
    if pos_options <= maxnodes:
        #pick all posible nodes
               
        #creation of diferent nodes 
        for option in range(len(Tpos)):
            nodeinfo = []
            tid = Tpos.iloc[option,0]
            opt = Tpos.iloc[option,1]
            lastopt = Tselected.query('tid == ' + str(tid))
            info = [tid,lastopt]
            Filter = 'tid!='+str(tid)
            node = Tselected.query(Filter)
            node = node.append(Tpos.iloc[option])
            node = node.sort_values(by=['tid'])
            nodeinfo.append(node)
            nodeinfo.append(info)
            
            ListNodes.append(nodeinfo)
        
    else: 
        #random number list for the option election following a half normal distribution
        
        randomlist = []
        for j in range(maxnodes):
            c=0
            while c==0:
                number = int(round(np.random.normal(pos_options-1,0.25*(pos_options-1))))
                if number >= pos_options:
                    number = number - 2*(number-(pos_options-1))
                if number >= 0:
                    if not number in randomlist:
                        c=1
                        randomlist.append(number)
                        
        Tpos = Tpos.sort_values(by=['R'])
        for option in randomlist:
            nodeinfo = []
            tid = Tpos.iloc[option,0]
            opt = Tpos.iloc[option,1]
            lastopt = Tselected.query('tid == ' + str(tid))
            info = [tid,lastopt.iloc[0,1],lastopt.iloc[0,2]]
            Filter = 'tid!='+str(tid)
            node = Tselected.query(Filter)
            node = node.append(Tpos.iloc[option])
            node = node.sort_values(by=['tid'])
            nodeinfo.append(node)
            nodeinfo.append(info)
            
            ListNodes.append(nodeinfo)
            
            
    #eliminate the nodes that have been already explored (Memory)
    if len(nodemem) > 0:
        ListNodesgood = []
        for node in ListNodes:
            c = 0
            noder = node[0]
            for nodeme in nodemem:
                if not (noder.values != nodeme.values).any():
                    c = 1
                    print('Found Explored node')
            if c == 0: ListNodesgood.append(node)
            
        ListNodes = ListNodesgood
        
    return ListNodes

def Calc_SetT(node,T_multi,T_single):
    #Calculus of the acutal T table node to explore.
    for option in range(len(node)):
        tid = node.iloc[option,0]
        opt = node.iloc[option,1]
        Filter = 'tid==' + str(tid) + '&opt==' + str(opt)
        setgoodtasks = T_multi.query(Filter)
        for i in range(len(setgoodtasks)):
                    setgoodtasks.iloc[i,0] = setgoodtasks.iloc[i,13]
        del setgoodtasks['opt']
        del setgoodtasks['realtid']
        T_single = T_single.append(setgoodtasks)
        
    T = T_single
    return T
def UpdateRewards (Rewards,score,T_multi,node):
    #Reward updating after explorations made based on the scores
    reward = (1-score)
    taskchanged = node[1]
    newtask = [node[1][0],node[0].query('tid ==' + str(taskchanged[0])).iloc[0,1]]
    
    #Know to which fo and ma we have went
    tid = node[1][0]
    opt = node[0].query('tid ==' + str(tid)).iloc[0,1]
    fo = T_multi.query('tid ==' +str(tid)+'& opt ==' +str(opt)).iloc[0,3]
    
    Rewards.loc[fo] += reward
    
    return Rewards

def Update_TposReward(Tpos,Rewards):
    #Update the reward asociated with the posibilities left.
    for i in range(len(Tpos)):
        fo = Tpos.iloc[i,2]
        Tpos.iloc[i,3] = Rewards.loc[fo]['R']       
                                                                
    return Tpos

def hourslate(Sequence,lasts_foid):    
    # Calculus of the penalization of the delay on the duw dates
    hourslate = 0    
    for foid in lasts_foid[1]:
        foid_Sequence = Sequence.query('foid=='+str(foid))
        for task in range(len(foid_Sequence)):
            end = foid_Sequence.iloc[task,9]
            ddt = foid_Sequence.iloc[task,11]
            if end > ddt:                
                hourslate += end-ddt        
    if hourslate == 0:
        hourslate = 1
    return hourslate

def Generative(Sequence,Tselected,Tpos,T_multi,Ma,T_single,info,Fo):
    #Main Reinforcement learning phase function
    weights = [info['weight_time'],info['weight_cost'],info['weight_machines'],info['weight_duedates']]
    weights = Weight_Norm(weights)
    maxnodes = info['explorations']
    c = 1; i = 0
    maxtime = info['max_total_time']
    start_time = time.time()
    #Rewards definition
    foid_unique = Fo['formula_id'].unique()
    Rewards = {'R':len(foid_unique)*[0.]}
    Rewards = pd.DataFrame(Rewards,index = foid_unique)
    #Node memory
    nodemem = []
    print('Exploring ', maxnodes, 'nodes each iteration')
    bestTselected = Tselected
    no_solcount = 0
    lasts_foid = ms.Last_step(Fo)
    while c==1: #and i <100:
        print('iteration ', i)
        
        
        oldhorizon = Sequence['end'].max()
        oldcost = Sequence['c'].sum()
        oldmachinesused = len(Sequence['mid'].unique())
        oldhourslate = hourslate(Sequence,lasts_foid)
        Tpos = Update_TposReward(Tpos,Rewards)
    
        ListNodes = Select_nodes(Tselected,Tpos, maxnodes,nodemem)
        ListSequences = []
        ListScores = []
        j = 0
        
        for node in ListNodes:
            
            T = Calc_SetT(node[0],T_multi,T_single)
            
            Subsequence = ms.Define_Subsequences(T,Fo) 
            Sequencetry = Solve_option(T,Ma,Subsequence,info,Fo)
            score = Evaluate(Sequencetry, weights, oldhorizon, oldcost,oldmachinesused,oldhourslate,lasts_foid)
            
            ListSequences.append(Sequencetry)
            ListScores.append(score)
            print('Explored node:',j,score)
            Rewards = UpdateRewards(Rewards,score,T_multi,node)
            j += 1
            nodemem.append(node[0])
        
        if min(ListScores) >= 1:
            print('No better solution found.')
            if no_solcount < 3:
                bestsol_index = ListScores.index(min(ListScores))
                Tselected = ListNodes[bestsol_index][0]
                no_solcount += 1
                print('keep exploring with a score:',min(ListScores))
            else : 
                print('Returning to the best sol found')
                Tselected = bestTselected
                no_solcount = 0
            if time.time()-start_time > maxtime:
                c = 0
                print('Time exceded. Time:',time.time()-start_time)
                print('Best solution:')
                print('Makespan:', Sequence['end'].max())
                print('Cost:', Sequence['c'].sum())
            i += 1
                
        else:
            print('Better solution found with a score:',min(ListScores),' .Keep exploring...')
            print('Current time:', time.time()-start_time)
            no_solcount = 0
            bestsol_index = ListScores.index(min(ListScores))
            Sequence = ListSequences[bestsol_index]
            Tselected = ListNodes[bestsol_index][0]
            bestTselected = Tselected
            print('Makespan:', Sequence['end'].max())
            print('Cost:', Sequence['c'].sum())
            print('Keep exploring...')
            if time.time()-start_time > maxtime:
                c = 0
                print('Time exceded. Time:',time.time()-start_time)
                print('Best solution:')
                print('Makespan:', Sequence['end'].max())
                print('Cost:', Sequence['c'].sum())
            i += 1
    Tselected = bestTselected    
    return Sequence,Tselected
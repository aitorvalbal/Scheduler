
import pandas as pd
import collections as cll
import numpy as np
import copy
import operator
from ortools.sat.python import cp_model

def AddvariablesfromT(model,T,horizon,M_info=pd.DataFrame(columns=['Empty'])):
    #Create model variables inside the T_single table
    for task in range(len(T)):
        #Create model variables for normal tasks:
        suffix = '_%i%i%i' % (T.iloc[task,2], T.iloc[task,7], T.iloc[task,0])
        start_var = model.NewIntVar(0, horizon, 'st' + suffix) #Create model variable
        end_var = model.NewIntVar(0, horizon, 'end' + suffix) #Create model variable
        T.iloc[task,8] = start_var
        T.iloc[task,9] = end_var
    
    return T

def Const_NoOverLap(T,model): 
    #Constraint definition of no overlap. The machines can only execute one task at a time
    machineinterval_list = []
    k = 0
    T = T.sort_values(by=['mid'])
    for task in range(len(T)):
        if (T.iloc[task,4]==T.iloc[task-1,4]):
            suffix = '_%i' % (k); k+=1
            interval_var = model.NewIntervalVar(T.iloc[task,8], int(T.iloc[task,10]), T.iloc[task,9],'interval'+ suffix )   
            machineinterval_list.append(interval_var)                                   
        else:  
            model.AddNoOverlap(machineinterval_list)
            machineinterval_list = []
            suffix = '_%i' % (k); k+=1
            interval_var = model.NewIntervalVar(T.iloc[task,8], int(T.iloc[task,10]), T.iloc[task,9],'interval'+ suffix )   
            machineinterval_list.append(interval_var)
            
    model.AddNoOverlap(machineinterval_list)        
    
    return model

def Define_Subsequences(T,Fo):
    #Subsequence Definition , Explained in detail inside the master thesis
    Subsequence = []
    oidunique = T['oid'].unique()
    for order in oidunique:
        oidT = T.query('oid==' + str(order))
        tinfo = [[]]
        i = 0
        oidT = oidT.sort_values(by=['stp'])
        laststep = oidT.iloc[0,7]
        for task in range(len(oidT)): 
            tid = [oidT.iloc[task,0]]
            q = oidT.iloc[task,5]
            step = oidT.iloc[task,7]
            if (laststep != step and task !=0) :
                tinfo.append([])
                i += 1
                tinfo[i].append([tid,q,1,1,1])
                laststep = step
            else:
                tinfo[i].append([tid,q,1,1,1])    
        #tinfo = [#each task has [tid,q,prepicked,postpicked,len(tid)]
        # tinfo fractioning into step to step dependencies.
        if len(tinfo) != 1:
               
            laststep = 0
            tinforel = []
            
            foidunique = oidT['foid'].unique()
            for foid in foidunique:
                foidFo = Fo.query('formula_id==' + str(foid))
                stp_pre = foidFo.iloc[0,3]
                step = foidFo.iloc[0,2]        
                if stp_pre != [0] and step != laststep:            
                    for (i,tiestp_pre) in enumerate(stp_pre):                
                        prestep = copy.deepcopy(tinfo[stp_pre[i]-1])
                        poststep = copy.deepcopy(tinfo[step-1])                
                        tinforel.append([prestep,poststep])
                    
                    
                    
                laststep = step 
                    
            #Define Subsequences 
            for tinfo in tinforel :
                step = 0
                j = 0
                c = 1
                while c == 1:
                    #order first les tasks implicated(len) and then more quantity
                    tinfo[step] = sorted(tinfo[step] , key=operator.itemgetter(1),reverse = True)
                    tinfo[step] = sorted(tinfo[step] , key=operator.itemgetter(4),reverse = False)
                    #order for the [-] search. Less quantity first
                    tinfo[step+1].sort(key=operator.itemgetter(1),reverse = True)
                    #pick next task
                    j = 0
                    
                    while tinfo[step][j][1] == 0:
                        j += 1
                        
                    task = tinfo[step][j]
                    quantity = task[1]
                    
                    result = -1
                     
                    # [-] search 
                    minustasks = []
                    plustask = task[0]
                    alpha = 0;beta = 0
                    for i,nextsteptask in enumerate(tinfo[step+1]):
                        if nextsteptask[2] == 1:#filter the candidates to choose from
                            result = quantity-nextsteptask[1]            
                            if result > 0:
                                posiblesol = plustask; bestresult = result
                                if alpha !=2 : 
                                    for l,postask in enumerate(tinfo[step]):
                                        if postask[3] == 1:                                
                                            quantity = postask[1]
                                            result = quantity-nextsteptask[1]                                
                                            if result >= 0 and result<bestresult:
                                                posiblesol = postask[0]
                                                bestresult = result
                                                bestask = postask                                    
                                                j = l
                                                task = postask
                                                if result == 0:                                                                        
                                                    task = bestask 
                                                    alpha = 1
                                                    break
                                            elif result<0: 
                                                alpha = 2
                                                quantity= task[1]
                                                break
                                plustask = posiblesol                
                                result = quantity-nextsteptask[1]
                                minustasks.append(nextsteptask[0])
                                tinfo[step+1][i][2] = 0
                                quantity = result 
                                if alpha == 1: break 
                            elif result == 0:
                                minustasks.append(nextsteptask[0])
                                quantity = result
                                tinfo[step+1][i][2] = 0
                                break  
                            else: 
                                bestresult= float('inf')
                                posiblesol = plustask
                                originaltask = task
                                for l,postask in enumerate(tinfo[step]):                        
                                    if postask[3] == 1 and postask[4] > originaltask[4]:                            
                                        quantity = postask[1]
                                        result = quantity-nextsteptask[1]                            
                                        if result >= 0 and result<=bestresult:
                                            posiblesol = postask[0]
                                            bestresult = result
                                            bestask = postask
                                            j = l
                                            task = postask
                                            beta = 3
                                            if result == 0:                                  
                                                beta = 1
                                                break
                                        else: 
                                            beta = 2
                                            quantity= task[1]
                                            
                                if beta == 1 or beta == 3:
                                    plustask = posiblesol  
                                    minustasks.append(nextsteptask[0])
                                    tinfo[step+1][i][2] = 0
                                    quantity = result
                                    break 
                                
                    if len(minustasks) !=0:            
                            tinfo[step][j][1] = quantity; tinfo[step][j][3] = 0 #update leftover and picked              
                            if len(minustasks)==1:Subsequence.append([plustask,minustasks[0]]) #store subsequence if found
                            if len(minustasks)>1:Subsequence.append([plustask,minustasks])
                            #check if the subsequence is done
                           
                            for checktasks in tinfo[step+1]:
                                c = 0
                                if checktasks[2] == 1:
                                    c = 1
                                    break
                                
                    else: #Create new task as the sum of the output from others.
                        # [+] search
                        tinfo[step] = sorted(tinfo[step] , key=operator.itemgetter(1),reverse = True)
                        #•tinfo[step] = sorted(tinfo[step] , key=operator.itemgetter(4),reverse = False)
                        #tinfo[step].sort(key=operator.itemgetter(3, 4, 1))
                        for k,samesteptask in enumerate(tinfo[step]):
                            if (samesteptask[1] > 0 and (samesteptask[0] != task[0])):#.any()):
                                if type(samesteptask[0]) == list : plustask = plustask + samesteptask[0]
                                else :  plustask.append(samesteptask[0])
                                tinfo[step].append([plustask,task[1]+tinfo[step][k][1],1,1,len(plustask)])
                                task[1] = 0;task[3] = 0; tinfo[step][k][1]=0; tinfo[step][k][3] = 0
                                break    
    return Subsequence

def Const_Precedence(T,model,Subsequence):
    #Precedence constraint definition with the Subsequences defined.
    for j in Subsequence: 
        Subsequencelist = pd.DataFrame()
        numpretask = len(j[0])
        numpostask = len(j[1])
        for k in j : 
            if len(k) == 1:
                Filter = 'tid==' + str(k[0])
                Subsequencelist = Subsequencelist.append(T.query(Filter))
            else: 
                for i in k:
                    Filter = 'tid==' + str(i)
                    Subsequencelist = Subsequencelist.append(T.query(Filter))                
        if numpretask == 1:
            for z in range(numpostask):  
                model.Add(Subsequencelist.iloc[0,9] <= Subsequencelist.iloc[z+1,8])                    
        else:
            for z in range(numpretask):
                model.Add(Subsequencelist.iloc[z,9] <= Subsequencelist.iloc[numpretask,8])
                        
        
    return model
    
def Const_DueDate(T,model, Ma, Fo):
    #Due date constraint definition
    #It contains the necessary correction of the expected cip task delay introduced
    T = T.sort_values(by=['oid','stp','cip','q'])
    machine_unique = T['mid'].unique()
    wt_list = [[],[],[]]
    wt_list[0].append(machine_unique)
    for machine in machine_unique:
        subT_mid = T.query('mid=='+str(machine))
        subMa = Ma.query('machine_id=='+str(machine))
        wt_acumm = subT_mid['dt'].sum()
        wt_cipp = (np.floor(wt_acumm/subMa.iloc[0,3]))*subMa.iloc[0,1]
        wt_list[1].append(wt_cipp) 
        wt_list[2].append(wt_acumm)
    #wt_list == [listmachines,wt_cipps,wt_tasks]
    
    lasts_foid = Last_step(Fo) #last foid for each product
    critical_foid = [item for sublist in lasts_foid[1] for item in sublist]
    for machine in machine_unique:
        subT_mid = T.query('mid=='+str(machine))
        subMa = Ma.query('machine_id=='+str(machine))
        lastfoid = 0
        for task in range(len(subT_mid)):
            foid = subT_mid.iloc[task,3]
            if foid in critical_foid:#only do the ddt correction with the lasts steps(lasts foids)
                if foid !=lastfoid :#no need to calculate again the correction f the foid is the same as the last calculated
                    prestepmach = [-1]
                    machine_list = Previous_machines(foid,Fo)#for this foid which are the machines implicated and the step they fullfill and are precedented
                    machine_list.sort(key=Maxsecondelement)
                    
                    machine_list_good = []
                    for mach in wt_list[0][0]:
                        c = 0
                        for mach2 in machine_list:
                            if mach == mach2[0]:
                                machine_list_good.append(mach2)
                                break
                    machine_list = machine_list_good
                    
                    wt_cipp = 0 ; wt_stored = -1; branches_list = []; wt_total_stored = -1
                    for i,premach in enumerate(machine_list):#premach [machine,[step],[presteps]]             
                        
                        
                        index = wt_list[0][0].tolist().index(premach[0])                            
                        wt_cippnow = wt_list[1][index];wt_cipp = 0
                        wt_task = wt_list[2][index]
                        if (i+1) != len(machine_list):
                            #update wt_cipp for multitask steps
                            if prestepmach == premach[1] or premach[1] == machine_list[i+1][1]:
                                if wt_cippnow + subT_mid['dt'].sum() > wt_total_stored:
                                    wt_stored = wt_cippnow
                                    wt_total_stored = wt_cippnow + subT_mid['dt'].sum()
                                if prestepmach == premach[1] and premach[1] != machine_list[i+1][1]:
                                    wt_cipp = wt_stored
                                    wt_stored = -1; wt_total_stored = -1                           
                            else:
                                wt_cipp = wt_cippnow                                
                            #update the branches list
                            if premach[1] != machine_list[i+1][1]:                                
                                #creation of new branch
                                if premach[2] == [0] :
                                    
                                    branches_list.append([premach[1][0],wt_cipp,wt_task])
                                #update branch
                                else: 
                                    if len(premach[2]) == 1:                                        
                                        for i,branch in enumerate(branches_list):
                                            if len(premach[2]) == 1:
                                                if branch[0]==premach[2][0]:
                                                    branches_list[i][1] += wt_cipp
                                                    branches_list[i][0] = premach[1][0]
                                                    branches_list[i][2] = wt_task
                                                    
                                    else:#junction of branches
                                        wt_junction = 0; wt_time_junction_stored = -1
                                        
                                        for prebranches in premach[2]: 
                                            for i, branch in enumerate(branches_list):
                                                if prebranches == branch[0]:
                                                    
                                                    if branch[1]+branch[2] > wt_time_junction_stored:
                                                        wt_junction = branch[1]   
                                                        wt_time_junction_stored = branch[1]+branch[2]                                                         
                                        branches_list.append([premach[1][0],wt_cipp+wt_junction,wt_task])                                                                                                                                
                            prestepmach = premach[1]
                            
                        else:#last machine, it needs to regroup branches 
                            if len(premach[2]) == 1:                                        
                                    for i,branch in enumerate(branches_list):
                                            if branch[0]==premach[2][0]:
                                                branches_list[i][1] += wt_cippnow
                                                branches_list[i][0] = premach[1][0]
                                                branches_list[i][2] = wt_task
                            else:#junction of branches
                                wt_junction = 0; wt_time_junction_stored = -1
                                
                                for prebranches in premach[2]: 
                                    for i, branch in enumerate(branches_list):
                                        if prebranches == branch[0]:
                                            
                                            if branch[1]+branch[2] > wt_time_junction_stored:
                                                wt_junction = branch[1]   
                                                wt_time_junction_stored = branch[1]+branch[2]
                                branches_list.append([premach[1][0],wt_cippnow+wt_junction,wt_task])
                   
                    
                    wt_cipp = branches_list[-1][1]
                    lastfoid = foid
                                
                realddt = int(subT_mid.iloc[task,11]-wt_cipp)
                model.Add(subT_mid.iloc[task,9] <= realddt)
        
    return model

def Maxsecondelement(elem):
    #Key function for sorting 
    return max(elem[2])

def Last_step(Fo):
    #Function to calculate the last step that completes a product
    prd_unique = Fo['product_id'].unique()
    lasts_foid = []
    lasts_foid.append(list(prd_unique))
    lasts_foid.append([])
    for prod in prd_unique:
        subprod = Fo.query('product_id=='+str(prod))
        stp_unique = subprod['step'].unique()
        for stp in stp_unique:
            c = 0
            lasts = []
            for search in range(len(subprod)):
                stp_pre = subprod.iloc[search,3]
                for step_pre in stp_pre:
                    if step_pre == stp:
                        c = 1
                        break
            if c == 0:
                lasts.append(stp)
        subprodstp = subprod.query('step ==' +str(lasts))
        stp = subprodstp['formula_id'].unique()
        lasts_foid[1].append(list(stp))
        
    return lasts_foid #list [[productlist],[[lastfoid for prod 1],[lastfoid for prod2]]]

def Previous_machines(foid,Fo):
    #From a given fo_id calculate all the previous machines implicated necessary with the production of the product.
    subfo = Fo.query('formula_id=='+str(foid))
    stp_pre = subfo.iloc[0,3]
    prod = subfo.iloc[0,1]
    machine = subfo.iloc[0,4]
    subprod = Fo.query('product_id=='+str(prod))
    c = 0
    machine_list = []
    machine_list.append(machine)
    stp_pre_list = []
    stp_pre_list.append(stp_pre)
    while c == 0:
        for sp in stp_pre_list:
            subfo = subprod.query('step == ' + str(sp))
            stp_pre_list_next = []
            for task in range(len(subfo)): 
                machine = subfo.iloc[task,4]
                machine_list.append(machine)
                stp_pre = subfo.iloc[task,3]
                stp_pre_list_next.append(stp_pre)
        
        stp_pre_list = stp_pre_list_next
        if all(i == 0 for i in stp_pre_list):
            c = 1
            
    machine_list = list(set(machine_list))#list uniques machines implicated
    machine_list_good = []
    for machine in machine_list:
        submach = subprod.query('machine_id=='+str(machine))
        steps = []
        for task in range(len(submach)):
            steps.append(submach.iloc[task,2])
            steps_pre = submach.iloc[task,3]
            machine_list_good.append([machine,steps,steps_pre])
    machine_list = machine_list_good
    return machine_list #[[machine,[step],[steps_pre]]

def Const_Machine_Precedence(T,model):
    #Constraint of precedence inside a machine. Used on the second solver.
    #Way to store the important information calculated on the first solver.
    Machine_list = T['mid'].unique()
    tasksche = -1
    for i, machine in enumerate(Machine_list):
        Filter = 'mid ==' + str(machine)
        Sequencemach = T.query(Filter) 
        tasksche += 1
        for task in range(len(Sequencemach)-1):
            model.Add(T.iloc[tasksche,9] <= T.iloc[tasksche+1,8])
            tasksche += 1
            
    return model

def Solver(T,model,time,horizon):
    #Creation of minimizing function
    
    T = T.astype({"ddt": int})
    
    #Objective of less time
    J1 = model.NewIntVar(0,horizon,'J1')
    model.AddMaxEquality(J1, [T.iloc[task,9] for task in range(len(T))])
    
    #function to minimize
    model.Minimize(J1)
    
    # Solve model.
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time
    status = solver.Solve(model)
    if status == 3:
        end_horizon = 0 ; Sequence = 0; model = 0
    else:
        end_horizon = solver.Value(J1)
        Sequence = pd.DataFrame(columns=['tid', 'cip', 'oid', 'foid', 'mid', 
                                  'q', 'c','stp', 'st', 'end',
                                  'dt', 'ddt'])
        
               
        for task in range(len(T)):
            Sequence = Sequence.append({
                            'tid': T.iloc[task,0], 
                            'cip':T.iloc[task,1],
                            'oid': T.iloc[task,2], 
                            'foid':T.iloc[task,3],
                            'mid':T.iloc[task,4],
                            'q':T.iloc[task,5],
                            'c': T.iloc[task,6],
                            'stp': T.iloc[task,7],
                            'st':solver.Value(T.iloc[task,8]),
                            'end':solver.Value(T.iloc[task,9]),
                            'dt': T.iloc[task,10],                            
                            'ddt':T.iloc[task,11] }, ignore_index=True)
        Sequence = Sequence.sort_values(by=['mid','st'])
        
    
    
    
    return status,end_horizon,Sequence,model

def Solveproblem(T,Subsequence,info,Ma,Fo):
    #Mmain function to solve the probelm
    model = cp_model.CpModel()
    horizon =  int(T['ddt'].max())
    Tsol = AddvariablesfromT(model,T,horizon)
    model = Const_NoOverLap(Tsol,model)
    model = Const_Precedence(Tsol, model,Subsequence)
    model = Const_DueDate(Tsol,model,Ma,Fo)
    time = info['max_time_solver']
    [status,end_horizon,Sequence,model] = Solver(Tsol,model,time,horizon)
    if status == 3:
        print('Problem not feasible. Eliminating due date constraints')
        model2 = cp_model.CpModel()
        horizon = int(T['dt'].sum())
        Tsol2 = AddvariablesfromT(model2,T,horizon)
        model2 = Const_NoOverLap(Tsol2,model2)
        model2 = Const_Precedence(Tsol2, model2,Subsequence)
        [status,end_horizon,Sequence,model] = Solver(Tsol2,model2,time,horizon)
        if status == 2:
            print('Feasible Solution Found')
        if status == 4:
            print('Optimal Solution Found')
        if status == 3:
            print('Problem not feasible. Problem error')
    else:
        if status == 2:
            print('Feasible Solution Found')
        if status == 4:
            print('Optimal Solution Found')
            
    return Sequence
    
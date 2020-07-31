
from ortools.sat.python import cp_model
import scheduler.ModelSolver as ms
import pandas as pd

def Add_Cip(model,Sequence,Ma,horizon):
    #Add cip to the solution with already model variables
    T = pd.DataFrame(columns=['tid', 'cip', 'oid','foid', 'mid', 
                              'q', 'c','stp', 'st', 'end',
                              'dt', 'ddt'])
    z = max(Sequence['tid'])+1
    Machine_list = Sequence['mid'].unique()
    for i, machine in enumerate(Machine_list):
        solution = Sequence.query('mid =='+str(machine))
        clean_every = Ma.iloc[i,3]
        acumm = 0
        for task in range(len(solution)):
            acumm += solution.iloc[task,10]
            if acumm == clean_every:
                T = T.append(solution.iloc[task])
                suffix = '_%i_%i' % (solution.iloc[task,2], z)
                T = T.append({'tid': z, 
                              'cip':1,
                              'oid': z,
                              'foid':0,
                              'mid':machine,
                              'q': int(1) ,
                              'c': int(Ma.iloc[i,2]),
                              'stp': 1,
                              'st': model.NewIntVar(0, horizon, 'st' + suffix),
                              'end': model.NewIntVar(0, horizon, 'end' + suffix),
                              'dt': Ma.iloc[i,1],
                              'ddt': horizon }, ignore_index=True)
                z += 1; acumm = 0
            elif acumm > clean_every:
                suffix = '_%i_%i' % (solution.iloc[task,2], z)
                T = T.append({'tid': z, 
                              'cip':1,
                              'oid': z,
                              'foid':0,
                              'mid':machine,
                              'q': int(1) ,
                              'c': int(Ma.iloc[i,2]),
                              'stp': 1,
                              'st': model.NewIntVar(0, horizon, 'st' + suffix),
                              'end': model.NewIntVar(0, horizon, 'end' + suffix),
                              'dt': Ma.iloc[i,1],
                              'ddt': horizon }, ignore_index=True)
                z += 1; acumm = 0
                T = T.append(solution.iloc[task])
                acumm += solution.iloc[task,10]
            else:
                T = T.append(solution.iloc[task])
                
    return T

def Add_Cip_to_solution(Sequence,Ma):    
    #Full function to declare the cip task already with ortools model variables
    Sequence = Sequence.set_index(pd.Series(list(range(len(Sequence)))))
    makespan = Sequence['end'].max()
    horizon = int(makespan+(makespan/Ma['clean_every_list'].min())*Ma['clean_delay'].max())
    model = cp_model.CpModel()
    Sequence = ms.AddvariablesfromT(model,Sequence,horizon)
    Sequence = Add_Cip(model,Sequence,Ma,horizon)
    return Sequence, model, horizon

def Second_Solver(Sequence,Subsequence,model,info,horizon):
    #Second solver call
    model = ms.Const_NoOverLap(Sequence,model)
    model = ms.Const_Precedence(Sequence,model,Subsequence)
    model = ms.Const_Machine_Precedence(Sequence,model)#Note this extra constraint
    time = info['max_time_solver']
    [status,end_horizon,Sequence,model] = ms.Solver(Sequence,model,time,horizon)
    return Sequence
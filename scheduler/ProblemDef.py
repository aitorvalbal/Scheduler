import pandas as pd

import scheduler.JsonTools as jsont
import scheduler.ProblemProcessing as pp
import scheduler.ConstructiveStep as cs
import scheduler.ModelSolver as ms
import scheduler.PostProcessing as post
import scheduler.GenerativeStep as gs
import scheduler.WorkersProcessing as wp
import scheduler.SchedulePlot as sp

class Problem:
    #basic info exported from json format with the initialization
    def __init__(self,data,form):
        #Extract info from .json files:
        if form == 'json' :
            [fo, ma, orders, mastate, info, workers, shifts] = jsont.Import_Json(data)
            self.fo = fo
            self.ma = ma
            self.orders = orders
            self.mastate = mastate
            self.info = info
            self.workers = workers
            self.shifts = shifts
        #Extract info from raw data (API application)
        if form == 'raw' :
            [fo, ma, orders, mastate, info, workers, shifts] = jsont.Import_Json_from_request(data)
            self.fo = fo
            self.ma = ma
            self.orders = orders
            self.mastate = mastate
            self.info = info
            self.workers = workers
            self.shifts = shifts

    #Problem Parameters that have to be stored and initialized first:
    Sequence =  pd.DataFrame(columns=['tid', 'cip', 'oid','foid', 'mid', 
                              'q', 'c','stp', 'st', 'end',
                              'dt', 'ddt'])
    T_single = pd.DataFrame(columns=['tid', 'cip', 'oid','foid','mid', 
                              'q', 'c','stp', 'st', 'end',
                              'dt','ddt'])
    T_multi = pd.DataFrame(columns=['tid', 'cip', 'oid', 'foid','mid', 
                              'q', 'c','stp', 'st', 'end',
                              'dt','ddt','opt','realtid'])
    
    T = pd.DataFrame(columns=['tid', 'cip', 'oid','foid', 'mid', 
                              'q', 'c','stp', 'st', 'end',
                              'dt', 'ddt'])
    Workers_Schedule = pd.DataFrame(columns=['worker_id','machine_id','shift_id'])
    Tselected = []
    Tpos = []
    Subsequence = []
    
    #Intermidiate methods
    def Encoding(self):
        #from the basic info to the T_single,T_multi, Ma list
        [self.T_single, self.T_multi, self.ma,self.fo] = pp.Encoding(self.fo,
                                                             self.ma,
                                                             self.mastate,
                                                             self.orders,
                                                             self.workers,
                                                             self.info,
                                                             self.shifts)
    def Constructive_step(self):
        #Select the T_multi tasks and form the definitive T
        [self.T,self.Tselected,self.Tpos] = cs.Contructivestep(self.T_single,self.T_multi)
    def Solve_Problem(self):
        #Subsequence definition and constraint problem solver with ortools
        self.Subsequence = ms.Define_Subsequences(self.T,self.fo)     
        self.Sequence = ms.Solveproblem(self.T,self.Subsequence,self.info,self.ma,self.fo)
    def Add_Cip(self):
        #If enabled, add cipp to the solution and solve a second problem to optimize solution further
        if self.info['cip_tasks'] == 1:
            [self.Sequence, model,horizon] = post.Add_Cip_to_solution(self.Sequence,self.ma)
            self.Sequence = post.Second_Solver(self.Sequence,self.Subsequence,model,self.info,horizon)    
    def Main_Scheduler(self):
        #Solve problem instance once
        self.Encoding()
        self.Constructive_step()
        self.Solve_Problem()
        if self.info['cip_tasks'] == 1:
            self.Add_Cipp()
    def Generative(self):
        #Reinforcement learning phase
        [self.Sequence,self.Tselected] = gs.Generative(self.Sequence,
                                                       self.Tselected,
                                                       self.Tpos,
                                                       self.T_multi,
                                                       self.ma,
                                                       self.T_single,
                                                       self.info,
                                                       self.fo)    
    def Workers_Assignation(self):
        #Workers scheduler
        self.Workers_Schedule = wp.WorkersScheduler(self.ma,self.workers,self.Sequence,self.shifts)     
    #Main methods
    def Graphic_Sequence(self):
        sp.Show_Schedule(self.Sequence)    
    def Return_json(self):
        del self.Sequence['dt']
        del self.Sequence['ddt']
        Solution = jsont.Create_Json_Solution(self.Sequence,self.Workers_Schedule,self.info)
        return Solution    
    def Scheduler(self):
        self.Encoding()
        if type(self.T_single) == int:
            print('Problem not Feasible')
        else : 
            self.Constructive_step()
            self.Solve_Problem()
            self.Add_Cip()
            if len(self.T_multi)==0:
                print('No Reinforcement Learning needed')
            else: 
                self.Generative()
            
            if self.info['workers'] == 1:
                self.Workers_Assignation()
            else:
                self.Workers_Schedule = 0
        


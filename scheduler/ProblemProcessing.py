
import datetime as dt
import pandas as pd
import numpy as np
    
def Tlist_Calc(Fo,Or,shifts):
    #Creation of the T_single table ( list of necessary task to fulfill the orders)
    #And creation of the multinfo list which contains the multistage steps info required
    T_single = pd.DataFrame(columns=['tid', 'cip', 'oid', 'foid', 'mid', 
                                  'q', 'c','stp', 'st', 'end',
                                  'dt','ddt'])   
    multinfo = []
    tid = 0
    
    for order in range(len(Or)):
        
        #Calculus of the delivery date and creation date for the order
        dd = Calculus_dd(Or,order,shifts)
        
        Fo = Fo.sort_values(by=['product_id','step','max_output'],
                            ascending=[True,True,False])
        
        for formula in range(len(Fo)):
            if Or.iloc[order,3] == Fo.iloc[formula,1]: #check if the formula containts the product
                multi = Multistage_detection(Fo, formula)
                if multi == False:
                    n_full = int(np.floor(Or.iloc[order,2]/Fo.iloc[formula,6]))
                    for i in range(n_full):
                        T_single = T_single.append({
                                    'tid': tid, 
                                    'cip':0,
                                    'oid': Or.iloc[order,0], 
                                    'foid':Fo.iloc[formula,0],
                                    'mid':Fo.iloc[formula,4],
                                    'q':Fo.iloc[formula,6],
                                    'c': Fo.iloc[formula,8],
                                    'stp': Fo.iloc[formula,2],
                                    'st':0,
                                    'end':0,
                                    'dt': Fo.iloc[formula,7],                                
                                    'ddt':dd }, ignore_index=True)
                        tid += 1
                    
                    #Calculous of the last task quantity
                    q = Or.iloc[order,2]%Fo.iloc[formula,6]
                    
                    if q != 0:
                        if Fo.iloc[formula,5] == 1:
                            dt = (Fo.iloc[formula,7]/Fo.iloc[formula,6])*q
                            c = (Fo.iloc[formula,8]/Fo.iloc[formula,6])*q
                        if Fo.iloc[formula,5] == 2:
                            dt = Fo.iloc[formula,7]
                            c = Fo.iloc[formula,8]
                        T_single = T_single.append({
                                    'tid': tid, 
                                    'cip':0,
                                    'oid': Or.iloc[order,0],
                                    'foid':Fo.iloc[formula,0],
                                    'mid':Fo.iloc[formula,4],
                                    'q': q,
                                    'c': c,
                                    'stp': Fo.iloc[formula,2],
                                    'st':0,
                                    'end':0,
                                    'dt':int(np.ceil(dt)),
                                    'ddt':dd }, ignore_index=True)  
                        tid += 1
                    #pr_multi = multi
                #creation of multitasks they need to have the same tid in order
                #to know that in the list are options and need to be filtrated
                if multi == True:
                    if len(multinfo) != 0:
                        if multinfo[-1][3] == Fo.iloc[formula,2] and multinfo[-1][2] == Or.iloc[order,0]:
                            multinfo[-1][0].append(Fo.iloc[formula,0])
                        else:
                            multinfo.append([[Fo.iloc[formula,0]],
                                          Or.iloc[order,2],
                                          Or.iloc[order,0],
                                          Fo.iloc[formula,2],
                                          dd])
                    else: 
                        multinfo.append([[Fo.iloc[formula,0]],
                                          Or.iloc[order,2],
                                          Or.iloc[order,0],
                                          Fo.iloc[formula,2],
                                          dd])
                    
    #multinfo = [list of foid,q,oid,stp]
    T_single = T_single.sort_values(by=['oid','stp'])
    return T_single,multinfo

def Calculus_dd(Or,order,shifts):
    #contar els dies que no estan en el shifts ( diumenges i tal)
    
    today = dt.datetime.today()
    del_date = dt.datetime.strptime(Or.iloc[order,1], '%Y-%m-%d')
    dd = del_date-today   
    days = dd.days +1
    
    
    unique_days = shifts['day_of_the_week'].to_list()
    unique_days = list(dict.fromkeys(unique_days))
    full_days_list = [1,2,3,4,5,6,7]
    nonworker_days = list(set(full_days_list) - set(unique_days))
    
    first_weekday = today.weekday()+2
    
    if first_weekday in nonworker_days:
        while first_weekday in nonworker_days:
            if first_weekday == 7:
                first_weekday = 1
                days -= 1
            else:
                first_weekday += 1
                days -= 1
    
    shift_index = shifts.query('day_of_the_week=='+str(first_weekday)).index[0]
    
    next_day = first_weekday
    last_day = 0; acumulated_days = 0
    acumulated_hours = 0
    while days > acumulated_days: 
       acumulated_hours += shifts.iloc[shift_index,3] - shifts.iloc[shift_index,2]
       
       # index jump
       shift_index += 1       
       if shift_index > len(shifts)-1:
           shift_index = 0     
           
       #day calculus( note the previous index jump)
       actual_day = shifts.iloc[shift_index,1]
       if actual_day != last_day: #if the next shift will happen on a diferent day
           next_day += 1 #Know which day will be next
             
           if next_day in nonworker_days: # if the next day is not a working day we need to find the next workind day counting the days that the plant will not work
              while next_day in nonworker_days : 
                 if next_day == 7:
                     next_day = 1
                 else:
                     next_day += 1
                 acumulated_days += 1
              acumulated_days += 1
           else: 
              acumulated_days += 1
       else: 
           print('same shift days')
       last_day = actual_day
       
                  
    dd = acumulated_hours
    
    return dd

def Multistage_detection(Fo,index):
    #Formulas: full list of the formula
    #index: position on the list to know if its multistage
    #Check if the step, product and formula of its surroundings is the same
    if index == 0:
        if (Fo.iloc[index,1]==Fo.iloc[index+1,1] and
            Fo.iloc[index,2]==Fo.iloc[index+1,2]):
            multi = True
            # while (Fo.iloc[index,1]==Fo.iloc[index+1,1] and
            #        Fo.iloc[index,7]==Fo.iloc[index+1,7] and
            #        Fo.iloc[index,0]==Fo.iloc[index+1,0]):
            #     index += 1
            #     c += 1
        else:
            multi = False
    elif index == len(Fo)-1:
        if (Fo.iloc[index,1]==Fo.iloc[index-1,1] and
            Fo.iloc[index,2]==Fo.iloc[index-1,2]):
            multi = True
        else:
            multi = False
    else:
        if ((Fo.iloc[index,1]==Fo.iloc[index-1,1]  or 
             Fo.iloc[index,1]==Fo.iloc[index+1,1]) and
           (Fo.iloc[index,2]==Fo.iloc[index-1,2]   or 
            Fo.iloc[index,2]==Fo.iloc[index+1,2])):
            multi = True
            # while (Fo.iloc[index,1]==Fo.iloc[index+1,1] and
            #        Fo.iloc[index,6]==Fo.iloc[index+1,6]):
            #     index += 1
            #     c += 1
        else:
            multi = False
    
    #multi is true when the index of the list Fo is multistage
    return multi

def Add_Dependencies_multi(multinfo,Fo,T_single):
    #Takes the multinfo information and creates the T_multi table
    #T_multi table contains all the alternatives posible to perform the multistage steps
    T_multi = pd.DataFrame(columns=['tid', 'cip', 'oid', 'foid', 'mid', 
                              'q', 'c','stp', 'st', 'end',
                              'dt', 'ddt','opt','realtid'])
    tid = T_single['tid'].max() + 1
    realtid = tid
    for multitask in multinfo:
        foinfo = Fo.query('formula_id=='+str(multitask[0]))
        q = foinfo.max_output.max()
        totalq = multitask[1]
        #Add option of max output in one machine or the other
        acumqor = 0
        while acumqor != totalq: 
            #calculous of the next q of the set of tasks.
            if totalq-acumqor<q:
                q = totalq-acumqor
            opt = 1
            for formula in range(len(foinfo)):
                acumqt = 0
                max_output = foinfo.iloc[formula,6]
                while acumqt != q:                
                    #full tasks
                    if ((q-acumqt)-max_output)>=0:
                       #Calculus of dt and c with the type of formula:   
                        if foinfo.iloc[formula,5] == 1:
                            dt = (foinfo.iloc[formula,7]/foinfo.iloc[formula,6])*max_output
                            c = (foinfo.iloc[formula,8]/foinfo.iloc[formula,6])*max_output
                        if foinfo.iloc[formula,5] == 2:
                            dt = foinfo.iloc[formula,7]
                            c = foinfo.iloc[formula,8]
                        T_multi = T_multi.append({
                                         'tid': tid, 
                                         'cip':0,
                                         'oid': multitask[2],
                                         'foid':foinfo.iloc[formula,0],
                                         'mid':foinfo.iloc[formula,4],
                                         'q': max_output,
                                         'c': c,
                                         'stp': foinfo.iloc[formula,2],
                                         'st':0,
                                         'end':0,
                                         'dt':np.ceil(dt),
                                         'ddt': multitask[4],
                                         'opt': opt,
                                         'realtid':realtid}, ignore_index=True)
                        acumqt += max_output
                        realtid += 1
                    #No full tasks
                    else: 
                        if foinfo.iloc[formula,5] == 1:
                            dt = (foinfo.iloc[formula,7]/foinfo.iloc[formula,6])*(q-acumqt)
                            c = (foinfo.iloc[formula,8]/foinfo.iloc[formula,6])*(q-acumqt)
                        if foinfo.iloc[formula,5] == 2:
                            dt = foinfo.iloc[formula,7]
                            c = foinfo.iloc[formula,8]
                        T_multi = T_multi.append({
                                         'tid': tid, 
                                         'cip': 0,
                                         'oid': multitask[2],
                                         'foid':foinfo.iloc[formula,0],
                                         'mid': foinfo.iloc[formula,4],
                                         'q': q-acumqt,
                                         'c': c,
                                         'stp': foinfo.iloc[formula,2],
                                         'st': 0,
                                         'end': 0,
                                         'dt':np.ceil(dt),
                                         'ddt': multitask[4],
                                         'opt': opt,
                                         'realtid':realtid}, ignore_index=True)
                        acumqt += q-acumqt
                        realtid += 1
                opt += 1
            acumqor += q
            tid = realtid
       
    #Making all the elements of the table ints
    T_multi = T_multi.astype({'tid': 'int64', 'cip': 'int','oid':'int64',
                              'foid':'int64' ,'mid':'int64','q':'int64',
                              'stp':'int64' ,'st':'int64','end':'int64',
                              'dt':'int64' ,'ddt':'int64','opt':'int',
                              'realtid':'int'})
    
    return T_multi     
    
def Detect_CriticalMachines(Fo,Or):
    #Calculus of the Critical machines with the current orders
    #The critical machines are the ones that cannot be eliminated for the completion of a product
    CriticalMachines = []
    produnique = Or.product_id.unique()
    for prod in produnique : 
        Filter = 'product_id == ' + str(prod)
        subFo = Fo.query(Filter)
        c = 0
        if len(subFo) > 1:
            for index in range(len(subFo)):
                multi = Multistage_detection(subFo,index)
                if multi == False:
                    CriticalMachines.append(subFo.iloc[index,4])
                        
    CriticalMachines = list(dict.fromkeys(CriticalMachines))
    
    return CriticalMachines

def Problem_Feasible_Machines(CriticalMachines,Mastate):
    #Check if the problem is feasible with the available machines
    """
    Work to be done
    Return Which set of orders are feasible in order to solve a partial problem
    """
    a = True
    for machine in CriticalMachines:
        if Mastate.loc[machine].available == 0:
            a = False
            break
        
    return a

def Calculusofscore(Fo,Ma,NoCritical_Machines,w_time,w_cost):
    #Function used when knowing which machine is better to eliminate if not enough workers are available
    #It takes into account the user preferences.

    multi_info = [] #This list each element will be : 
    # [[stp,prod_id],[machin_id,score],[machin_id,score],...]
    #for each multistage that is present on the Fo
    #For the calculus of the score is taken the weights
    for machine_id in NoCritical_Machines:
        subFo = Fo.query('machine_id==' + str(machine_id))
        for index_subFo in range(len(subFo)):
            prod_id = subFo.iloc[index_subFo,1]
            step = subFo.iloc[index_subFo,2]
            
            #Check if the info of this step and product has already been calculated
            c = 0
            for stored_info in multi_info:
                if stored_info[0][0] == step and stored_info[0][1] == prod_id:
                    c = 1
                    break
            #If it is not calculated proceed to calculate
            if c == 0 : 
                machine_multiFo = Fo.query('product_id ==' + str(prod_id) + '& step ==' + str(step))
                
                multi_particular_info = [[step,prod_id]]
                for index_machine_multiFo in range(len(machine_multiFo)):
                    ratio = machine_multiFo.iloc[index_machine_multiFo,7]/machine_multiFo.iloc[index_machine_multiFo,6]
                    cost = machine_multiFo.iloc[index_machine_multiFo,8]
                    score = w_time * ratio  + w_cost * cost
                    multi_particular_info.append([machine_multiFo.iloc[index_machine_multiFo,4],score])
                
                multi_info.append(multi_particular_info)
    
    #With this info it is choosen which machine to drop following the criteria:
    #eliminate one by one, the machine with more score sum
    #First is necesary to normalize the scores for the same step and product.       
    for multi_particular_info in multi_info:
        #store the scores:
        list_scores = []
        c = 1
        for multi_element_info in multi_particular_info:
            if c == 1:
                c = 0
            if c!=1:
                list_scores.append(multi_element_info[1])
        del list_scores[0]
        #normalization:
        list_scores = list_scores/sum(list_scores)
        #update the scores inside the multi_info list
        n_actualizations = len(list_scores)
        for i in range(n_actualizations):
            multi_particular_info[i+1][1] = list_scores[i]            
    
      
    #Creation of the non critical machine list with the scores normalized for each multistage step.
    listnocrit_score = []#list of [[mach],score,score,[mach],score,[mach],score]
    for nocritmach in NoCritical_Machines:
        
        listnocrit_score.append([nocritmach])
        for multi_particular_info in multi_info:
            c = 1
            for multi_element_info in multi_particular_info:
                if c == 1:
                    c = 0
                if c != 1:
                    if multi_element_info[0] == nocritmach:
                        listnocrit_score.append(multi_element_info[1])
                      
    
    #Normalization of the scores for each machine ( maybe they are implicated in more than one multistage step)
    clean_listnocrit_score = []
    list_scores = []
    list_machines = []
    for element in listnocrit_score:
        if type(element) == list:
            if len(list_machines) != 0:                        
                list_scores.append(sumscores/count)                   
            list_machines.append(element)
            c = 1                
        else: 
            if c == 1:
                sumscores = 0
                c = 0
                count = 0
            if c == 0:
                sumscores += element
                count += 1
    list_scores.append(sumscores/count)
    return list_scores, list_machines    
   
def CleanLists_withWorkers(Workers,MaState,CriticalMachines,Ma,Fo,Or,info,shifts):
    
    #Normalization of the time and cost weights
    w_cost = info['weight_cost']
    w_time = info['weight_time']
    w_cost = w_cost/(w_time+w_cost)
    w_time = w_time/(w_time+w_cost)

    #Count of the workers and machines used
    #This count is the number of the least number workers available on a given shift
    least_worker_count = 100000
    shifts_schedulability = []
    for shift in range(len(shifts)):
        shift_id = shifts.iloc[shift,0]
        worker_count = 0
        for worker in range(len(Workers)):
            if Workers.iloc[worker,0]:
                shifts_available = Workers.iloc[worker,1]
                for i in shifts_available:
                    if shift_id == i :
                        worker_count = worker_count + 1
        shifts_schedulability.append([shift_id,worker_count])
      
    least_worker_count = 100000
    for shift_info in shifts_schedulability:
        if least_worker_count > shift_info[1]:
            least_worker_count = shift_info[1]
    worker_count = least_worker_count
    
    machines_count= len(Ma)
  
    if machines_count > worker_count:
        print('Understaffed plant, eliminating machines for the schedule.')
        #Some machines will not be available due to personnel limitations
        #So a cleaning has to be done
        #Eliminating no critical machines with certain criteria
        
        #List of the nocriticalmachines
        NoCritical_Machines = []
        Machine_id_list = Ma['machine_id'].tolist()
        for machine_id in Machine_id_list:
            if not machine_id in CriticalMachines:
                NoCritical_Machines.append(machine_id)
        if len(NoCritical_Machines) < (machines_count-worker_count):
            print('Not Enough non critical machines (multistage steps) available to eliminate')
            stop = 1
        
        else:
            n_machinesout = 0
            stop = 0
            while (machines_count-worker_count) > n_machinesout and stop == 0:
                #Recalculous of the non critical machines
                NoCritical_Machines = []
                Machine_id_list = Ma['machine_id'].tolist()
                CriticalMachines = Detect_CriticalMachines(Fo,Or)
                for machine_id in Machine_id_list:
                    if not machine_id in CriticalMachines:
                        NoCritical_Machines.append(machine_id)
                        
                if len(NoCritical_Machines) == 0:
                    print('Not Enough non critical machines (multistage steps) available to eliminate')
                    stop = 1
                
                elif len(NoCritical_Machines) == 1:
                    #Only one posible machine to delete
                    worstmachine = NoCritical_Machines
                    Ma = Ma.query('machine_id !=' + str(worstmachine))
                    Fo = Fo.query('machine_id !=' + str(worstmachine))
                    n_machinesout += 1
                else:
                    #Evaluation of the non_critical machines to eliminate some of them
                    [list_scores, list_machines] = Calculusofscore(Fo,Ma,NoCritical_Machines,w_time,w_cost)                                                   
                    #Selecting the machine with worse score
                    worstscore = -1
                    index = 0
                    worstindex = -1
                    for score in list_scores:
                        if worstindex == -1 or worstscore<score:
                            worstscore = score
                            worstindex = index
                        index += 1
                    worstmachine = list_machines[worstindex]
                    
                    #Eliminating worse machine from Ma and Fo         
                    Ma = Ma.query('machine_id !=' + str(worstmachine))
                    Fo = Fo.query('machine_id !=' + str(worstmachine))
                    n_machinesout += 1
    else: 
        stop = 0
    return Ma,Fo,stop

def CleanLists_withMaStates(Ma,Fo,MaState,Or):   
    #Cleaning of the Fo and Ma and Ma with the machine availability
    ListMachinestodrop = list()
    ListFotodrop = list()
    Listofmachines = MaState.index
    machinesused = Fo.machine_id.unique()
    for machine in machinesused:
        if MaState.loc[machine]['available'] == 0:
            ListFotodrop.append(list(Fo.query('machine_id=='+str(machine)).index))
            ListMachinestodrop.append(machine)
            
    Ma = Ma.query('machine_id !=' + str(ListMachinestodrop))
    
    Fov = Fo 
    for i in ListFotodrop:
        Fov = Fov.drop(i)
        
    return Ma,Fov

def CleanLists_withOrders(Fo,Ma,Or):
    #Cleaning of Ma and Fo eliminating the elements that are not present with the set of orders (products not demanded)
    produnique = Or.product_id.unique()
    Fo = Fo.query('product_id=='+str(produnique.tolist()))
    ListMachinestodrop = list()
    machinesused = Fo.machine_id.unique()
    machine_unique = Ma.machine_id.unique()
    for machine in machine_unique:
        if not machine in machinesused:
            ListMachinestodrop.append(machine)
     
    Ma = Ma.query('machine_id != ' + str(ListMachinestodrop))
    
    return  Ma, Fo 
def Clean_Fo(Fo,Ma,Or):
    # Dealing with type 3 formulas (Changing the encoding to make it equal to type 1 formulas)
    division = 4
    for fo in range(len(Fo)):
        if Fo.iloc[fo,5] == 3:
            machine = Fo.iloc[fo,4]
            machine_info = Ma.query('machine_id=='+str(machine))
            clean_every = machine_info.iloc[0,3]
            Fo.iloc[fo,5] = 1
            Fo.iloc[fo,6] = int(Fo.iloc[fo,6]*(clean_every/division))
            Fo.iloc[fo,7] = int(np.ceil(clean_every/division))
            Fo.iloc[fo,8] = int(Fo.iloc[fo,8]*(clean_every/division))
    return Fo
            
def Encoding(Fo,Ma,MaState,Or,Workers,info,shifts):
    #Main pre-processing function
    Fo = Fo.sort_values(by=['product_id','step','max_output'],
                            ascending=[True,True,False])
    Ma = Ma.sort_values(by=['machine_id'])
    MaState = MaState.sort_index()
    CriticalMachines = Detect_CriticalMachines(Fo, Or)
    
    Fo = Clean_Fo(Fo,Ma,Or)
    [Ma,Fo] = CleanLists_withOrders(Fo,Ma,Or)
    [Ma,Fo] = CleanLists_withMaStates(Ma,Fo,MaState,Or)

    Feasible = Problem_Feasible_Machines(CriticalMachines, MaState)
    if Feasible == True: 
        if info['workers'] == 1:  
             #Eliminate worse multistage step machines if the workers are less than the machines avialable
             [Ma,Fo,stop] = CleanLists_withWorkers(Workers,MaState,CriticalMachines,Ma,Fo,Or,info,shifts)
             if stop == 1:
                 T_single = 0
                 T_multi = 0
                 Ma = 0 
             else:
                #T_list with the Fo and Or. and calculous of the information of T-multi
                [T_single,multinfo] = Tlist_Calc(Fo,Or,shifts)
                #Creation of the T_Multi with the information of the last step
                T_multi = Add_Dependencies_multi(multinfo,Fo,T_single)
                #Creating different option to choose for the multistage tasks
                #T_multi = Adding_Options(T_multi)
        else:
            [T_single,multinfo] = Tlist_Calc(Fo,Or)
            T_multi = Add_Dependencies_multi(multinfo,Fo,T_single)
        
    if Feasible == False:
        print ('Problem not feasible with the current available machines')
        T_single = 0
        T_multi = 0
        Ma = 0
    return T_single, T_multi, Ma, Fo
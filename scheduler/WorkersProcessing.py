import pandas as pd
import datetime as dt
#key function for sorting
def takeSecond(elem):
    return elem[1]

def Calculus_ofshifts_necessary(Schedule,shifts):
    horizon = Schedule['end'].max()
    today = dt.date.today()
    today_weekday = today.weekday()+2 #The function returns 0-6 and we want to schedule for tomorrow
    
    acumulated_hours = []
    for shift in range(len(shifts)):
        acumulated_hours.append(shifts.iloc[shift,3]-shifts.iloc[shift,2])
        
    unique_days = shifts['day_of_the_week'].to_list()
    unique_days = list(dict.fromkeys(unique_days))
    shifts['working_hours'] = acumulated_hours
    
    if today_weekday in unique_days:
        shift_index = shifts.query('day_of_the_week=='+str(today_weekday)).index[0]
    elif today_weekday > max(unique_days):
        shift_index = 0
    else:
        encountred = 0
        while encountred == 0:
            today_weekday += 1
            if today_weekday in unique_days:
                shift_index = shifts.query('day_of_the_week=='+str(today_weekday)).index[0]
                encountred += 1
    
    starting_index = shift_index
            
    working_hours = 0; n_shifts = 0       
    while working_hours < horizon: 
        working_hours += shifts.iloc[shift_index,4]
        shift_index += 1
        if shift_index >= len(shifts)-1:
            shift_index = 0
        n_shifts += 1
    
        
    return n_shifts, starting_index
        
    
    
def WorkersScheduler(Ma,Workers,Schedule,shifts):
    Workers_Schedule = pd.DataFrame(columns=['worker_id',
                                             'machine_id',
                                             'shift_id'])
   
    
    n_machines = len(Ma)
    Workers['hours'] = [0]*len(Workers)
    
    
    SelectedWorkers = []
    SelectedMa = []
    
    [n_shifts,starting_index] = Calculus_ofshifts_necessary(Schedule,shifts)
    
    shift_index = starting_index; n_scheduled = 0;
    while n_scheduled < n_shifts:
        
        shift_id = shifts.iloc[shift_index,0]
        shift_start = shifts.iloc[shift_index,2]
        shift_end = shifts.iloc[shift_index,3]
        shift_working_hours = shift_end - shift_start
        
        posible_workers = []
        for worker in range(len(Workers)):
            if Workers.iloc[worker,0]:
                shifts_available = Workers.iloc[worker,1]
                for i in shifts_available:
                    if shift_id == i :
                        posible_workers.append([Workers.iloc[worker].name,Workers.iloc[worker,2]])
        
        posible_workers.sort(key=takeSecond)
        for i in range(n_machines):
            machine=Ma.iloc[i,0]
            machine = Ma.iloc[i,0]
            SelectedMa.append(machine)

            Workers.at[posible_workers[i][0],'hours'] += shift_working_hours
            Workers_Schedule = Workers_Schedule.append({'worker_id':posible_workers[i][0], 'machine_id':machine, 'shift_id':shift_id}, ignore_index=True)
        shift_index += 1
        n_scheduled += 1
        if shift_index >= len(shifts)-1:
            shift_index = 0
                                                        
        
    return Workers_Schedule
    

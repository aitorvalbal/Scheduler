import pandas as pd
import json
import numpy


def Import_Json_from_request(data):
    #Create table from raw data
    y = data
    
    Problem_info = y['problem_info']
    formulas = y['formulas']
    machines = y['machines']
    machines_states = y['machines_states']
    orders = y['orders']
    workers_states = y['workers']
    shifts = y['shifts']
    
    #Order conversion:
    order_id_list = []
    delivery_date_list = []
    quantity_list = []
    product_id_list = []
    for order in orders: 
        order_id_list.append(order['order_id'])
        delivery_date_list.append(order['delivery_date'])
        quantity_list.append(order['quantity'])
        product_id_list.append(order['product_id'])    
    orders = {'order_id': order_id_list,
              'delivery_date': delivery_date_list,
              'quantity':quantity_list,
              'product_id':product_id_list}
    Or = pd.DataFrame.from_dict(orders)
    
    #Formulas conversion
    formula_id_list = []
    product_id_list = []
    step_list = []
    stp_pre_list = []
    machine_id_list = []
    type_list = []
    max_output_list = []
    processing_delay_list = []
    cost_list = []
    for formula in formulas: 
        formula_id_list.append(formula['formula_id'])
        product_id_list.append(formula['product_id'])
        step_list.append(formula['step'])
        stp_pre_list.append(formula['stp_pre']) 
        machine_id_list.append(formula['machine_id']) 
        type_list.append(formula['type']) 
        max_output_list.append(formula['max_output'])
        processing_delay_list.append(formula['processing_delay'])
        cost_list.append(formula['cost'])
    formulas = {'formula_id': formula_id_list,
              'product_id': product_id_list,
              'step':step_list,
              'stp_pre':stp_pre_list,
              'machine_id':machine_id_list,
              'type':type_list,
              'max_output':max_output_list,
              'processing_delay':processing_delay_list,
              'cost':cost_list}
    Fo = pd.DataFrame.from_dict(formulas)
    
    #Force the formulas to go from 1 and += 1
    z = 1
    for formula in range(len(Fo)):
        Fo.iloc[formula,0] = z
        z += 1
    #Machines conversion
    
    machine_id_list = []
    clean_delay_list = []
    clean_cost_list = []
    clean_every_list = []
    for machine in machines: 
        machine_id_list.append(machine['machine_id'])
        clean_delay_list.append(machine['clean_delay'])
        clean_cost_list.append(machine['clean_cost'])
        clean_every_list.append(machine['clean_every'])
    machines = {'machine_id': machine_id_list,
              'clean_delay': clean_delay_list,
              'clean_cost':clean_cost_list,
              'clean_every_list':clean_every_list}
    Ma = pd.DataFrame.from_dict(machines)
    #Machines_state
    
    machine_states = machines_states['available']
    Mastate = pd.DataFrame.from_dict(machine_states, orient='index')
    Mastate.columns = ['available']
    Mastate = Mastate.rename(index=int)
    
    #Workers Info
    if workers_states != [0]:
        workers_states = workers_states['available']
        Workers = pd.DataFrame.from_dict(workers_states, orient='index', columns=['available','shifts_available'])
        Workers = Workers.rename(index=int)  
    else : 
        Workers = 0
    #Shifts info
    shifts_id_list = []
    day_of_the_week_list = []
    shift_start_list = []
    shifts_end_list = []
    if shifts != [0]:        
        for shift in shifts: 
            shifts_id_list.append(shift['shift_id'])
            day_of_the_week_list.append(shift['day_of_the_week'])
            shift_start_list.append(shift['shift_start'])
            shifts_end_list.append(shift['shift_end'])
        shifts = {'shift_id': shifts_id_list,
                  'day_of_the_week': day_of_the_week_list,
                  'shift_start': shift_start_list,
                  'shift_end': shifts_end_list}
        Shifts = pd.DataFrame.from_dict(shifts)
        Shifts = Shifts.sort_values(by=['day_of_the_week','shift_start'])
    else:
        Shifts = 0
    return Fo, Ma, Or, Mastate, Problem_info, Workers, Shifts

def Import_Json(name):
    #Extract tables from JSON file.
    with open(name) as f:
            Fo_string = f.read()
    
    y = json.loads(Fo_string)
    
    Problem_info = y['problem_info']
    formulas = y['formulas']
    machines = y['machines']
    machines_states = y['machines_states']
    orders = y['orders']
    workers_states = y['workers']
    shifts = y['shifts']
    
    #Order conversion:
    order_id_list = []
    delivery_date_list = []
    quantity_list = []
    product_id_list = []
    for order in orders: 
        order_id_list.append(order['order_id'])
        delivery_date_list.append(order['delivery_date'])
        quantity_list.append(order['quantity'])
        product_id_list.append(order['product_id'])    
    orders = {'order_id': order_id_list,
              'delivery_date': delivery_date_list,
              'quantity':quantity_list,
              'product_id':product_id_list}
    Or = pd.DataFrame.from_dict(orders)
    
    #Formulas conversion
    formula_id_list = []
    product_id_list = []
    step_list = []
    stp_pre_list = []
    machine_id_list = []
    type_list = []
    max_output_list = []
    processing_delay_list = []
    cost_list = []
    for formula in formulas: 
        formula_id_list.append(formula['formula_id'])
        product_id_list.append(formula['product_id'])
        step_list.append(formula['step'])
        stp_pre_list.append(formula['stp_pre']) 
        machine_id_list.append(formula['machine_id']) 
        type_list.append(formula['type']) 
        max_output_list.append(formula['max_output'])
        processing_delay_list.append(formula['processing_delay'])
        cost_list.append(formula['cost'])
    formulas = {'formula_id': formula_id_list,
              'product_id': product_id_list,
              'step':step_list,
              'stp_pre':stp_pre_list,
              'machine_id':machine_id_list,
              'type':type_list,
              'max_output':max_output_list,
              'processing_delay':processing_delay_list,
              'cost':cost_list}
    Fo = pd.DataFrame.from_dict(formulas)
    
    #Force the formulas to go from 1 and += 1
    z = 1
    for formula in range(len(Fo)):
        Fo.iloc[formula,0] = z
        z += 1
    #Machines conversion
    
    machine_id_list = []
    clean_delay_list = []
    clean_cost_list = []
    clean_every_list = []
    for machine in machines: 
        machine_id_list.append(machine['machine_id'])
        clean_delay_list.append(machine['clean_delay'])
        clean_cost_list.append(machine['clean_cost'])
        clean_every_list.append(machine['clean_every'])
    machines = {'machine_id': machine_id_list,
              'clean_delay': clean_delay_list,
              'clean_cost':clean_cost_list,
              'clean_every_list':clean_every_list}
    Ma = pd.DataFrame.from_dict(machines)
    #Machines_state
    
    machine_states = machines_states['available']
    Mastate = pd.DataFrame.from_dict(machine_states, orient='index')
    Mastate.columns = ['available']
    Mastate = Mastate.rename(index=int)
    
    #Workers Info
    if workers_states != [0]:
        workers_states = workers_states['available']
        Workers = pd.DataFrame.from_dict(workers_states, orient='index', columns=['available','shifts_available'])
        Workers = Workers.rename(index=int)  
    else : 
        Workers = 0
    #Shifts info
    shifts_id_list = []
    day_of_the_week_list = []
    shift_start_list = []
    shifts_end_list = []
    if shifts != [0]:        
        for shift in shifts: 
            shifts_id_list.append(shift['shift_id'])
            day_of_the_week_list.append(shift['day_of_the_week'])
            shift_start_list.append(shift['shift_start'])
            shifts_end_list.append(shift['shift_end'])
        shifts = {'shift_id': shifts_id_list,
                  'day_of_the_week': day_of_the_week_list,
                  'shift_start': shift_start_list,
                  'shift_end': shifts_end_list}
        Shifts = pd.DataFrame.from_dict(shifts)
        Shifts = Shifts.sort_values(by=['day_of_the_week','shift_start'])
    else:
        Shifts = 0
    return Fo, Ma, Or, Mastate, Problem_info, Workers, Shifts


def Create_Json_Solution(Sequence,Workers_Schedule,info):
    #Create Solution File
    with open('Solution.json','w') as f:
        if info['workers'] == 1:
            Solution = '{\n"task_sequence":\n'+ Sequence.to_json(orient='records',indent = 1) + ',\n "workers_schedule":\n' + Workers_Schedule.to_json(orient='records',indent = 1) +'\n }' 
            f.write(Solution)
        else:
            Solution = '{\n"task_sequence":\n'+ Sequence.to_json(orient='records',indent = 1) + '\n }'
            f.write(Solution)
    return Solution
        
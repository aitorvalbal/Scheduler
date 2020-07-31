
from scheduler import ProblemDef as PD

#Name of the input file as an argument of the initialization
#second argument is the mode of initialization (json or flask)
Pro = PD.Problem('test.json','json')
Pro.Scheduler()

Pro.Graphic_Sequence()

Pro.Return_json()

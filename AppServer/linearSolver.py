from __future__ import print_function
import six
from ortools.linear_solver import pywraplp

from ortools.sat.python import cp_model
from collections import namedtuple

#quitarlos si no se usan, es una caca que hice para poder testear directamente aca
from django.http import JsonResponse, HttpResponseServerError
import json
from LyOpServer import settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LyOpServer.settings')
# aca termina la caca

def solve(json_data):
    # carga de datos, tendria que hacerse en un model o algo, asi es muy choto
    cant_rest = int(json_data['cantRest'])
    cant_var = int(json_data['cantVars'])
    coef = json_data['coef']
    min = json_data['min']
    sign = json_data['sign']
    term_indp = json_data['term_indp']
    obj = json_data['obj']

    # creo el solver
    solver = pywraplp.Solver('LinearProgrammingSolver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    # agrego variables
    vars = [solver.NumVar(0, solver.infinity(), 'x'+str(i)) for i in range(cant_var)]

    # agrego restricciones
    for i in range(cant_rest):
        # signo y termino independiente
        if sign[i] == '=':
            constraint = solver.Constraint(term_indp[i], term_indp[i])
        elif sign[i] == '>':
            constraint = solver.Constraint(term_indp[i], solver.infinity())
        elif sign[i] == '<':
            constraint = solver.Constraint(-solver.infinity(), term_indp[i])
        #coeficientes
        for j in range(cant_var):
            constraint.SetCoefficient(vars[j], coef[i][j])

    # funcion objetivo
    objective = solver.Objective()
    for i in range(cant_var):
        objective.SetCoefficient(vars[i], obj[i])
    if min is True:
        objective.SetMinimization()
    else:
        objective.SetMaximization()

    solver.Solve()
    solution = [var.solution_value() for var in vars]
    opt = sum([obj[i]*vars[i].solution_value() for i in range(cant_var)])
    return {'solution': solution, 'opt': opt}

def ejemplo():
    """Linear programming sample."""
    # Instantiate a Glop solver, naming it LinearExample.
    # [START solver]
    solver = pywraplp.Solver('LinearProgrammingExample',
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    # [END solver]

    # Create the two variables and let them take on any non-negative value.
    # [START variables]

    # cantidad de variables, podemos asumir que seran -solver.infinity(), solver.infinity

    x = solver.NumVar(0, solver.infinity(), 'x')
    y = solver.NumVar(0, solver.infinity(), 'y')
    # [END variables]

    # [START constraints]
    # Constraint 0: x + 2y <= 14.
    constraint0 = solver.Constraint(-solver.infinity(), 14)
    constraint0.SetCoefficient(x, 1)
    constraint0.SetCoefficient(y, 2)

    # Constraint 1: x + 2y >= 16.
    constraint1 = solver.Constraint(17, solver.infinity())
    constraint1.SetCoefficient(x, 2)
    constraint1.SetCoefficient(y, 1)

    # Constraint 2: x - y <= 2.
    constraint2 = solver.Constraint(-solver.infinity(), 2)
    constraint2.SetCoefficient(x, 1)
    constraint2.SetCoefficient(y, -1)
    # [END constraints]

    # [START objective]
    # Objective function: 3x + 4y.
    objective = solver.Objective()
    objective.SetCoefficient(x, 3)
    objective.SetCoefficient(y, 4)
    objective.SetMaximization()
    # [END objective]

    # Solve the system.
    # [START solve]
    status = solver.Solve()
    # [END solve]
    # [START print_solution]
    opt_solution = 3 * x.solution_value() + 4 * y.solution_value()
    print('Number of variables =', solver.NumVariables())
    print('Number of constraints =', solver.NumConstraints())
    # The value of each variable in the solution.
    print('Solution:')
    print('x = ', x.solution_value())
    print('y = ', y.solution_value())
    # The objective value of the solution.
    print('Optimal objective value =', opt_solution)
    # [END print_solution]
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
        print('x =', x.solution_value())
        print('y =', y.solution_value())
    else:
        print('The problem does not have an optimal solution.')

    return [x.solution_value(), y.solution_value()]

# [END program]

def test2():

    data = {
            'cantRest': "2",
            'cantVars': "2",
            'coef':
                [[1, 7],
                 [1, 0]],
            'min': False,
            'sign': ['>', '>'],
            'term_indp': [17.5, 3.5],
            'obj': [3, 4]
            }

    request = JsonResponse(data, safe=False) #esto simula lo que enrealidad seria el request
    solution_data = integer(json.loads(request.content))
    return JsonResponse(solution_data)


def integer(body):
    json_data = body
    print("llego")
    print(json_data)
    # carga de datos, tendria que hacerse en un model o algo, asi es muy choto
    cant_rest = int(json_data['cantRest'])
    cant_var = int(json_data['cantVars'])
    coef = json_data['coef']
    min = json_data['min']
    sign = json_data['sign']
    term_indp = json_data['term_indp']
    obj = json_data['obj']

    # creo el solver
    solver = pywraplp.Solver('IntegerProgrammingSolver', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # agrego variables
    vars = [solver.IntVar(0.0, solver.infinity(), 'x' + str(i)) for i in range(cant_var)]

    # agrego restricciones
    for i in range(cant_rest):
        # signo y termino independiente
        if sign[i] == '=':
            constraint = solver.Constraint(term_indp[i], term_indp[i])
        elif sign[i] == '<':
            constraint = solver.Constraint(term_indp[i], solver.infinity())
        elif sign[i] == '>':
            constraint = solver.Constraint(-solver.infinity(), term_indp[i])
        # coeficientes
        for j in range(cant_var):
            constraint.SetCoefficient(vars[j], coef[i][j])

    # funcion objetivo
    objective = solver.Objective()
    for i in range(cant_var):
        objective.SetCoefficient(vars[i], obj[i])
    if min is True:
        objective.SetMinimization()
    else:
        objective.SetMaximization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        solution = [var.solution_value() for var in vars]
        opt = sum([obj[i] * vars[i].solution_value() for i in range(cant_var)])
        answer = {'error': False, 'solution': solution, 'opt': opt}
        print(solution)
        print(opt)
    else:
        answer = {'error': True, 'message': 'No existe una solución'}
        print('No existe una solución')
    return answer

def sensibility(body):
    # data = {
    #     'cantProductos': "2",
    #     'cantInsumos': "3",
    #     'costeProd':
    #         [[1, 3, 0],
    #          [1, 4, 1]],
    #     'stockInsumos':
    #         [50, 180, 40],
    #     'beneficio':
    #         [40, 50],
    # }
    json_data = body
    print("llego")
    print(json_data)
    cant_prod = int(json_data['cantProductos'])
    cant_ins = int(json_data['cantInsumos'])
    coste_prod = json_data['costeProd']
    beneficio = json_data['beneficio']
    stock = json_data['stockInsumos']

    # creo el solver
    solver = pywraplp.Solver('LinearProgrammingSolver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    # agrego variables, una por cada producto, indican la produccion de cada producto
    produccion = [solver.NumVar(0.0, solver.infinity(), 'p' + str(i)) for i in range(cant_prod)]

    print(coste_prod)
    print(produccion)
    cons = []
    # agrego restricciones, no se puede sobrepasar el stock de cada insumo
    for i in range(cant_ins):
        constraint = solver.Constraint(-solver.infinity(), stock[i])
        # coeficientes
        for j in range(cant_prod):
            constraint.SetCoefficient(produccion[j], coste_prod[j][i])
        cons.append(constraint)

    # funcion objetivo
    objective = solver.Objective() # maximizar sum(beneficio*produccion)
    for i in range(cant_prod):
        objective.SetCoefficient(produccion[i], beneficio[i])
    objective.SetMaximization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        solution = [var.solution_value() for var in produccion]
        opt = sum([beneficio[i] * produccion[i].solution_value() for i in range(cant_prod)])
        consumo = [sum([coste_prod[i][j]*solution[i] for i in range(cant_prod)]) for j in range(cant_ins)]
        costo_reducido = [var.reduced_cost() for var in produccion] # def: la cantidad por la cual un coeficiente de
                                                    # la funcion objetivo tiene que aumentar para que sea posible que
                                                    # variable correspondiente tome un valor > 0 en una solución óptima

        dual_value = [c.dual_value() for c in cons] # def: the change in the value of an objective function per unit
                                                    # increase in the right-hand side of a constraint (lo vimos como
                                                    # shadow price o precio sombra)
        answer = {'error': False,
                  'solution': solution,
                  'opt': opt,
                  'consumo': consumo,
                  'costo_reducido': costo_reducido,
                  'dual_value': dual_value
                  }
    else:
        answer = {'error': True, 'message': 'No existe una solución'}
        print('No existe una solución')
    return answer

def testSensibility():

    data = {
            'cantProductos': "2",
            'cantInsumos': "3",
            'costeProd':
                [[1, 3, 0],
                 [1, 4, 1]],
            'stockInsumos':
                [50, 180, 40],
            'beneficio':
                [40, 100],
            }

    request = JsonResponse(data, safe=False) #esto simula lo que enrealidad seria el request
    solution_data = sensibility(json.loads(request.content))
    return JsonResponse(solution_data)

def scheduling(body):
    # data = {
    #     'cantJobs': "3",
    #     'cantTasks': "4",
    #     'tiempoTasks':  # lo que se demora cada tarea
    #            [3, 3, 2, 1],
    #     'precedencia':  # restricciones de precedencia, son del tipo endBeforeStart(tarea1, tarea2)
    #            [[4, 3],
    #            [3, 2],
    #            [2, 1]],
    #     'cantRecursos': "2",
    #     'cantUnidades': # cantidad de cada recurso
    #           [1, 2],
    #     'demandaTasks':
    #         [[1, 0],
    #          [1, 1],
    #          [0, 1],
    #          [1, 0]]
    # }

    json_data = body
    print("llego")
    print(json_data)
    cant_jobs = int(json_data['cantJobs'])
    cant_tasks = int(json_data['cantTasks'])
    tiempo_tasks = json_data['tiempoTasks']
    precedencia = (json_data['precedencia'])
    cant_recursos = int(json_data['cantRecursos'])
    cant_unidades = json_data['cantUnidades']
    demanda_tasks = json_data['demandaTasks']

    # crear modelo
    model = cp_model.CpModel()

    # crear las variables de decision: intervalos para cada task
    task_type = namedtuple('task_type', 'jobId taskId start end interval demand')
    jobs = []
    all_tasks = []
    limite = sum(tiempo_tasks)*cant_jobs    # limite de tiempo para las variables
    for j in range(cant_jobs):
        tasks = []
        for t in range(cant_tasks):
            id = '_'+str(j)+'_'+str(t)

            start = model.NewIntVar(0, limite, 'start'+id)
            duration = tiempo_tasks[t]
            end = model.NewIntVar(0, limite, 'end'+id)
            interval = model.NewIntervalVar(start, duration, end, 'interval'+id)

            demand = demanda_tasks[t]

            task = task_type(j, t, start, end, interval, demand)
            tasks.append(task)
            all_tasks.append(task)
        jobs.append(tasks)

    print(jobs)

    # Restricciones
    # Precedencia
    for p in precedencia:
        end_task = p[0] - 1
        before_start_task = p[1] - 1
        for job in jobs:
            model.Add(job[end_task].end <= job[before_start_task].start)

    # Recursos: va a ser siempre con reposición, que el acumulado de la demanda de cada recurso no supere la capacidad
    # en un momento dado
    for r in range(cant_recursos):
        model.AddCumulative([task.interval for task in all_tasks],  # los intervalos de los tasks
                             [task.demand[r] for task in all_tasks],  # la demanda por cada task de ese recurso
                             cant_unidades[r])   # la capacidad de cada recurso

    # Objetivo: crear un timeSpan que termine lo antes posible la ultima tarea del ultimo job
    obj_var = model.NewIntVar(0, limite, 'makespan')
    model.AddMaxEquality(obj_var, [task.end for task in job for job in jobs])
    model.Minimize(obj_var)

    # Resolver el modelo
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        solution = []
        for task in all_tasks:
            solution.append({'job': task.jobId+1,
                             'task': task.taskId+1,
                             'start': solver.Value(task.start),
                             'end': solver.Value(task.end)})
        answer = {'error': False, 'solution': solution}

    else:
        answer = {'error': True, 'message': 'No existe una solución'}
    print(solution)
    print(answer)
    return answer


def testScheduling():
    data = {
        'cantJobs': "3",
        'cantTasks': "4",
        'tiempoTasks':  # lo que se demora cada tarea
               [3, 3, 2, 1],
        'precedencia':  # restricciones de precedencia, son del tipo endBeforeStart(tarea1, tarea2)
              [[3, 4],
               [2, 3],
               [1, 2]],
        'cantRecursos': "2",
        'cantUnidades':  # cantidad de cada recurso
              [1, 2],
        'demandaTasks':
            [[1, 0],
             [0, 1],
             [0, 1],
             [1, 0]]
    }
    request = JsonResponse(data, safe=False)  # esto simula lo que enrealidad seria el request
    solution_data = scheduling(json.loads(request.content))
    return JsonResponse(solution_data)


print(testScheduling())

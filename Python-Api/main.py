from collections import namedtuple

from ortools.linear_solver import pywraplp


import hug
from ortools.sat.python import cp_model

api = hug.API(__name__)
api.http.add_middleware(hug.middleware.CORSMiddleware(api, max_age=10))


@hug.get("/") 
def main():
    return "API para aplicación LyOp->  https://www.lyop-unsj.web.app"

@hug.post("/lineal") 
def lineal(body):
    json_data=body
    print("llego" )
    print(json_data)

    # carga de datos
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
        elif sign[i] == '<':
            constraint = solver.Constraint(term_indp[i], solver.infinity())
        elif sign[i] == '>':
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


@hug.post("/integer")
def integer(body):
    json_data = body
    print("llego")
    print(json_data)
    # carga de datos
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


@hug.post("/sensibility")
def sensibility(body):
    json_data = body
    print("llego")
    print(json_data)
    # carga de datos, tendria que hacerse en un model o algo, asi es muy choto
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
    # restricciones, no se puede sobrepasar el stock de cada insumo
    for i in range(cant_ins):
        constraint = solver.Constraint(-solver.infinity(), stock[i])
        # coeficientes
        for j in range(cant_prod):
            constraint.SetCoefficient(produccion[j], coste_prod[j][i])
        cons.append(constraint)

    # funcion objetivo
    objective = solver.Objective()  # maximizar sum(beneficio*produccion)
    for i in range(cant_prod):
        objective.SetCoefficient(produccion[i], beneficio[i])
    objective.SetMaximization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        solution = [var.solution_value() for var in produccion]
        opt = sum([beneficio[i] * produccion[i].solution_value() for i in range(cant_prod)])
        consumo = [sum([coste_prod[i][j] * solution[i] for i in range(cant_prod)]) for j in range(cant_ins)]
        costo_reducido = [var.reduced_cost() for var in produccion]  # def: la cantidad por la cual un coeficiente de
        # la funcion objetivo tiene que aumentar para que sea posible que
        # variable correspondiente tome un valor > 0 en una solución óptima

        dual_value = [c.dual_value() for c in cons]  # def: the change in the value of an objective function per unit
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


@hug.post("/scheduling")
def scheduling(body):
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
    return answer



# Especificación de formatos json:
# lineal y integer:
#     problema:
#         data = {    'cantRest': "2",
#                     'cantVars': "2",
#                     'coef':
#                         [[1, 7],
#                          [1, 0]],
#                     'min': False,
#                     'sign': ['>', '>'],
#                     'term_indp': [17.5, 3.5],
#                     'obj': [3, 4]
#                     }
#     respuesta:
#         exito:
#             answer = {'error': False,
#                       'solution': solution,
#                       'opt': opt}
#         fallo:
#             answer = {'error': True,
#                       'message': 'No existe una solución'}
# # sensibility:
#     problema:
#          data = {
#              'cantProductos': "2",
#              'cantInsumos': "3",
#              'costeProd':
#                  [[1, 3, 0],
#                   [1, 4, 1]],
#              'stockInsumos':
#                  [50, 180, 40],
#              'beneficio':
#                  [40, 50],
#          }
#     respuesta:
#         exito:
#             answer = {'error': False,
#                               'solution': solution,
#                               'opt': opt,
#                               'consumo': consumo,
#                               'costo_reducido': costo_reducido,
#                               'dual_value': dual_value
#                               }
#         fallo:
#             answer = {'error': True,
#                       'message': 'No existe una solución'}
#
# scheduling:
#      problema:
#         data = {
#             'cantJobs': "3",
#             'cantTasks': "4",
#             'tiempoTasks':  # lo que se demora cada tarea
#                    [3, 3, 2, 1],
#             'precedencia':  # restricciones de precedencia, son del tipo endBeforeStart(tarea1, tarea2)
#                   [[3, 4],
#                    [2, 3],
#                    [1, 2]],
#             'cantRecursos': "2",
#             'cantUnidades':  # cantidad de cada recurso
#                   [1, 2],
#             'demandaTasks':
#                 [[1, 0],
#                  [0, 1],
#                  [0, 1],
#                  [1, 0]]
#         }
#       answer:
#         exito:
#             answer = {'error': False,
#                       'solution': [
#                               {'job': jobId,
#                                 'task': taskId,
#                                 'start': start,
#                                 'end': end
#                                } ...
#                           ]
#                       }
#             fallo:
#                      answer = {'error': True,
#                                 'message': 'No existe una solución'}
# Explicacion del problema de shceduling:
# Existen x trabajos iguales de y tareas cada uno. Las tareas siempre se demoran el mismo tiempo.
# Exiten z cantidad de recursos de los que hay una cierta capacidad (ejemplo: empleados)
# Siempre se minimiza el final de todos los trabajos
# Las restricciones dependen del orden de precedencia que se les de y de la cantidad de recursos que
# use cada tipo de tarea. Similar al ejemplo de la construccion de la casa, pero mas general.
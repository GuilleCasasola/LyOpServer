from __future__ import print_function
import six
from ortools.linear_solver import pywraplp

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

    # Constraint 1: 3x - y >= 0.
    constraint1 = solver.Constraint(0, solver.infinity())
    constraint1.SetCoefficient(x, 3)
    constraint1.SetCoefficient(y, -1)

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
    solver.Solve()
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
    return [x.solution_value(), y.solution_value()]

# [END program]

ejemplo()
def test2():

    data = {
            'cantRest': "3",
            'cantVars': "2",
            'coef':
                [[1, 2],
                 [3, -1],
                 [1, -1]],
            'min': False,
            'sign': ['<', '>', '<'],
            'term_indp': [14, 0, 2],
            'obj': [3, 4]
            }

    request = JsonResponse(data, safe=False) #esto simula lo que enrealidad seria el request
    solution_data = solve(json.loads(request.content))
    return JsonResponse(solution_data)

print(test2())
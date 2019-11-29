from ortools.linear_solver import pywraplp


import hug


api = hug.API(__name__)
api.http.add_middleware(hug.middleware.CORSMiddleware(api, max_age=10))


@hug.get("/") 
def main():
    return     {"results": {"nombre": "Guille"}}

@hug.post("/lineal") 
def lineal(body):
    json_data=body
    print("llego" )
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

    solver.Solve()
    solution = [var.solution_value() for var in vars]
    opt = sum([obj[i]*vars[i].solution_value() for i in range(cant_var)])
    return {'solution': solution, 'opt': opt}
    

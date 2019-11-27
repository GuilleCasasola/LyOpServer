from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError
import json
from AppServer import linearSolver


def linear(request):

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
    solution_data = linearSolver.solve(json.loads(request.content))
    return JsonResponse(solution_data)


def test(request):
    data = json.loads(request.content)
    data['cantRest'] = 'SUPUTAMADRE'
    return data


from collections import OrderedDict, deque
import copy
from math import sqrt
from flask import Flask, render_template, request
from ast import literal_eval
import sudoku_constraints
app = Flask(__name__)

def revise(csp, variableOneName, variableTwoName):
    newDomain = []
    for i in range(len(csp.get("variables").get(variableOneName))):
        for j in range(len(csp.get("variables").get(variableTwoName))):
            if csp.get("variables").get(variableOneName)[i] != csp.get("variables").get(variableTwoName)[j]:
                newDomain.append(csp.get("variables").get(variableOneName)[i])
                break
    numChanges = len(csp.get("variables").get(variableOneName)) - len(newDomain)
    if len(csp.get("variables")[variableOneName]) > 1:
        csp.get("variables")[variableOneName] = newDomain
    return numChanges != 0

def ac3(csp):
    queue = deque()
    constraintsList = list(csp.get("constraints").keys())
    for constraint in constraintsList:
        queue.appendleft(constraint)
        queue.appendleft((constraint[1], constraint[0]))
    while len(queue) != 0:
        constraint = queue.pop()
        if revise(csp, constraint[0], constraint[1]):
            if len(csp.get("variables").get(constraint[0])) == 0:
                return False
            for variable in csp.get("constraints"):
                #neighbors in a row
                if variable[1] == constraint[0] and variable[0] != constraint[1]:
                    queue.appendleft(variable)
                #neighbors in a column
                elif variable[0] == constraint[0] and variable[1] != constraint[1]:
                    queue.appendleft((variable[1], constraint[0]))
    return True

def minimumRemainingValues(csp, assignments):
    for variable in assignments.keys():
        csp["variables"][variable] = assignments.get(variable)
    minLength = int(sqrt(len(csp["variables"].keys()))) + 1
    finalVariable = ""
    for variable in csp["variables"].keys():
        if len(csp["variables"].get(variable)) < minLength and len(csp["variables"].get(variable)) > 1:
            minLength = len(csp["variables"].get(variable))
            finalVariable = variable
    return finalVariable

def backtrack(csp, assignment):
    numFilledTiles = 0
    for variable in csp.get("variables").keys():
        if len(csp.get("variables").get(variable)) == 1:
            numFilledTiles += 1
    #if len(assignment) == len(csp.get("variables").keys()):
        #return assignment
    if numFilledTiles == len(csp["variables"].keys()):
        return assignment
    var = minimumRemainingValues(csp, assignment)
    for value in csp["variables"][var]:
        oldDomains = copy.deepcopy(csp["variables"])
        csp["variables"][var] = [value]
        if ac3(csp):
            assignment[var] = value
            result = backtrack(csp, assignment)
            if result != None:
                return result
        del assignment[var]
        csp["variables"] = oldDomains
    return None

def backtrackingSearch(csp):
    return backtrack(csp, OrderedDict())

@app.route('/')
def createWebsite():
    return render_template('form.html')

@app.route('/solve')
def saveSudoku():
    csp = {"variables": {}, "constraints": sudoku_constraints.nineByNineConstraints}
    board = [[None for row in range(9)] for col in range(9)]
    for row in range(9):
        for col in range(9):
            var = "C{}{}".format(row+1, col+1)
            val = request.args[var]
            val = int(val) if val else val
            board[row][col] = val
            if val:
                csp["variables"][var] = [val]
            else:
                csp["variables"][var] = list(range(1, 10))
    boards = [board]
    solution = backtrackingSearch(csp)
    for var in solution:
        board = copy.deepcopy(board)
        row = int(var[1])
        col = int(var[2])
        board[row-1][col-1] = solution[var]
        boards.append(board)
    return render_template('savedSudoku.html', boards=boards)

if __name__ == "__main__":
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
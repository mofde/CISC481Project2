from collections import OrderedDict, deque
import copy
from math import sqrt
from flask import Flask, render_template, request
import sudoku_constraints
app = Flask(__name__)

def revise(csp, variableOneName, variableTwoName, assignment):
    numChanges = 0
    newDomain = []
    for i in range(len(csp.get("variables").get(variableOneName))):
        for j in range(len(csp.get("variables").get(variableTwoName))):
            if csp.get("variables").get(variableOneName)[i] != csp.get("variables").get(variableTwoName)[j] and csp.get("variables").get(variableOneName)[i] not in newDomain:
                newDomain.append(csp.get("variables").get(variableOneName)[i])
    numChanges = len(csp.get("variables").get(variableOneName)) - len(newDomain)
    newDomain.sort()
    csp.get("variables")[variableOneName] = newDomain
    if len(csp.get("variables")[variableOneName]) == 1:
        assignment[variableOneName] = csp.get("variables")[variableOneName][0]
    return numChanges != 0

def ac3(csp, assignment):
    queue = deque()
    constraintsList = list(csp.get("constraints").keys())
    for constraint in constraintsList:
        queue.appendleft(constraint)
    while len(queue) != 0:
        constraint = queue.pop()
        if revise(csp, constraint[0], constraint[1], assignment):
            if len(csp.get("variables").get(constraint[0])) == 0:
                return False
    return True

def minimumRemainingValues(csp, assignments):
    for variable in assignments.keys():
        csp["variables"][variable] = [assignments.get(variable)]
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
    if numFilledTiles == len(csp["variables"].keys()):
        return assignment
    var = minimumRemainingValues(csp, assignment)
    oldDomain = copy.deepcopy(csp["variables"][var])
    for value in csp["variables"][var]:
        cspCopy = copy.deepcopy(csp)
        cspCopy["variables"][var] = [value]
        if ac3(cspCopy, assignment):
            assignment[var] = value
            csp["variables"][var] = [value]
            result = backtrack(csp, assignment)
            if result != None:
                return result
            csp["variables"][var] = oldDomain
    if var in assignment.keys():
        del assignment[var]
    return None

def backtrackingSearch(csp):
    return backtrack(csp, OrderedDict())

@app.route('/')
def createWebsite():
    return render_template('inputSudoku.html')

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
    if solution != None:
        for var in solution:
            board = copy.deepcopy(board)
            row = int(var[1])
            col = int(var[2])
            board[row-1][col-1] = solution[var]
            boards.append(board)
    return render_template('sudokuSolution.html', boards=boards)

if __name__ == "__main__":
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
from collections import OrderedDict, deque
import copy
from math import sqrt
from flask import Flask, render_template

def revise(csp, variableOneName, variableTwoName):
    newDomain = []
    for i in range(len(csp.get("variables").get(variableOneName))):
        for j in range(len(csp.get("variables").get(variableTwoName))):
            if csp.get("variables").get(variableOneName)[i] != csp.get("variables").get(variableTwoName)[j]:
                newDomain.append(csp.get("variables").get(variableOneName)[i])
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
    minLength = int(sqrt(len(csp["variables"].keys())))
    finalVariable = ""
    for variable in csp["variables"].keys():
        if len(csp["variables"].get(variable)) <= minLength and len(csp["variables"].get(variable)) > 1:
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
    for value in csp["variables"][var]:
        oldDomains = copy.deepcopy(csp["variables"])
        csp["variables"][var] = [value]
        if ac3(csp):
            assignment[var] = [value]
            result = backtrack(csp, assignment)
            if result != None:
                return result
        del assignment[var]
        csp["variables"] = oldDomains
    return None

def backtrackingSearch(csp):
    return backtrack(csp, OrderedDict())

app.route("/")
def webDesign():
    return render_template("sudoku.html", message="web design")
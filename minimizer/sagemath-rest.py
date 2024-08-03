from sage.all import *

import itertools as it
import subprocess
import datetime
import os
import inspect
import sys
import time
import timeit
from timeit import Timer

from flask import Flask
from flask_restful import Resource, Api, reqparse

parser = reqparse.RequestParser()

def compute_groebner_basis(str_vars: str, espresso_output: str):
    split = str_vars.split(",")
    R = PolynomialRing(GF(2), "x", len(split))
    bits = R.gens()

    n = len(bits)
    relations = []

    # Parse the minimized output from espresso
    for line in espresso_output.split("\n"):
        if not line or line.startswith("."):
            continue
        var, res = line.split(" ")
        term = 1
        for i in range(len(var)):
            if var[i] == "-":
                continue
            elif var[i] == '1':
                term *= bits[i]
            elif var[i] == '0':
                term *= bits[i] + 1
        relations.append(term)

    idempotency_relations = [bits[i]**2 + bits[i] for i in range(n)]
    relations.extend(idempotency_relations)

    # Compute the groebner basis
    I = R.ideal(relations)
    B = I.groebner_basis()

    return str(B)

class SageMathRoute(Resource):
    def get(self):
        # Define the set of url arguments.
        parser.add_argument("variables", type=str, location='args')
        parser.add_argument("espresso_output", type=str, location='args')
        args = parser.parse_args()

        # List of variables separated by commas, e.g.: x0,x1,x2,x3,x4
        strVars = args["variables"]
        # Espresso PLA input file
        strPLA = args["espresso_output"]

        basis = compute_groebner_basis(strVars, strPLA)

        return basis

def start_api(port):
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(SageMathRoute, '/sage/')
    app.run(threaded=False, debug=False, port=port)
    while True:
        continue

if __name__ == "__main__":
    port = 5000
    start_api(port)
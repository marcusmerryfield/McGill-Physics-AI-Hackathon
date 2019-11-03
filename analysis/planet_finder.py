#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import spatial

def vectorize(data, n, variables, k):
    v = np.zeros(len(variables))
    i = 0
    for key in list(data.keys()):
        v[i] = data[key][k] 
        i += 1
    return v

    
def calculate_minimum_distance(test_vector, vectorized_data):
    md = 1e10
    mdv = None
    min_index = None
    index = 0
    for vector in vectorized_data:
        d = spatial.distance.euclidean(test_vector, vector)
        if d <= md:
            md = d
            mdv = vector
            min_index = index
        index += 1
    return md, mdv, min_index

def get_closest_planet(test_vector):
    baked_fwp = "/Users/azwaniga/McGill-Physics-AI-Hackathon/data/planets_final_data.npz"
    data = np.load(baked_fwp, allow_pickle=True)["arr_0"].item()
    print(data)
    n = 1075  # Number of planets that have all six parameters
    variables = ["pl_pnum", "pl_bmassj", "pl_orbsmax", "pl_orbeccen", "st_mass", "st_teff"]
    vectorized_data = np.zeros([n, len(variables)])
    for k in range(n):
        vectorized_data[k] = vectorize(data, n, variables, k)
    print(vectorized_data)
    results = calculate_minimum_distance(test_vector, vectorized_data)
    closest_planet_data = results[1]
    print("The test vector is {}".format(test_vector))
    print("The minimum distance between the test vector and the data set is {} and the closest point is {} with index {} in the original data set".format(results[0], results[1], results[2]))
    original_data_fwp = "/Users/azwaniga/McGill-Physics-AI-Hackathon/data/planets_2019.11.01_20.07.23_master_data.npz"
    original_data = np.load(original_data_fwp, allow_pickle=True)["arr_0"]
    checks = []
    found_item = None
    for item in original_data:
        i = 0
        for var in variables:
            if item[var] != "":
                if float(item[var]) == closest_planet_data[i]:
                    checks.append(True) 
        i += 1
        if len(checks) == 6:
            found_item = item
            print(found_item)
    print("The name of the planet is {}".format(found_item["pl_name"]))

if __name__ == "__main__":
    # test_vector = [1., 1.34845361, 5.1521304, 0., 1.0734717, 0.4176236]
    get_closest_planet(test_vector)

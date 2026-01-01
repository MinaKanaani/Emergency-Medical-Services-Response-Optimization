# genetic_algorithm.py
"""
Genetic Algorithm (GA) that optimizes the EMS repositioning table.

This file IMPORTS the simulation fitness function from simulation.py
so we do NOT repeat the simulation code.

Run:
    python genetic_algorithm.py

It saves plots in /outputs.
"""

import os
import random
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

from simulation import fitness_function  # <-- key idea: reuse simulation code, no duplication

SEED = 31
random.seed(SEED)
np.random.seed(SEED)

# Cache for expensive fitness evaluations
score_cache = {}


def initialize_population(pop_size, th, n_stations):
    population = []
    for _ in range(pop_size):
        individual = []
        code_counter = Counter()
        while len(individual) < (th - 1):
            new_code = random.randint(1, n_stations)
            if code_counter[new_code] < 2:  # limit repeats (you can tune this)
                individual.append(new_code)
                code_counter[new_code] += 1
        population.append(individual)
    return population


def get_fitness(individual, th, n_ambulance, n_stations):
    key = tuple(individual)
    if key in score_cache:
        return score_cache[key]

    metrics = fitness_function(individual, th, n_ambulance, n_stations, iterations=3)
    score = metrics["median_response_time"]  # minimize
    score_cache[key] = score
    return score


def tournament_selection(population, fitness_scores, tournament_size=3):
    parents = []
    for _ in range(2):
        idxs = random.sample(range(len(population)), tournament_size)
        best_idx = min(idxs, key=lambda i: fitness_scores[i])  # lower fitness is better
        parents.append(population[best_idx])
    return parents


def elitism(population, fitness_scores, elitism_count=1):
    paired = sorted(zip(population, fitness_scores), key=lambda x: x[1])
    return [ind for ind, _ in paired[:elitism_count]]


def crossover(parent1, parent2, prob=0.7):
    if random.random() <= prob and len(parent1) > 1:
        p = random.randint(1, len(parent1) - 1)
        return parent1[:p] + parent2[p:]
    return random.choice([parent1, parent2]).copy()


def mutate(individual, mutation_rate, n_stations):
    child = individual.copy()
    for i in range(len(child)):
        if random.random() < mutation_rate:
            child[i] = random.randint(1, n_stations)
    return child


def genetic_algorithm(pop_size, n_ambulance, n_stations, generations, mutation_rate, elitism_count, crossover_prob, th):
    population = initialize_population(pop_size, th, n_stations)
    best_progress = []

    for gen in range(generations):
        fitness_scores = [get_fitness(ind, th, n_ambulance, n_stations) for ind in population]
        elites = elitism(population, fitness_scores, elitism_count)

        children = []
        while len(children) < pop_size - elitism_count:
            p1, p2 = tournament_selection(population, fitness_scores, tournament_size=3)
            child = crossover(p1, p2, crossover_prob)
            child = mutate(child, mutation_rate, n_stations)
            children.append(child)

        population = elites + children

        # track best
        fitness_scores = [get_fitness(ind, th, n_ambulance, n_stations) for ind in population]
        best_idx = int(np.argmin(fitness_scores))
        best_score = float(fitness_scores[best_idx])
        best_progress.append(best_score)

        print(f"Generation {gen+1}/{generations} — Best median RT: {best_score:.3f} min")

    best_idx = int(np.argmin([get_fitness(ind, th, n_ambulance, n_stations) for ind in population]))
    best_individual = population[best_idx]
    best_score = float(get_fitness(best_individual, th, n_ambulance, n_stations))

    return best_individual, best_score, best_progress


def save_outputs(best_progress, best_individual, th, n_stations, outdir="outputs"):
    os.makedirs(outdir, exist_ok=True)

    # 1) GA progress plot
    plt.figure(figsize=(8, 5))
    plt.plot(best_progress, marker="o")
    plt.title("GA Progress: Best Fitness per Generation (Synthetic Demo)")
    plt.xlabel("Generation")
    plt.ylabel("Best Median Response Time (min)")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "ga_fitness_progress.png"), dpi=200)
    plt.close()

    # 2) Best chromosome frequency
    counts = Counter(best_individual)
    xs = list(range(1, n_stations + 1))
    ys = [counts.get(x, 0) for x in xs]

    plt.figure(figsize=(9, 5))
    plt.bar(xs, ys, edgecolor="black")
    plt.title("Best GA Solution: Station Frequency in Chromosome (Synthetic Demo)")
    plt.xlabel("Station ID")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "best_solution_station_frequency.png"), dpi=200)
    plt.close()


def main():
    th = 17
    pop_size = 60
    n_ambulance = 16
    n_stations = 17
    generations = 15
    mutation_rate = 0.20
    crossover_prob = 0.70
    elitism_count = 1

    start = time.time()
    best_solution, best_score, best_progress = genetic_algorithm(
        pop_size, n_ambulance, n_stations, generations, mutation_rate, elitism_count, crossover_prob, th
    )

    print("\nBest solution (primary list):", best_solution)
    print("Best fitness (median RT):", best_score)

    # Optional: also print extra metrics for the best solution (still synthetic)
    metrics = fitness_function(best_solution, th, n_ambulance, n_stations, iterations=3)
    print("Best solution metrics:", metrics)

    save_outputs(best_progress, best_solution, th, n_stations, outdir="outputs")

    elapsed = time.time() - start
    print(f"\nDone. Elapsed: {elapsed:.2f} seconds")
    print("Saved figures to outputs/")


if __name__ == "__main__":
    main()

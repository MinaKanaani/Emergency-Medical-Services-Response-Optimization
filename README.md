# EMS Response Time Optimization (Simulation + Genetic Algorithm)

This repository contains a discrete-event EMS simulation and a Genetic Algorithm (GA) that searches for improved ambulance repositioning strategies.  
The goal is to reduce response time (and optionally improve coverage and system reliability) by optimizing repositioning rules under fluctuating demand.

## What’s in this repo

- **simulation.py**
  - Implements the EMS discrete-event simulation and the core `fitness_function(...)`.
  - The fitness function evaluates a candidate repositioning strategy by running the simulation and returning performance metrics (e.g., median response time, coverage ≤ 9 minutes, lost calls).

- **genetic_algorithm.py**
  - Implements a GA (tournament selection + crossover + mutation + elitism).
  - Calls the simulation fitness function to score candidate solutions.
  - Uses **caching** so repeated solutions do not re-run expensive simulations.

## The key idea (plain language)

A repositioning strategy is represented as a list of station IDs (a chromosome).  
That list is converted into a repositioning table (rules for where idle units should move when system availability drops below a threshold).

The GA works like this:
1. Create many random strategies (population)
2. Evaluate each strategy using the simulation (fitness function)
3. Keep the best strategies (elitism)
4. Mix strategies (crossover)
5. Slightly change strategies (mutation)
6. Repeat for many generations until performance improves

## Outputs (what you’ll see)

This repo can generate:
- **GA Fitness Progress**: best fitness score per generation
- **Best Solution Station Frequency**: which stations appear most in the best strategy

> Note: This public version is designed to be **data-safe**. It can be run with synthetic/demo inputs.
> Private or restricted datasets are not included in this repository.

## How to run

```bash
python genetic_algorithm.py

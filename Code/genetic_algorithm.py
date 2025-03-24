from random import choices, randint, randrange, random, sample
from typing import List, Callable, Tuple

Individual = List[int]
Population = List[Individual]
FitnessFunc = Callable[[Individual], int]


def generate_individual(length: int) -> Individual:
    return choices([0, 1], k=length)


def one_point_crossover(a: Individual, b: Individual) -> Tuple[Individual, Individual]:
    if len(a) != len(b):
        raise ValueError("Individuals a and b must be of same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]


def mutation(individual: Individual, num: int = 1, probability: float = 0.5) -> Individual:
    for _ in range(num):
        index = randrange(len(individual))
        individual[index] = individual[index] if random() > probability else abs(individual[index] - 1)
    return individual


def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return sample(
        population=generate_weighted_distribution(population, fitness_func),
        k=2
    )


def generate_weighted_distribution(population: Population, fitness_func: FitnessFunc) -> Population:
    result = []

    for gene in population:
        result += [gene] * int(fitness_func(gene)+1)

    return result


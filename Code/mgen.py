import click
from datetime import datetime
from typing import List, Dict
from midiutil import MIDIFile
from pyo import *
import random

from genetic_algorithm import Individual, generate_individual, selection_pair, one_point_crossover, mutation

'''
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]
'''
BITS_PER_NOTE = 4
GENRE_PARAMETERS = {
    "rock": {"num_bars": 10, "num_notes": 8, "num_steps": 1,
             "pauses": True, "key": "G", "scale": "minorBlues", "root": 3, "bpm": 180},
    "house": {"num_bars": 16, "num_notes": 4, "num_steps": 3,
              "pauses": False, "key": "F", "scale": "minorM", "root": 3, "bpm": 100},
    "Vivaldi": {"num_bars": 12, "num_notes": 8, "num_steps": 2,
                "pauses": False, "key": "C", "scale": "major", "root": 4, "bpm": 200},
    "Mozart": {"num_bars": 16, "num_notes": 6, "num_steps": 2,
               "pauses": False, "key": "C", "scale": "major", "root": 3, "bpm": 100},
}


def int_from_bits(bits: List[int]) -> int:
    return int(sum([bit * pow(2, index) for index, bit in enumerate(bits)]))


def individual_to_melody(individual: Individual, num_bars: int, num_notes: int, num_steps: int,
                         pauses: int, key: str, scale: str, root: int) -> Dict[str, list]:
    notes = [individual[i * BITS_PER_NOTE:i * BITS_PER_NOTE + BITS_PER_NOTE] for i in range(num_bars * num_notes)]
    note_length = 4 / float(num_notes)

    scl = EventScale(root=key, scale=scale, first=root)
    melody = {
        "notes": [],
        "velocity": [],
        "beat": []
    }

    for note in notes:
        integer = int_from_bits(note)

        if not pauses:
            integer = int(integer % pow(2, BITS_PER_NOTE - 1))

        # Pauses are introduced with a 20% probability
        if random.uniform(0, 1) <= 0.2 and pauses is True:
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]
        else:
            if len(melody["notes"]) > 0 and melody["notes"][-1] == integer:
                melody["beat"][-1] += note_length
            else:
                melody["notes"] += [integer]
                melody["velocity"] += [127]
                melody["beat"] += [note_length]

    steps = []
    for step in range(num_steps):
        steps.append([scl[(note + step * 2) % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps
    return melody


def individual_to_events(individual: Individual, num_bars: int, num_notes: int, num_steps: int,
                         pauses: bool, key: str, scale: str, root: int, bpm: int) -> [Events]:
    melody = individual_to_melody(individual, num_bars, num_notes, num_steps, pauses, key, scale, root)

    return [
        Events(
            midinote=EventSeq(step, occurrences=1),
            midivel=EventSeq(melody["velocity"], occurrences=1),
            beat=EventSeq(melody["beat"], occurrences=1),
            attack=0.001,
            decay=0.05,
            sustain=0.5,
            release=0.005,
            bpm=bpm
        ) for step in melody["notes"]
    ]


def fitness(individual: Individual, s: Server, num_bars: int, num_notes: int, num_steps: int,
            pauses: bool, key: str, scale: str, root: int, bpm: int, melody_index: int) -> int:
    fitness_events = individual_to_events(individual, num_bars, num_notes, num_steps, pauses, key, scale, root, bpm)
    for e in fitness_events:
        e.play()
    s.start()

    rating = input(f"Rating melody {melody_index} (0-5): ")

    for e in fitness_events:
        e.stop()
    s.stop()
    time.sleep(1)

    try:
        rating = int(rating)
    except ValueError:
        rating = 0

    return rating


def save_individual_to_midi(filename: str, individual: Individual, num_bars: int, num_notes: int, num_steps: int,
                            pauses: bool, key: str, scale: str, root: int, bpm: int):
    melody = individual_to_melody(individual, num_bars, num_notes, num_steps, pauses, key, scale, root)

    if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
        raise ValueError

    mf = MIDIFile(1)

    track = 0
    channel = 0

    midi_time = 0.0
    mf.addTrackName(track, midi_time, "Sample Track")
    mf.addTempo(track, midi_time, bpm)

    for i, vel in enumerate(melody["velocity"]):
        if vel > 0:
            for step in melody["notes"]:
                mf.addNote(track, channel, step[i], midi_time, melody["beat"][i], vel)

        midi_time += melody["beat"][i]

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)


@click.command()
@click.option("--population-size", default=10, prompt='Population size:', type=int)
@click.option("--num-mutations", default=2, prompt='Number of mutations:', type=int)
@click.option("--mutation-probability", default=0.5, prompt='Mutations probability:', type=float)
@click.option("--genre", prompt='Choose a genre:', type=click.Choice(GENRE_PARAMETERS.keys()))
def main(genre: str, population_size: int, num_mutations: int, mutation_probability: float):
    folder = genre + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    parameters = GENRE_PARAMETERS[genre]
    (num_bars, num_notes, num_steps,
     pauses, key, scale, root, bpm) = (
        parameters["num_bars"], parameters["num_notes"], parameters["num_steps"],
        parameters["pauses"], parameters["key"], parameters["scale"], parameters["root"], parameters["bpm"]
    )

    population = [generate_individual(num_bars * num_notes * BITS_PER_NOTE) for _ in range(population_size)]
    population_id = 0

    s = Server().boot()

    running = True
    while running:
        population_fitness = []
        random.shuffle(population)
        allIndividuals = []

        for i, individual in enumerate(population):
            allIndividuals.append(individual)
            fitness_value = fitness(individual, s, num_bars, num_notes, num_steps, pauses, key, scale, root, bpm, i)
            population_fitness.append((individual, fitness_value))

        sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)

        population = [e[0] for e in sorted_population_fitness]

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):

            def fitness_lookup(individual):
                for e in population_fitness:
                    if e[0] == individual:
                        return e[1]
                return 0

            parents = selection_pair(population, fitness_lookup)
            offspring_a, offspring_b = one_point_crossover(parents[0], parents[1])
            offspring_a = mutation(offspring_a, num=num_mutations, probability=mutation_probability)
            offspring_b = mutation(offspring_b, num=num_mutations, probability=mutation_probability)
            next_generation += [offspring_a, offspring_b]

        print(f"Population {population_id} evaluation finished.")

        eval_events = individual_to_events(population[0], num_bars, num_notes, num_steps, pauses, key, scale, root, bpm)
        for e in eval_events:
            e.play()
        s.start()
        idx = allIndividuals.index(population[0])
        print(f"This is the first melody proposition (melody {idx}).")
        input()
        s.stop()
        for e in eval_events:
            e.stop()

        time.sleep(1)

        eval_events = individual_to_events(population[1], num_bars, num_notes, num_steps, pauses, key, scale, root, bpm)
        for e in eval_events:
            e.play()
        s.start()
        idx = allIndividuals.index(population[1])
        input(f"This is the second melody proposition (melody {idx}).")
        s.stop()
        for e in eval_events:
            e.stop()

        time.sleep(1)

        print("Processing midi population.")
        for i, individual in enumerate(population):
            save_individual_to_midi(f"{folder}/{population_id}/{scale}-{key}-{i}.mid", individual, num_bars, num_notes,
                                    num_steps, pauses, key, scale, root, bpm)
        print("Evaluation finished.")

        running = input("Want to continue? [Y/n]") != "n"
        population = next_generation
        population_id += 1


if __name__ == '__main__':
    main()
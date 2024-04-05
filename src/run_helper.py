import sys
from random import shuffle, random
import math

def get_sequence(queries: list, query_priorities: dict) -> list:
    base = 5
    
    dist = tuple(distribution(priority, base) for priority in query_priorities.values())
    zero_priority_query = []
    positive_priority_query = []
    negative_priority_query = []
    for query in queries:
        match query_priorities[query[0]]:
            case 0:
                zero_priority_query.append(query)
            case x if x > 0:
                positive_priority_query.append(query)
            case _:
                negative_priority_query.append(query)
    
    shuffle(zero_priority_query)
        
    return (zero_priority_query + 
            weight_shuffle(positive_priority_query, tuple(filter(lambda x: x != float('inf') and x > 0, dist))) +
            weight_shuffle(negative_priority_query, tuple(filter(lambda x: x < 0, dist))))

def distribution(priority: int, base: int) -> float:
    positive_priority = abs(priority)
    
    if priority == 0:
        return float('inf')
    
    return positive_priority // priority * min(positive_priority, base) * min(1, math.log(positive_priority + 1, base))
    
def weight_shuffle(items: list, weights: list) -> list:
    if len(items) != len(weights):
        raise ValueError('items and weights must have the same length')
    if not (items or weights):
        return []
    
    # https://utopia.duth.gr/%7Epefraimi/research/data/2007EncOfAlg.pdf
    # https://softwareengineering.stackexchange.com/questions/233541/how-to-implement-a-weighted-shuffle
    
    order = sorted(range(len(items)), key=lambda i: random() ** (weights[i] ** -1), reverse=True)
    return [items[i] for i in order]

def update_priority_to_file(filename: str, key: str, priority: int):
    with open(filename, 'r+', encoding='utf-8') as f:
        content = f.readlines()
        for i, line in enumerate(content):
            _, word = line.split(' | ')
            
            word = word.strip()
            
            if word == key:
                content[i] = f'{priority} | {word}\n'
                break
        else:
            raise ValueError(f'{key} is not found in {filename}')
        
        f.seek(0)
        f.writelines(content)
        f.truncate()
        
def get_updated_priority(is_know_word: bool, priority: int) -> int:
    i_dont_know_it = {
        -5: 1,
        -4: 1,
        -3: 1,
        -2: 1,
        -1: 2,
        0: 1,
        1: 2,
        2: 4,
        3: 5,
        4: 5,
        5: 5
    }
    i_know_it = {
        -5: -5,
        -4: -5,
        -3: -5,
        -2: -4,
        -1: -2,
        0: -1,
        1: -1,
        2: -1,
        3: 1,
        4: 2,
        5: 3
    }
    
    return i_know_it.get(priority, -5) if is_know_word else i_dont_know_it.get(priority, 5)

def process_input(priority: int, input_string: str | None = None) -> int:
    inp = input(f'{input_string if input_string else ""}\n')
    
    while True:
        if inp == 'y':
            return get_updated_priority(True, priority)
        elif inp == 'n':
            return get_updated_priority(False, priority)
        elif inp == 'q':
            sys.exit();

        inp = input("<y|n|q>")
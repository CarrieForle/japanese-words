import sys
import re
from random import random, shuffle
from pathlib import Path
import math

class ParsedData:
    def __init__(self):
        self.__mode = 'desc'
        self.__file = 'README.md'
        self.__is_help = False

    @property
    def mode(self):
        return self.__mode
    
    @mode.setter
    def mode(self, value):
        self.__mode = value

    @property
    def file(self):
        return self.__file
    
    @file.setter
    def file(self, value):
        self.__file = value

    @property
    def is_help(self):
        return self.__is_help
    
    @is_help.setter
    def is_help(self, value):
        self.__is_help = value
        
def parse_arg(argv: list) -> ParsedData: 
    pd = ParsedData()
    arg_is_value = ''

    for arg in argv:

        match arg_is_value:
            case 'mode':
                if arg in ['desc', 'pron']:
                    pd.mode = arg
                    arg_is_value = ''
                else:
                    raise ValueError('invalid mode')
                continue

        is_use_equal_syntax = False
        
        if len((arg_and_value := arg.split('='))) == 2:
            is_use_equal_syntax = True
            arg_value = arg_and_value[1]

        match arg:
            case '-m' | '--mode':
                if is_use_equal_syntax:
                    pd.mode = arg_value
                    is_use_equal_syntax = False
                else:
                    arg_is_value = 'mode'
            case '-h' | '-?' | '--help':
                pd.is_help = True
            case _:
                if pd.file == 'README.md':
                    pd.file = arg
                else:
                    raise ValueError('too many arguments')

    return pd

def run(mode: str, file: str):
    with open(file, 'r', encoding='utf-8') as f:
        file_content = f.readlines()
    
    file_content = filter((lambda s: not (
            any(s.startswith(ch) for ch in '#!>') or s.strip() == '')),
            file_content)
    
    queries = []
    
    jw_filename = f'.jw_{file}'
   
    jw_file_exist = Path(jw_filename).exists()
    query_priorities = {}
    
    if jw_file_exist:
        with open(jw_filename, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if not line.strip():
                    continue
                priority, word = line.split(' | ')
                query_priorities[word.strip()] = int(priority)
    else:
        with open(jw_filename, 'x', encoding='utf-8') as _:
            pass
    
    words = []
    one_or_more_entries_of_word_list_is_modified = False
    
    for query in file_content:
        if ms := re.finditer(r'(?P<whole>\[(?P<original_text>.+?)\]\(.*?\))', query):
            for m in ms:
                query = query.replace(m.group('whole'), m.group('original_text'))
        
        if len(sp := query.split('（', 1)) > 1:
            word = sp[0]
            pronunciation, description = sp[1].split('）', 1)
            
        else:
            word, description = query.split(' ', 1)
            pronunciation = word
        
        word = word.strip()
        description = description.strip()
        pronunciation = pronunciation.strip()
        
        if not jw_file_exist or word not in query_priorities:
            query_priorities[word] = 0
            one_or_more_entries_of_word_list_is_modified = True
          
        queries.append((word, pronunciation, description))
        words.append(word)
        
    for word in query_priorities.copy():
        if word not in words:
            del query_priorities[word]
            one_or_more_entries_of_word_list_is_modified = True
    
    del words
    
    if one_or_more_entries_of_word_list_is_modified:
        with open(jw_filename, 'w', encoding='utf-8') as f:
            for key in query_priorities:
                f.write(f'{query_priorities[key]} | {key}\n')
                
    del one_or_more_entries_of_word_list_is_modified
    
    print(f'Loaded {len(queries)} queries')
    
    is_try_again = True
    
    while is_try_again:    
        queries = get_sequence(queries, query_priorities)
        
        for i, query in enumerate(queries):
            last_query = queries[i - 1] if i > 0 else None
            
            match mode:
                case 'desc':
                    has_desc = query[2] != ''
                    if has_desc:
                        if optionals := re.finditer(r'\(.+?\)', query[2]):
                            desc = query[2]
                            for optional in optionals:
                                desc = desc.replace(optional.group(), '')
                            has_desc = desc.strip() != ''
                        
                    if has_desc:
                        if not last_query:
                            if input(query[2] + '\n') == 'q':
                                sys.exit()
                        else:
                            
                            updated_priority = process_input(query_priorities[last_query[0]], query[2])
                            
                            query_priorities[last_query[0]] = updated_priority
                            
                            update_priority_to_file(
                                jw_filename, 
                                last_query[0],
                                updated_priority)
                    else:
                        if not last_query:
                            if input(query[0] + '\n') == 'q':
                                sys.exit()
                        else:
                            updated_priority = process_input(query_priorities[last_query[0]], query[0])
                            
                            query_priorities[last_query[0]] = updated_priority
                            
                            update_priority_to_file(
                                jw_filename, 
                                last_query[0],
                                updated_priority)
                    
                case 'pron':
                    if not last_query:
                        if input(query[1] + '\n') == 'q':
                            sys.exit()
                    else:
                        updated_priority = process_input(query_priorities[last_query[0]], query[1])
                        
                        query_priorities[last_query[0]] = updated_priority
                        
                        update_priority_to_file(
                            jw_filename, 
                            last_query[0],
                            updated_priority)
                    
            print(f'\t{query[0]}', end='')
            if query[0] != query[1]:
                print(f'（{query[1]}）', end='')
            print(f' {query[2]}\n')
                    
                    
        updated_priority = process_input(query_priorities[queries[-1][0]], 'Final input!')
        
        query_priorities[queries[-1][0]] = updated_priority
        
        update_priority_to_file(
            jw_filename, 
            queries[-1][0], 
            updated_priority)
                
        print('You\'ve browsed all the queries. Do you want to try again? [y/n] = ', end='')
        
        while True:
            match input():
                case 'y':
                    is_try_again = True
                    break
                case 'n':
                    is_try_again = False
                    break

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

if __name__ == '__main__':
    try:
        parsed_data = parse_arg(sys.argv[1:])
    except Exception as e:
        print(e)
        sys.exit(1)
    
    if parsed_data.is_help:
        print(f'''
Usage:
  {sys.argv[0]} [options] [<file>]

Arguments:
  <file>  The path of the file to read from. [default: README.md]

Options:
  -m, --mode <desc|pron>  Determine the type of test. Default to description test.
                          [default: desc]''')
        sys.exit()
        
    file = parsed_data.file
    mode = parsed_data.mode

    run(mode, file)
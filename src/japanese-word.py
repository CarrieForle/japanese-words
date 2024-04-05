import sys
import re
from pathlib import Path
from run_helper import *
from cmd_parser import *

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
import sys
import re
from random import shuffle

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

def Run(mode: str, file: str):
    file_content = open(file, 'r', encoding='utf-8').readlines()
    file_content = filter((lambda s: not (
            any(s.startswith(ch) for ch in '#!>') or s.strip() == '')),
            file_content)

    queries = []
    
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
          
        queries.append((word, pronunciation, description))
    
    print(f'Loaded {len(queries)} queries.\n')
    
    is_try_again = True
    
    while is_try_again:    
        shuffle(queries)
        
        for query in queries:
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
                        input(query[2])
                    else:
                        input(query[0])
                        
                    print(f'\n\t{query[0]}', end='')
                    if query[0] != query[1]:
                        print(f'（{query[1]}）', end='')
                    print(f' {query[2]}\n')
                    
                case 'pron':
                    input(query[1])
                    
                    print(f'\n\t{query[0]}', end='')
                    if query[0] != query[1]:
                        print(f'（{query[1]}）', end='')
                    print(f' {query[2]}\n')
        
        print('You\'ve browsed all the queries. Do you want to try again? [y/n] = ', end='')
        
        while True:
            inp = input()
            match inp:
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
        sys.exit(0)
        
    file = parsed_data.file
    mode = parsed_data.mode

    Run(mode, file)

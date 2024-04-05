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

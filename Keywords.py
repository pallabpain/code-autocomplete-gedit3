# Required modules
#
import keyword, builtins
#
#------------------------------------------------------------------------------------------------
# C Language Keywords and commonly used functions 
#
c_keywords_list = ['auto', 'break', 'case', 'char', 'const', 'continue',
				'default', 'do', 'double', 'else', 'enum', 'extern', 
				'float', 'for', 'goto', 'if', 'int', 'long', 'register',
				'return', 'short', 'signed', 'sizeof', 'static', 'struct',
				'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile',
				'while', 'include', 'define', 'main']

c_stdio_list =['clearerr', 'fclose', 'fdopen', 'feof', 'ferror', 'fflush',
			'fgetc', 'fgetpos', 'fgets', 'fileno', 'fopen', 'fprintf', 
			'fpurge', 'fputc', 'fputs', 'fread', 'freopen', 'fscanf',
			'fseek', 'fsetpos', 'ftell', 'fwrite', 'getc', 'getchar',
			'gets', 'getw', 'mktemp', 'perror', 'printf', 'putc',
			'putchar', 'puts', 'putw', 'remove', 'rewind', 'scanf',
			'setbuf', 'setbuffer', 'setlinebuf', 'setvbuf', 'sprintf',
			'sscanf', 'strerror', 'sys_errlist', 'sys_nerr', 'tempnam',
			'tmpfile','tmpnam', 'ungetc', 'vfprintf', 'vfscanf', 'vprintf',
			'vscanf', 'vsprintf', 'vsscanf']

c_list = c_keywords_list + c_stdio_list				
#
# END of C Language Keywords and commonly used functions 
#------------------------------------------------------------------------------------------------
# Python Keywords and Builtins
#
builtins_list = [i for i in dir(builtins) if not (i.startswith('__') and i.endswith('__'))]
python_list = keyword.kwlist + builtins_list + ['self']
#
# End of Python Keywords and Builtins
#------------------------------------------------------------------------------------------------
# Ruby Reserved Words
#
error = ['ArgumentError', 'EOFError', 'FloatDomainError', 'IOError', 
		'IndexError', 'LoadError', 'MysqlError', 'NameError', 
		'NoMemoryError', 'NotImplementedError', 'PGError', 
		'RangeError', 'RegexpError', 'RuntimeError', 'ScanError', 
		'SecurityError', 'SocketError', 'SyntaxError', 
		'SystemStackError', 'ThreadError', 'TypeError', 'ZeroDivisionError']
					
constants = ['ADDITIONAL_LOAD_PATHS', 'ARGF', 'ARGV', 'CGI', 'CROSS_COMPILING',
			'ENV', 'ERB', 'FALSE', 'GC', 'IO', 'LN_SUPPORTED', 'NIL', 
			'OPT_TABLE', 'PLATFORM', 'RAKEVERSION', 'RELEASE_DATE', 'RUBY', 
			'RUBY_PLATFORM', 'RUBY_RELEASE_DATE', 'RUBY_VERSION', 'STDERR', 
			'STDIN', 'STDOUT', 'TOPLEVEL_BINDING', 'TRUE', 'VERSION', 'YAML']

reserved_words = ['ActionController', 'ActionView', 'ActiveRecord', 'ArgumentError', 
			'Array', 'BasicSocket', 'Benchmark', 'Bignum', 'Binding', 
			'CGIMethods', 'Class', 'ClassInheritableAttributes', 'Comparable', 
			'ConditionVariable', 'Config', 'Continuation', 'DRb', 'DRbIdConv', 
			'DRbObject', 'DRbUndumped', 'Data', 'Date', 'DateTime', 
			'Delegater', 'Delegator', 'Digest', 'Dir', 'EOFError', 'Enumerable', 
			'Errno', 'Exception', 'FalseClass', 'Fcntl', 'File', 'FileList', 
			'FileTask', 'FileTest', 'FileUtils', 'Fixnum', 'Float', 
			'FloatDomainError', 'Gem', 'GetoptLong', 'Hash', 'IOError', 
			'IPSocket', 'IPsocket', 'IndexError', 'Inflector', 'Integer', 
			'Interrupt', 'Kernel', 'LoadError', 'LocalJumpError', 'Logger', 
			'Marshal', 'MatchData', 'MatchingData', 'Math', 'Method', 'Module', 
			'Mutex', 'Mysql', 'MysqlError', 'MysqlField', 'MysqlRes', 
			'NameError', 'NilClass', 'NoMemoryError', 'NoMethodError', 'NoWrite', 
			'NotImplementedError', 'Numeric', 'Object', 'ObjectSpace', 'Observable', 
			'Observer', 'PGError', 'PGconn', 'PGlarge', 'PGresult', 'PStore', 
			'ParseDate', 'Precision', 'Proc', 'Process', 'Queue', 'Rack', 'Rake', 
			'RakeApp', 'RakeFileUtils', 'Range', 'RangeError', 'Rational', 'Regexp', 
			'RegexpError', 'Request', 'RuntimeError', 'ScanError', 'ScriptError', 
			'SecurityError', 'Signal', 'SignalException', 'SimpleDelegater', 
			'SimpleDelegator', 'Singleton', 'SizedQueue', 'Socket', 'SocketError', 
			'StandardError', 'String', 'StringScanner', 'Struct', 'Symbol', 
			'SyntaxError', 'SystemCallError', 'SystemExit', 'SystemStackError', 
			'TCPServer', 'TCPSocket', 'TCPserver', 'TCPsocket', 'Task', 'Text', 
			'Thread', 'ThreadError', 'ThreadGroup', 'Time', 'Transaction', 'TrueClass', 
			'TypeError', 'UDPSocket', 'UDPsocket', 'UNIXServer', 'UNIXSocket', 
			'UNIXserver', 'UNIXsocket', 'UnboundMethod', 'Url', 'Verbose', 
			'ZeroDivisionError']

keywords = ['alias', 'and', 'BEGIN', 'begin', 'break', 'case', 'class', 'def', 
		'defined?', 'do', 'else', 'elsif', 'END', 'end', 'ensure', 'false', 
		'for', 'if', 'module', 'next', 'nil', 'not', 'or', 'redo', 'rescue', 
		'retry', 'return', 'self', 'super', 'then', 'true', 'undef', 'unless', 
		'until', 'when', 'while', 'yield', '_ _FILE_ _', 'LINE']
				

ruby_list = keywords + constants + error + reserved_words
#
#
# End of Ruby Reserved Words
#------------------------------------------------------------------------------------------------


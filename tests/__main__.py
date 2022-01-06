from os import scandir, DirEntry
from os.path import dirname

entry: DirEntry
i = 0
for entry in scandir(dirname(__file__)):
    if entry.is_file() and not entry.name.startswith('__') and entry.name.endswith('.py'):
        i += 1
        print(f"{i} Executing test {entry.name}")
        exec(open(entry.path).read())

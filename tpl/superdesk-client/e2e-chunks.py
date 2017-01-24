import sys
from subprocess import check_output, check_call


def chunked_specs(sizes, n):
    names = sorted((k for k, v in sizes), reverse=True)
    sizes = {k: int(v) for k, v in sizes}

    def chunk(names, n):
        if n == 1:
            size = sum(v for k, v in sizes.items() if k in names)
            print('size=%s; files=%s' % (size, names))
            return names

        chunk, size = [], 0
        chunksize = sum(v for k, v in sizes.items() if k in names) / n
        while size < chunksize:
            new_size = size + int(sizes[names[-1]])
            if new_size > chunksize:
                break
            size = new_size
            chunk.append(names.pop())
        print('size=%s; files=%s' % (size, chunk))
        return chunk

    for i in range(n):
        res = chunk(names, n - i)
        if res:
            yield sorted(res)


part = '/var/tmp/specs-part'
check_call('rm -f %s*' % part, shell=True)
sizes = check_output('''
cd /opt/superdesk/client-core;
find spec -type f -name "*spec*.js" -printf '%p\t%s\n' | sort -k2,2n
''', shell=True).decode()
sizes = [i.split() for i in sizes.split('\n') if i]
count = int(sys.argv) if len(sys.argv) == 2 else 2
for num, specs in enumerate(chunked_specs(sizes, count), 1):
    with open(part + str(num), 'w') as f:
        f.write(','.join(specs))

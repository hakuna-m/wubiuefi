# Written by Michael Janssen
# See LICENSE.txt for license information

def fmttime(n, compact = 0):
    if n == -1:
        if compact: 
            return '(no seeds?)'
        else: 
            return 'download not progressing (no seeds?)'
    if n == 0:
        if compact: 
            return "complete"
        else: 
            return 'download complete!'
    n = int(n)
    m, s = divmod(n, 60)
    h, m = divmod(m, 60)
    if h > 1000000:
        return 'n/a'
    if compact: 
        return '%d:%02d:%02d' % (h, m, s)
    else: 
        return 'finishing in %d:%02d:%02d' % (h, m, s)

def fmtsize(n, baseunit = 0, padded = 1):
    unit = [' B', ' K', ' M', ' G', ' T', ' P', ' E', ' Z', ' Y']
    i = baseunit
    while i + 1 < len(unit) and n >= 999:
        i += 1
        n = float(n) / (1 << 10)
    size = ''
    if padded:
        if n < 10:
            size = '  '
        elif n < 100:
            size = ' '
    if i != 0:
        size += '%.1f %s' % (n, unit[i])
    else:
        if padded:
            size += '%.0f   %s' % (n, unit[i])
        else:
            size += '%.0f %s' % (n, unit[i])
    return size


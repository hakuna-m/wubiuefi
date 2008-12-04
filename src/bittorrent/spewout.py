
# This file created for Debian because btdownloadcurses can't 
# find btdownloadheadless because we rename it.

def print_spew(spew):
    s = StringIO()
    s.write('\n\n\n')
    for c in spew:
        s.write('%20s ' % c['ip'])
        if c['initiation'] == 'local':
            s.write('l')
        else:
            s.write('r')
        rate, interested, choked = c['upload']
        s.write(' %10s ' % str(int(rate)))
        if c['is_optimistic_unchoke']:
            s.write('*')
        else:
            s.write(' ')
        if interested:
            s.write('i')
        else:
            s.write(' ')
        if choked:
            s.write('c')
        else:
            s.write(' ')

        rate, interested, choked, snubbed = c['download']
        s.write(' %10s ' % str(int(rate)))
        if interested:
            s.write('i')
        else:
            s.write(' ')
        if choked:
            s.write('c')
        else:
            s.write(' ')
        if snubbed:
            s.write('s')
        else:
            s.write(' ')
        s.write('\n')
    print s.getvalue()

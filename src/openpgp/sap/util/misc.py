"""Realy miscellaneous functions
"""
def unique_order(l, reverse=False):
    """Retrieve unique elements from a list, preserving their order.

    :Parameters:
        - `l`: list
        - `reverse`: False for front to back, True for back to front

    :Returns: list, missing duplicates

    This function does not manipulate the list `l` parameter.
    """
    import copy

    nl = copy.deepcopy(l)

    if reverse == True:
        nl.reverse()

    idx = 0

    while idx < len(nl):

        while nl.count(nl[idx]) > 1:
            found_idx = nl[idx+1:].index(nl[idx]) + idx + 1
            nl.pop(found_idx)

        idx += 1

    if reverse == True:
        nl.reverse()

    return nl

# If the individual lists are normalized, then the order is irrelevant
# since the items in the intersection will be unique to their list.
def order_intersection(L):
    """Order items in an intersection of lists in decreasing popularity.

    :Parameters:
        - `L`: list of lists (must have at least two sublists)

    :Returns: list of common items ordered by frequency descending
        (most popular item at the beginning of the list)
    """
    a = L[0]
    idx = 1

    while idx <= len(L) - 1:
        b = L[idx]
        a = filter(lambda x: (x in a and x in b), a+b)
        idx += 1

    # match candidates with number of votes
    tally = {}

    for c in unique_order(a):
        tally[c] = a.count(c)

    items = tally_dict(tally)

    return [i[0] for i in items]

def tally_dict(d, least_popular_first=False):
    """
    :Parameters:
        - `d`: dictionary - values should be integers, keys can be
          anything
    """
    if least_popular_first:

        def cmp_votes(x, y):

            if x[1] > y[1]:
                return 1

            elif x[1] == y[1]:
                return 0

            elif x[1] < y[1]:
                return -1
    else:

        def cmp_votes(x, y):

            if x[1] < y[1]:
                return 1

            elif x[1] == y[1]:
                return 0

            elif x[1] > y[1]:
                return -1

    items = d.items()
    items.sort(cmp_votes)

    return items

# Since "prepared" sets are all unique intersects, they should all be the same
# length, allowing for an item rank-by-index.
def intersect_order(L):
    """
    """
    normalized = map(unique_order, L) # ensure sublists don't have duplicates
    shared = order_intersection(normalized) # shared items, order irrelevant
    tally = {}

    for set in normalized: # reduce sets to shared values, preserving orders
        s = filter(lambda x: x in shared, set)

        for idx in range(len(s)):

            if s[idx] in tally:
                tally[s[idx]] += idx

            else:
                tally[s[idx]] = idx

    items = tally_dict(tally, True) 

    return [i[0] for i in items]

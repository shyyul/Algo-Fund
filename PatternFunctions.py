__author__ = 'wuyuao'

# define constants
ROOT_ID = -1
FAKE_TRDRNG = {'lvl': -1, 'id': ROOT_ID, 'type': 'X', 'dir': 0,
               'high': 0, 'low': 0, 'pivot': 0, 'from': 0, 'to': 0,
               'start_id': ROOT_ID, 'turn_id': ROOT_ID,
               'total_len': 0, 'turn_len': 0, 'turn_height': 0.0,
               'conso_count': 0, 'avg_conso_len': 0, 'avg_conso_height': 0.0,
               'sib_id': ROOT_ID, 'sib_lvl': -1}

# create the short code for the pattern
def createShortCode(current):
    type_str = str(current['type'])
    startId_str = str(current['start_id'])
    if (current['dir'] > 0):
        dir_str = ',u'
    elif (current['dir'] < 0):
        dir_str = ',d'
    else:
        dir_str = ',e'

    shortCode = type_str + startId_str + dir_str
    return shortCode

def printShortCode(date, shortCodes):
    printStr = date + ": "
    for shortCode in shortCodes:
        printStr = printStr +'  '+shortCode
    print(printStr)
    return

# whether sib T/TR has larger conso levels than current:
def _largerConso(sib, current):
        if (sib['conso_count'] == 0):
            return False
        elif (current['conso_count'] == 0):
            return True
        elif (sib['avg_conso_height'] > (current['avg_conso_height'] * 2) and
                    current['avg_conso_len'] <= (sib['avg_conso_len'] * 2)):
            return True
        elif (sib['avg_conso_len'] > (current['avg_conso_len'] * 2) and
                    current['avg_conso_height'] <= (sib['avg_conso_height'] * 2)):
            return True
        else:
            return False

# whether sib pattern breaks out of current pattern
def _breaks(sib, current):
    if (current['type'] == 'R'):
        top = current['top']
        bottom = current['bottom']
    else:
        top = current['high']
        bottom = current['low']

    if (sib['type'] <> 'R'):
        if (sib['dir'] > 0):
            sib_to = sib['high']
            sib_from = sib['low']
        else:
            sib_to = sib['low']
            sib_from = sib['high']
    elif (sib['dir'] > 0):
        sib_to = sib['top']
        sib_from = sib['bottom']
    else:
        sib_to = sib['bottom']
        sib_from = sib['to']

    if (sib['id'] > current['id']):
        orderDir = 1
    else:
        orderDir = -1

    if (orderDir == 1):
        sib_pivot = (current['pivot'] + sib_to) / 2.0
    else:
        sib_pivot = (current['pivot'] + sib_from) / 2.0

    if (sib['type'] == 'R'):
        if (sib_pivot <= top and sib_pivot >= bottom):
            return False
        else:
            return True
    else:
        if (sib_pivot > top and sib['dir'] * orderDir > 0):
            return True
        elif (sib_pivot < bottom and sib['dir'] * orderDir < 0):
            return True
        else:
            return False


# whether parent pattern completely includes the child pattern in its range
def _includes(parent, child):
    if (_breaks(parent, child) and not(_breaks(child, parent))):
        return True
    else:
        return False

# ?(t/tr) + T/TR = T/TR or ?(<T) + r = r
def tryExpand(current, patterns_series):

    current_lvl = current['lvl']
    sib_id = current['sib_id']
    sib_lvlCount = patterns_series[sib_id]['lvlCount']

    if (sib_id == ROOT_ID):
        return current


    if (current['type'] == 'R'):
        sib_lvl = 0
        sib = patterns_series[sib_id]['list'][sib_lvl]
        while (not(_breaks(sib, current)) and sib_lvl <= sib_lvlCount):
            sib_lvl += 1
            if (sib_lvl <= sib_lvlCount):
                sib = patterns_series[sib_id]['list'][sib_lvl]

        neph_lvl = sib_lvl - 1
        if (neph_lvl < 0):
            return current
        else:
            neph = patterns_series[sib_id]['list'][neph_lvl]
            current['lvl'] -= 1
            expanded = combine(neph, current, patterns_series)
            return tryExpand(expanded, patterns_series)

    else:
        extend_lvl = -1
        sib_lvl = 0
        sib = patterns_series[sib_id]['list'][sib_lvl]
        while (((sib['type'] <> 'R' and (sib['dir'] == current['dir'])) or _includes(current, sib))
               and sib_lvl <= sib_lvlCount and not(_largerConso(sib, current))):
            if (sib['type'] <> 'R' and (sib['dir'] == current['dir'])):
                extend_lvl = sib_lvl
            sib_lvl += 1
            if (sib_lvl <= sib_lvlCount):
                sib = patterns_series[sib_id]['list'][sib_lvl]

        if (extend_lvl >= 0):
            sib = patterns_series[sib_id]['list'][extend_lvl]
            current['lvl'] -= 1
            expanded = extend(sib, current, patterns_series)
            return tryExpand(expanded, patterns_series)
        else:
            return current

def merge(sib, current):

    if (current['type'] == 'R'):
        cur_top = current['top']
        cur_bottom = current['bottom']
    else:
        cur_top = current['high']
        cur_bottom = current['low']

    sib_top = sib['high']
    sib_bottom = sib['low']

    new_top = min(cur_top, sib_top)
    new_bottom = max(cur_bottom, sib_bottom)

    new_pivot = (new_top + new_bottom) / 2.0

    new_high = max(sib['high'], current['high'])
    new_low = min(sib['low'], current['low'])

    merged = {'lvl': max(sib['lvl'], current['lvl']), 'id': current['id'], 'type': 'R', 'dir': sib['dir'],
              'high': new_high, 'low': new_low,
              'pivot': new_pivot,
              'from': new_pivot, 'to': new_pivot,
              'top': new_top, 'bottom': new_bottom,
              'start_id': sib['start_id'], 'turn_id': current['start_id'],
              'total_len': sib['total_len'] + current['total_len'], 'turn_len':  current['total_len'],'turn_height': 0.0,
              'conso_count': 1, 'avg_conso_len': sib['total_len'] + current['total_len'],
              'avg_conso_height': new_high - new_low,
              'sib_id': sib['sib_id'], 'sib_lvl': sib['sib_lvl']}
    return merged

# t'/t'r + t/tr = R or t/tr + r = R or  or t'/t'r/r + T = R or t'/t'r/r + R = R
def combine(sib, current, patterns_series):

    if (current['type'] == 'R'):
        cur_top = current['top']
        cur_bottom = current['bottom']
    else:
        cur_top = current['high']
        cur_bottom = current['low']
    cur_pivot = (cur_top + cur_bottom) / 2.0
    cur_from = cur_pivot
    cur_to = cur_pivot

    merged = {'lvl': current['lvl'], 'id': current['id'], 'type': current['type'], 'dir': current['dir'],
              'high': current['high'], 'low': current['low'],
              'pivot': cur_pivot, 'from': cur_from, 'to': cur_to,
              'top': cur_top, 'bottom': cur_bottom,
              'start_id': current['start_id'], 'turn_id': current['turn_id'],
              'total_len': current['total_len'], 'turn_len':  current['turn_id'], 'turn_height': current['turn_height'],
              'conso_count': current['conso_count'], 'avg_conso_len': current['avg_conso_len'],
              'avg_conso_height': current['avg_conso_height'],
              'sib_id': current['sib_id'], 'sib_lvl': current['sib_lvl']}
    merged_dir = merged['dir']
    merged_id = merged['start_id']

    while (merged_id > sib['start_id']):
        next_id = merged_id - 1
        lvlCount = patterns_series[next_id]['lvlCount']
        next_lvl = lvlCount
        next = patterns_series[next_id]['list'][next_lvl]
        while (next_lvl >= 0 and not(next['start_id'] >= sib['start_id'] and next['type'] <> 'R'
                                    and next['dir'] == -merged_dir and not(_includes(merged, next)))):
            next_lvl -= 1
            if (next_lvl >= 0):
                next = patterns_series[next_id]['list'][next_lvl]

        if (next_lvl < 0):
            merged_id = sib['start_id']
        else:
            merged = merge(next, merged)
            merged_id = merged['start_id']

    new_high = max(sib['high'], merged['high'])
    new_low = min(sib['low'], merged['low'])

    parent = {'lvl': max(merged['lvl'], current['lvl'] + 1), 'id': merged['id'], 'type': 'R', 'dir': merged['dir'],
              'high': new_high, 'low': new_low,
              'pivot': merged['pivot'], 'from': merged['from'], 'to': merged['to'],
              'top': merged['top'], 'bottom': merged['bottom'],
              'start_id': sib['start_id'], 'turn_id': merged['turn_id'],
              'total_len': sib['total_len'] + current['total_len'], 'turn_len':  merged['turn_id'], 'turn_height': 0.0,
              'conso_count': 1, 'avg_conso_len': sib['total_len'] + current['total_len'],
              'avg_conso_height': new_high - new_low,
              'sib_id': sib['sib_id'], 'sib_lvl': sib['sib_lvl']}

    return parent

# find pattern that ends on endID and starts at or before given startID
def findPattern(endID, startID, pattern_series):
    lvl = 0
    pattern = pattern_series[endID]['list'][lvl]
    lvlCount = pattern_series[endID]['lvlCount']
    while (pattern['start_id'] > startID):
        lvl += 1
        if (lvl > lvlCount):
            print(endID, startID)
        pattern = pattern_series[endID]['list'][lvl]

    return pattern

# T/TR + t/tr = T/Tr
def extend(sib, current, patterns_series):
    if (current['type'] == 'TR'):
        turn_id = current['turn_id']
        turn_len = current['turn_len']
        turn_height = current['turn_height']
    else:
        turn_id = ROOT_ID
        turn_len = 0
        turn_height = 0.0


    if (current['conso_count'] > 0):
        sib_conso_count = sib['conso_count']
        sib_conso_len = sib['avg_conso_len']
        sib_conso_height = sib['avg_conso_height']


        new_conso_len = current['avg_conso_len']
        new_conso_height = current['avg_conso_height']

        if (sib_conso_count == 0):
            conso_count = 1
            avg_conso_len = new_conso_len
            avg_conso_height = new_conso_height
            conso_lvl_adj = 1

        elif (((sib_conso_len > (new_conso_len * 2) and (sib_conso_height * 2) >= new_conso_height)) or
            ((sib_conso_height > (new_conso_height * 2) and (sib_conso_len * 2) >= new_conso_len))):
            conso_count = sib['conso_count']
            avg_conso_len = sib['avg_conso_len']
            avg_conso_height = sib['avg_conso_height']
            conso_lvl_adj = 0
        elif (((new_conso_len > (sib_conso_len * 2) and (new_conso_height * 2) >= sib_conso_height)) or
            ((new_conso_height > (sib_conso_height * 2) and (new_conso_len * 2) >= sib_conso_len))):
            conso_count = 1
            avg_conso_len = new_conso_len
            avg_conso_height = new_conso_height
            conso_lvl_adj = 1
        else:
            conso_count = sib_conso_count + 1
            avg_conso_len = float(sib_conso_len * sib_conso_count + new_conso_len) / conso_count
            avg_conso_height = float(sib_conso_height * sib_conso_count + new_conso_height) / conso_count
            conso_lvl_adj = 0
    else:
        conso_count = sib['conso_count']
        avg_conso_len = sib['avg_conso_len']
        avg_conso_height = sib['avg_conso_height']
        conso_lvl_adj = 0

    parent = {'lvl': max(sib['lvl'] + conso_lvl_adj, current['lvl'] + 1), 'id': current['id'], 'type': current['type'], 'dir': sib['dir'],
              'high': max(sib['high'], current['high']), 'low': min(sib['low'], current['low']),
              'pivot': (sib['from'] + current['to']) / 2.0,
              'from': sib['from'], 'to': current['to'],
              'top': current['top'], 'bottom': current['bottom'],
              'start_id': sib['start_id'], 'turn_id': turn_id,
              'total_len': sib['total_len'] + current['total_len'], 'turn_len': turn_len, 'turn_height': turn_height,
              'conso_count': conso_count, 'avg_conso_len': avg_conso_len, 'avg_conso_height': avg_conso_height,
              'sib_id': sib['sib_id'], 'sib_lvl': sib['sib_lvl']}

    return parent

# T'/T'R + t = T'R or T/TR + r = TR
def incTurn(sib, current, patterns_series):
    if (current['type'] == 'T'):
        current_top = current['high']
        current_bottom = current['low']
    else:
        current_top = current['top']
        current_bottom = current['bottom']

    if (sib['type'] == 'T'):
            new_top = current_top
            new_bottom = current_bottom
            turn_id = sib['id'] + 1
    else:
        new_top = min(current_top, sib['top'])
        new_bottom = max(current_bottom, sib['bottom'])
        turn_id = sib['turn_id']

    new_to = (new_top + new_bottom) / 2.0

    if (sib['type'] == 'T'):
        conso_count = 1
        conso_len = current['total_len']
        conso_height = current['high'] - current['low']
        new_conso_height = conso_height
        conso_lvl_adj = 0
    else:
        sib_conso_count = sib['conso_count']
        sib_conso_len = sib['avg_conso_len']
        sib_conso_height = sib['avg_conso_height']

        new_R = findPattern(current['sib_id'], sib['turn_id'], patterns_series)

        new_conso_len = sib['turn_len'] + current['total_len']
        new_conso_height = max(new_R['high'], current['high']) - min(new_R['low'], current['low'])

        if (((sib_conso_len > (new_conso_len * 2) and (sib_conso_height * 2) >= new_conso_height)) or
            ((sib_conso_height > (new_conso_height * 2) and (sib_conso_len * 2) >= new_conso_len))):
            conso_count = sib['conso_count']
            conso_len = sib['avg_conso_len']
            conso_height = sib['avg_conso_height']
            conso_lvl_adj = 0
        elif (((new_conso_len > (sib_conso_len * 2) and (new_conso_height * 2) >= sib_conso_height)) or
            ((new_conso_height > (sib_conso_height * 2) and (new_conso_len * 2) >= sib_conso_len))):
            conso_count = 1
            conso_len = new_conso_len
            conso_height = new_conso_height
            conso_lvl_adj = 1
        else:
            conso_count = sib_conso_count + 1
            conso_len = float(sib_conso_len * sib_conso_count + new_conso_len) / conso_count
            conso_height = float(sib_conso_height * sib_conso_count + new_conso_height) / conso_count
            conso_lvl_adj = 0

    parent = {'lvl': max(sib['lvl'] + conso_lvl_adj, current['lvl'] + 1), 'id': current['id'], 'type': 'TR', 'dir': sib['dir'],
              'high': max(sib['high'], current['high']), 'low': min(sib['low'], current['low']),
              'pivot': (sib['from'] + new_to) / 2.0,
              'from': sib['from'], 'to': new_to,
              'top': new_top, 'bottom': new_bottom,
              'start_id': sib['start_id'], 'turn_id': turn_id,
              'total_len': sib['total_len'] + current['total_len'],
              'turn_len': sib['turn_len'] + current['total_len'], 'turn_height': new_conso_height,
              'conso_count': conso_count, 'avg_conso_len': conso_len, 'avg_conso_height': conso_height,
              'sib_id': sib['sib_id'], 'sib_lvl': sib['sib_lvl']}

    return parent

# create lvl 0 pattern based on single candle
def createLvl0(px_data, stdDev):

    i = px_data['id']
    chgCoC = stdDev['chgCoC']
    prev_close = px_data['close'] - chgCoC

    if (chgCoC > 0):
        cur_dir = 1
    else:
        cur_dir = -1

    pattern = {'lvl': 0, 'id': i, 'type': 'T', 'dir': cur_dir,
               'high': max(prev_close, px_data['close']), 'low': min(prev_close, px_data['close']),
               'pivot': (prev_close + px_data['close']) / 2.0, 'from': prev_close, 'to': px_data['close'],
               'top': px_data['close'],  'bottom': px_data['close'],
               'start_id': i, 'turn_id': ROOT_ID, 'total_len': 1, 'turn_len': 0, 'turn_height': 0.0,
               'conso_count': 0, 'avg_conso_len': 0, 'avg_conso_height': 0.0,
               'sib_id': i - 1, 'sib_lvl': 0}

    return pattern

# find sib and parent for current
def findRelatives(current, patterns_series):
    sib_id = current['sib_id']
    sib_lvlCount = patterns_series[sib_id]['lvlCount']
    lvl = 0
    if (current['type'] == 'T' or current['type'] == 'TR'):
        foundSib = False
        while not(foundSib):
            if (lvl > sib_lvlCount):          #cannot find
                    lvl -= 1
                    sib = patterns_series[sib_id]['list'][lvl]
                    foundSib = True
                    parent = combine(sib, current, patterns_series)
                    parent = tryExpand(parent, patterns_series)
            else:
                sib = patterns_series[sib_id]['list'][lvl]
                if (sib['type'] == 'T' or sib['type'] == 'TR'):
                    if (sib['dir'] == current['dir']):      # s.1 T/TR + t/tr = T/Tr
                        foundSib = True
                        parent = extend(sib, current, patterns_series)
                        parent = tryExpand(parent, patterns_series)
                    elif _includes(current, sib):   # f.1 t'/t'r + T/TR -> keep searching larger sib
                        lvl += 1
                    elif _breaks(sib, current):   # s.2 T'/T'R + t/tr = T'R
                        foundSib = True
                        parent = incTurn(sib, current, patterns_series)
                        parent = tryExpand(parent, patterns_series)
                    else:                                    # s.3 t'/t'r + t/tr = R
                        foundSib = True
                        uncle = sib
                        lvl += 1
                        while (lvl <= sib_lvlCount and not(_includes(uncle, current))):
                            sib = uncle
                            uncle = patterns_series[sib_id]['list'][lvl]
                            lvl += 1
                        lvl -= 1
                        parent = combine(sib, current, patterns_series)
                        parent = tryExpand(parent, patterns_series)
                else:                                        # f.2 r+t/tr -> keep searching larger sib
                    lvl += 1


    elif (current['type'] == 'R'):
        foundSib = False
        while not(foundSib):
            if (lvl > sib_lvlCount):          #cannot find
                    lvl -= 1
                    sib = patterns_series[sib_id]['list'][lvl]
                    foundSib = True
                    parent = combine(sib, current, patterns_series)
                    parent = tryExpand(parent, patterns_series)
            else:
                sib = patterns_series[sib_id]['list'][lvl]
                if (sib['type'] == 'T' or sib['type'] == 'TR'):
                    if _breaks(sib, current) :   #s.1 T/TR + r = TR
                        foundSib = True
                        parent = incTurn(sib, current, patterns_series)
                        parent = tryExpand(parent, patterns_series)
                    elif _includes(current, sib):  #f.1 t/tr+R -> keep searching larger
                        lvl += 1
                    else:                                   #s.2 t/tr+r == R
                        foundSib = True
                        uncle = sib
                        lvl += 1
                        while (lvl <= sib_lvlCount and not(_includes(uncle, current))):
                            sib = uncle
                            uncle = patterns_series[sib_id]['list'][lvl]
                            lvl += 1
                        lvl -= 1
                        parent = combine(sib, current, patterns_series)
                        parent = tryExpand(parent, patterns_series)

    # Exception case: SHOULD NOT BE ANY
    else:
        sib = FAKE_TRDRNG
        parent = current
        print('Exception!, current[type]')

    return sib, parent

# main function to create the unit in a pattern_series
def CreatePatternsUnit(px_data, stdDev, patterns_series):

    # test breakpoint
    if (px_data['id'] == 123):
        testBreak = 1

    patterns = []
    shortCodes = []
    current = createLvl0(px_data, stdDev)
    patterns.append(current)
    lvlCount = 0
    shortCode = createShortCode(current)
    max_lvl = 0
    shortCodes.append(shortCode)
    while (current['sib_id'] > ROOT_ID):
        sib, parent= findRelatives(current, patterns_series)
        current['sib_lvl'] = sib['lvl']
        current = parent
        patterns.append(current)
        lvlCount += 1
        shortCode = createShortCode(current)
        prev_lvl = max_lvl
        max_lvl = current['lvl']
        for i in range(max_lvl - prev_lvl - 1):
            shortCodes.append(" - ")
        shortCodes.append(shortCode)

    unit = {'max_lvl': max_lvl, 'lvlCount': lvlCount, 'list': patterns, 'shortCodes': shortCodes}
    # print out the short codes for each line
    # printShortCode(px_data['date'], shortCodes)

    return unit

# main function to create pattern series
def CreatePatternsSeries(px_data_series, stdDev_series):
    patterns_series = []
    i = 0
    for px_data in px_data_series:
        stdDev = stdDev_series[i]
        unit = CreatePatternsUnit(px_data, stdDev, patterns_series)
        patterns_series.append(unit)
        i += 1

    return patterns_series
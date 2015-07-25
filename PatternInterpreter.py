__author__ = 'wuyuao'

import PatternFunctions

def _largerConso2(uncle_conso_len, uncle_conso_height, current_conso_len, current_conso_height):
    if (uncle_conso_len > (current_conso_len * 2) and (uncle_conso_height * 2) >= current_conso_height):
        return True
    elif (uncle_conso_height > (current_conso_height * 2) and (uncle_conso_len * 2) >= current_conso_len):
        return True
    else:
        return False

def get_son(parent_lvl, parent, parent_startID, patterns_series):
    lvl = parent_lvl
    son_id = parent['id']
    son = patterns_series[son_id]['list'][lvl]
    while (lvl > 0 and son['start_id'] < parent_startID):
        lvl -= 1
        son = patterns_series[son_id]['list'][lvl]

    return son

def get_sib(current_lvl, parent, current, residual_endID, pattern_series):
    start_id = parent['start_id']
    sib_dir = parent['dir']
    lvlCount = current_lvl
    # for r, find TRT or TR and returns the tail
    if (current == 'R' or current['dir'] <> parent['dir']):
        current_conso_len = current['total_len']
        current_conso_height = (current['high'] - current['low'])
        findUncle = False
        lvl = 0
        sib = pattern_series[residual_endID]['list'][lvl]
        uncle = sib
        while (lvl < lvlCount and not(findUncle)):
            uncle = pattern_series[residual_endID]['list'][lvl+1]
            if (uncle['start_id'] <= start_id):
                findUncle = True
            elif (uncle['type'] <> 'R' and uncle['dir'] == sib_dir
                  and _largerConso2(uncle['avg_conso_len'], uncle['avg_conso_height'],
                                    current_conso_len, current_conso_height)):
                findUncle = True
            else:
                sib = uncle
                lvl += 1

        if not(_largerConso2(uncle['total_len'], (uncle['high'] - uncle['low']),
                             current['total_len'], (current['high'] - current['low']))):
            return uncle, (lvl + 1), uncle['start_id'] -1

        if (uncle['type'] == 'TR'):
            residual_endID = uncle['turn_id'] - 1
        else:
            residual_endID = sib['start_id'] - 1

    # for t/tr, find t/tr of same magnitude
    else:
        current_conso_len = current['avg_conso_len']
        current_conso_height = current['avg_conso_height']
        findSib = False
        lvl = 0
        sib = pattern_series[residual_endID]['list'][lvl]
        while (lvl <= lvlCount and not(findSib)):
            sib = pattern_series[residual_endID]['list'][lvl]
            if (sib['start_id'] < start_id):
                lvl -= 1
                sib = pattern_series[residual_endID]['list'][lvl]
                findSib = True
            elif (sib['type'] <> 'R' and not(_largerConso2(current_conso_len, current_conso_height,
                                                           sib['avg_conso_len'], sib['avg_conso_height']))):
                findSib = True
            elif (sib['type'] == 'R' and not(_largerConso2(current_conso_len, current_conso_height,
                                                           sib['total_len'], (sib['high'] - sib['low'])))):
                findSib = True
            else:
                lvl += 1

        if (lvl >= lvlCount or sib['type'] <> 'R'):
            residual_endID = sib['start_id'] - 1
        else:
            uncle = pattern_series[residual_endID]['list'][lvl + 1]
            if (uncle['type'] == 'TR'):
                residual_endID = uncle['turn_id'] - 1
            else:
                residual_endID = sib['start_id'] - 1

    return sib, lvl, residual_endID

def LocatePatternsSeries(patterns_series):
    PatternLines_series = []
    i = 0
    for patterns in patterns_series:

        if (i==256):
            breakpoint = 1

        PatternLines = []
        lvl = 0
        lvlCount = patterns['lvlCount']
        while (lvl < lvlCount - 1):
            PatternLine = []
            current = patterns['list'][lvl]
            lvl_inc = 1
            parent = patterns['list'][lvl + lvl_inc]
            if (current['type'] <> 'R' and parent['type'] == 'R'):
                lvl_inc = 2
                parent = patterns['list'][lvl + lvl_inc]
            parent_startId = parent['start_id']
            PatternLine.append(current)
            residual_endID = current['sib_id']
            while (residual_endID >= parent_startId):
                parent_lvlCount = patterns_series[residual_endID]['lvlCount']
                sib, sib_lvl, residual_endID = get_sib(parent_lvlCount, parent, current, residual_endID, patterns_series)
                if (sib['start_id'] < parent_startId):
                    sib = get_son(sib_lvl, sib, parent_startId, patterns_series)
                PatternLine.append(sib)

            PatternCount = len(PatternLine)
            CurLvl_PatternLine = {'lvl': lvl, 'len': PatternCount, 'list': PatternLine}
            PatternLines.append(CurLvl_PatternLine)
            lvl += lvl_inc
        i += 1

        current = patterns['list'][lvl]
        Locs = []
        Locs.append(current)
        CurLvl_Locs = {'lvl': lvl, 'len': 1, 'list': Locs}
        PatternLines.append(CurLvl_Locs)
        lineLvlCount = len(PatternLines)
        PatternLines_unit = {'id': i, 'lvlCount': lineLvlCount, 'list': PatternLines}
        PatternLines_series.append(PatternLines_unit)
    return PatternLines_series


__author__ = 'wuyuao'

import tester

# Tester 1:
def PrintTest_1():
    prev_cross = tester.tech_px_Cross_LMA_daily[0]
    for cross in tester.tech_px_Cross_LMA_daily:
        if (cross['signal']):
            i = cross['id']
            print(tester.px_dataset_daily[i]['date'],cross['dir'],cross['count'],cross['dist'])
            j = prev_cross['id']
            print('\t', tester.px_dataset_daily[j]['date'],prev_cross['dir'],
                  prev_cross['count'],prev_cross['dist'])
        prev_cross = cross
    return

# Tester 2
def PrintTest_2():
    i = 0
    for px_data in tester.px_dataset_daily:
        print('%1.4f'%px_data['chg'], '%1.4f'%tester.stdDev_daily[i]['thresh'])
        i += 1
    return

# Tester 3
def PrintTest_3(testId):
    lvl = 0
    TrdRng_series = tester.patn_TrdRngs_daily[testId]
    px_data = tester.px_dataset_daily[testId]
    while (lvl <= TrdRng_series['lvlCount']):
        start_id = TrdRng_series['list'][lvl]['start_id']
        start_date = tester.px_dataset_daily[start_id]['date']
        type = TrdRng_series['list'][lvl]['type']
        dir = TrdRng_series['list'][lvl]['dir']
        end_date = px_data['date']
        fromLv = TrdRng_series['list'][lvl]['from']
        toLv = TrdRng_series['list'][lvl]['to']
        print('Lv: '+str(lvl)+': '+start_date+'-'+end_date+' '+type+' '+str(dir)+': '+str(fromLv)+' - '+str(toLv))
        lvl += 1
    return

# Tester 4: print out all levels of sibling patterns for TestID
# create the short code for the pattern
def createShortCode(current):
    type_str = str(current['type'])
    startId_str = str(current['start_id'])
    endId_str = str(current['id'])
    if (current['dir'] > 0):
        dir_str = ',u'
    elif (current['dir'] < 0):
        dir_str = ',d'
    else:
        dir_str = ',e'

    shortCode = type_str + startId_str + '/' + endId_str + dir_str
    return shortCode

def createLongCode(current):
    type_str = str(current['type'])
    startId = current['start_id']
    startDate = tester.px_dataset_daily[startId]['date']
    endId = current['id']
    endDate = tester.px_dataset_daily[endId]['date']
    if (current['dir'] > 0):
        dir_str = ',u'
    elif (current['dir'] < 0):
        dir_str = ',d'
    else:
        dir_str = ',e'

    shortCode = type_str+ dir_str +'(' + startDate + '-' + endDate +')'
    return shortCode


def PrintTest_4(testId):
    lvl = 0
    lvlCount = tester.patn_TrdRngLocs_daily[testId]['lvlCount']
    lvlLocsList = tester.patn_TrdRngLocs_daily[testId]['list']
    while (lvl < lvlCount):
        Locs = lvlLocsList[lvl]['list']
        line = ""
        for Loc in Locs:
            shortCode = createShortCode(Loc)
            longCode = createLongCode(Loc)
            line = line + longCode + "; "
        print(line)
        lvl += 1
    return

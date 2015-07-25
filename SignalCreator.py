__author__ = 'wuyuao'

# SignalCode: 01
# Name: Double Top/Bottom
# Description: A fake breakout on the range by a reversion back into it
def signal_DTDB(px_data, current, parent):
    if (current['dir'] > 0):
        peak = current['high']
        rangeBound = parent['high']
    else:
        peak = current['low']
        rangeBound = parent['low']
    if (current['type'] == 'TR' and parent['type'] == 'R' and peak == rangeBound):
        Signal = -current['dir']
        RW = px_data['close'] - current['pivot']
        RK = (current['top'] + (current['top'] - current['bottom']) / 2.0) - px_data['close']
        EW = current['pivot'] - (current['bottom'] + (current['top'] - current['bottom']) / 2.0)
        return Signal, RW, RK, EW
    else:
        return 0, 0, 0, 0

def CreateTrdRngSignals(px_dataset_daily, stdDev_daily, patn_TrdRngs_daily, patn_TrdRngLocs_daily):
    allSignals_series = []
    for patternLines in patn_TrdRngLocs_daily:
        allSignals = createSignals(patternLines)
        allSignals_series.append(allSignals)
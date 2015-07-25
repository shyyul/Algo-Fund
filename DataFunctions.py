__author__ = 'wuyuao'
# Headings - Library for functions dealing with data
import csv
import numpy

# CONSTANTS
PX_MAX_VAL = 10^9
PX_MIN_VAL = -PX_MAX_VAL

# Function to Read and Save Price Data
def ReadData(f):
    # initiate my variables
    px_data_series = []

    # function starts
    i = 0
    for row in csv.DictReader(f):
        px_date = row['Date']
        px_open = float(row['Open'])
        px_high = float(row['High'])
        px_low = float(row['Low'])
        px_close = float(row['PX_Last'])
        px_pivot = float(px_high + px_low + px_close) / 3
        px_chg = float(px_close - px_open)
        px_range = float(px_high - px_low)
        px_data = {'id': i, 'date': px_date, 'open': px_open,
                         'high': px_high, 'low': px_low,
                         'close': px_close, 'pivot': px_pivot,
                         'chg': px_chg, 'range': px_range}
        px_data_series.append(px_data)
        i += 1

    return px_data_series

# Function to Create Std Dev Data
def CreateStdDev(px_data_series, period):
    # initiate my variables
    StdDev_series = []

    i = 0
    cur_dataSeries = []
    cur_avg = 0

    # function starts
    for px_data in px_data_series:
        if (i == 0):
            chgCoC = px_data['close'] - px_data['open']
        else:
            prev_px_data = px_data_series[i-1]
            chgCoC = px_data['close'] - prev_px_data['close']

        if (i >= period):
            exclude = cur_dataSeries.pop(0)
            cur_avg = (cur_avg * period - exclude + abs(chgCoC)) / period
        else:
            cur_avg = (cur_avg * i + abs(chgCoC)) / (i + 1)
        cur_dataSeries.append(abs(px_data['chg']))
        std = numpy.std(cur_dataSeries)
        stdDev = {'stdDev': std, 'avg': cur_avg, 'thresh': cur_avg - std, 'chgCoC': chgCoC}
        StdDev_series.append(stdDev)
        i += 1

    return StdDev_series

# Function to Generate Moving Average series for close px and pivot px
def CreateMAs(px_data_series, MA_period):
    # initiate my variables
    MA_series = []
    i = 0
    sum_close = 0.0
    sum_pivot = 0.0

    # function starts
    for px_data in px_data_series:
        if (i < MA_period):
            sum_close += px_data['close']
            close = sum_close / (i+1)
            sum_pivot += px_data['pivot']
            pivot = sum_pivot / (i+1)
        else:
            j = i - MA_period
            px_data_j = px_data_series[j]
            sum_close -= px_data_j['close']
            sum_close += px_data['close']
            close = sum_close / MA_period
            sum_pivot -= px_data_j['pivot']
            sum_pivot += px_data['pivot']
            pivot = sum_pivot / MA_period

        MA = {'id': i, 'close': close, 'pivot': pivot}
        MA_series.append(MA)
        i += 1

    return MA_series

# Function to Generate Price and MA crosses
def CreatePxCrossMA(px_data_series, MA_series):
    # initiate my variables
    Cross_series = []
    i = 0
    prev_dir = 0
    id_prev_cross = 0

    # function starts
    for px_data in px_data_series:
        MA = MA_series[i]
        if (px_data['close']>MA['close']):
            cur_dir = 1
        elif (px_data['close']<MA['close']):
            cur_dir = -1
        else:
            cur_dir = 0

        crossSig = (cur_dir != prev_dir)
        if crossSig:
            id_prev_cross = i

        MA_prev_cross = MA_series[id_prev_cross]
        dist_cross = px_data['close'] - MA_prev_cross['close']
        count_cross = i - id_prev_cross + 1

        Cross = {'id': i, 'signal': crossSig, 'dir': cur_dir,
                 'count': count_cross, 'dist': dist_cross}

        prev_dir = cur_dir
        Cross_series.append(Cross)
        i += 1

    return Cross_series
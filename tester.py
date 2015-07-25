__author__ = 'wuyuao'

import DataFunctions
import PatternFunctions
import PatternInterpreter
import PrintTests

f = open('EUR Daily.csv', 'rU')
px_dataset_daily = DataFunctions.ReadData(f)    #{id, date, open, high, low, close, pivot}

stdDev_period = 200

stdDev_daily = DataFunctions.CreateStdDev(px_dataset_daily, stdDev_period)

L_MA_period = 120
M_MA_period = 60
S_MA_period = 20

tech_L_MAs_daily = DataFunctions.CreateMAs(px_dataset_daily, L_MA_period)
tech_px_Cross_LMA_daily = DataFunctions.CreatePxCrossMA(px_dataset_daily, tech_L_MAs_daily)

patn_TrdRngs_daily = PatternFunctions.CreatePatternsSeries(px_dataset_daily, stdDev_daily)
patn_TrdRngLocs_daily = PatternInterpreter.LocatePatternsSeries(patn_TrdRngs_daily)
signal_TrdRng_daily = SignalCreator.CreateTrdRngSignals(px_dataset_daily, stdDev_daily, patn_TrdRngs_daily, patn_TrdRngLocs_daily)

#Main
if __name__ == "__main__":
    testId = 315
    PrintTests.PrintTest_4(testId)




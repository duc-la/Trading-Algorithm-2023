import indexClass
import pandas as pd
import os
from globals import directory
class Stock:
    """This class will represent a stock object with all the prices and attached MACD, EMA, and ATR values
        Author: Duc La
        Date: 1/1/2024
    """

    def __init__(self, stockDF, stockTicker):
        #Stock Data
        self.stockData = stockDF
        self.stockName = stockTicker
        self.dateOffset = None
        self.setOffSet()


        #EMA
        self.ema200Data = calculateEMA(stockDF, 200)

        #MACD
        self.macd12Data = calculateEMA(stockDF, 12)
        self.macd26Data = calculateEMA(stockDF, 26)
        self.macdData = self.calculateMACD(self.macd12Data, self.macd26Data)
        self.signalData = self.calculateMACDSignal(self.macdData, 9)

        #ATR
        self.atr14Data = self.calculateATR(stockDF, 14)

    def setOffSet(self):
        nasdaq = indexClass.Index(pd.read_csv(os.path.join(directory, f'QQQ.csv')), "QQQ")
        count = 0
        for i in range(0, len(nasdaq.indexData)):
            if nasdaq.indexData['Date'][i] == self.stockData['Date'][0]:
                self.dateOffset = i
                break



    def calculateATR(self, stockDF, timePeriod):
        """This function calculates the ATR values given stock data and time period
            Args:
                stockDF - pandas data frame for stock data
                timePeriod - length of ATR

            Returns:
                List - representing all values of the ATR
        """


        firstTR = stockDF["High"][0] - stockDF["Low"][0]
        sumTR = firstTR

        for i in range (1, timePeriod):
            sumTR = sumTR + max(stockDF["High"][i] - stockDF["Low"][i], abs(stockDF["High"][i] - stockDF["Adj Close"][i-1]), abs(stockDF["Low"][i] - stockDF["Adj Close"][i-1]))

        atrData = []
        atrData.append(sumTR/timePeriod)


        for j in range(timePeriod, len(stockDF["High"])):
            atrData.append((atrData[j-timePeriod]*(timePeriod-1) + max(stockDF["High"][j] - stockDF["Low"][j], abs(stockDF["High"][j] - stockDF["Adj Close"][j-1]), abs(stockDF["Low"][j] - stockDF["Adj Close"][j-1])))/timePeriod)

        return atrData


    def calculateMACD(self, ema1, ema2):
        """This function calculates the MACD values given two lists of ema values
            Args:
                ema1 - the first and shorter length EMA
                ema2 - the second and longer length EMA

            Returns:
                List - representing all values of MACD
        """

        if len(ema1) > len(ema2):
            ema1 = ema1[len(ema1) - len(ema2):]
        else:
            ema2 = ema2[len(ema2) - len(ema1):]

        macdData = []

        for i in range(0, len(ema2)):
            macdData.append(ema1[i] - ema2[i])

        return macdData

    def calculateMACDSignal(self, macd, timePeriod):
        """This function calculates the signal values given a list of MACD values and a time period to be taken
            Args:
                macd - the macd values
                timePeriod - the time period average of macd to be taken

            Returns:
                List - representing the signal values of MACD indicator
        """


        signalData = []

        firstAverage = sum(macd[0:timePeriod]) / timePeriod
        signalData.append(firstAverage)

        for i in range(timePeriod, len(macd)):
            signalData.append(macd[i] * 2 / (timePeriod + 1) + signalData[i - timePeriod] * (1 - 2 / (timePeriod + 1)))

        return signalData

def calculateEMA(stockDF, timePeriod):
    """This function calculates the EMA values given stock data and time period
        Args:
            stockDF - pandas data frame for stock data
            timePeriod - length of EMA

        Returns:
            List - representing all values of the EMA
    """

    emaData = []

    firstAverage = sum(stockDF["Adj Close"][0:timePeriod])/timePeriod
    emaData.append(firstAverage)


    for i in range(timePeriod, len(stockDF["Adj Close"])):
        emaData.append(stockDF["Adj Close"][i] * 2 / (timePeriod+1) + emaData[i-timePeriod] * (1-2/(timePeriod+1)))

    return emaData



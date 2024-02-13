import datetime
import os
import time
from globals import directory

import pandas as pd

import closedTradeClass
import indexClass
import openTradeClass
import webscrapeIndices
from stockClass import Stock


class tradingAlgorithmMaster:
    """This class will simulate the backtesting and hold all the important information on the trades in the backtest
     Author: Duc La
     Date: 1/1/2024
     """

    def __init__(self):
        # Start, end, and interval
        # Current Data Folder
        self.start = int(time.mktime(datetime.datetime(2023, 3, 20, 23, 59).timetuple()))
        self.end = int(time.mktime(datetime.datetime(2024, 2, 12, 23, 59).timetuple()))

        # 7 year testing
        #self.start = int(time.mktime(datetime.datetime(2012, 2, 4, 23, 59).timetuple()))
        #self.end = int(time.mktime(datetime.datetime(2019, 2, 4, 23, 59).timetuple()))

        # 2019 to 2020 Data
        # self.start = int(time.mktime(datetime.datetime(2019, 2, 4, 23, 59).timetuple()))
        # self.end = int(time.mktime(datetime.datetime(2020, 11, 13, 23, 59).timetuple()))

        self.interval = '1d'  # 1w, 1m
        self.currentNet = 3000  # Original is 3000, but with margin 9000 because BP is 2
        self.cashAvailable = 9000
        self.openTradesMap = {}
        self.closedTrades = []

        self.longProfit1 = 0
        self.longProfit2 = 0
        self.longLoss1 = 0
        self.longLoss2 = 0

        self.shortProfit1 = 0
        self.shortProfit2 = 0
        self.shortLoss1 = 0
        self.shortLoss2 = 0

    def manageLongTrades(self, stock, currentDate):
        # Consider new trade because isn't currently an open trade
        i = currentDate - stock.dateOffset

        if stock.stockName not in self.openTradesMap:
            if (i < len(stock.stockData)) and (i >= 199) and (
                    stock.stockData["Adj Close"][i] > stock.ema200Data[i - 199]) and (
                    stock.macdData[i - 25] > stock.signalData[i - 33]) and (
                    stock.macdData[i - 26] < stock.signalData[i - 34]) and (stock.macdData[i - 26] < 0):
                self.openTradesMap[stock.stockName] = openTradeClass.openTrade(stock.stockData["Date"][i],
                                                                               stock.stockData["Adj Close"][i],
                                                                               stock.atr14Data[i - 13],
                                                                               self.currentNet * .01,
                                                                               stock.stockData["Low"][i],
                                                                               self.cashAvailable)
                print("OPENED LONG: " + str(stock.stockName) + " AT PRICE: " + str(
                    stock.stockData['Adj Close'][i]) + " CHANGE IN CASH: " + \
                      str(self.openTradesMap[stock.stockName].quantity * round(
                          self.openTradesMap[stock.stockName].fillPrice, 2)) + \
                      " QUANTITY: " + str(self.openTradesMap[stock.stockName].quantity))
                self.cashAvailable = self.cashAvailable - self.openTradesMap[stock.stockName].quantity * round(
                    self.openTradesMap[stock.stockName].fillPrice, 2)

        # Monitor open trade
        else:
            self.manageOpenPositions(stock, i)

    def manageShortTrades(self, stock, currentDate):

        i = currentDate - stock.dateOffset

        # Consider new trade because isn't currently an open trade
        if stock.stockName not in self.openTradesMap:

            if (
                    (i < len(stock.stockData)) and
                    (i >= 199) and
                    (stock.stockData["Adj Close"][i] < stock.ema200Data[i - 199]) and
                    (stock.macdData[i - 25] < stock.signalData[i - 33]) and
                    (stock.macdData[i - 26] > stock.signalData[i - 34]) and
                    (stock.macdData[i - 26] > 0)
            ):
                self.openTradesMap[stock.stockName] = openTradeClass.openTrade(stock.stockData["Date"][i],
                                                                               stock.stockData["Adj Close"][i],
                                                                               stock.atr14Data[i - 13],
                                                                               self.currentNet * -.01,
                                                                               stock.stockData["Low"][i],
                                                                               self.cashAvailable)
                print("OPENED SHORT: " + str(stock.stockName) + " AT PRICE: " + str(
                    stock.stockData['Adj Close'][i]) + " CHANGE IN CASH: " + \
                      str(self.openTradesMap[stock.stockName].quantity * round(
                          self.openTradesMap[stock.stockName].fillPrice, 2)) + \
                      " QUANTITY: " + str(self.openTradesMap[stock.stockName].quantity))
                self.cashAvailable = self.cashAvailable + self.openTradesMap[stock.stockName].quantity * round(
                    self.openTradesMap[stock.stockName].fillPrice, 2)

        # Monitor open trade
        else:
            self.manageOpenPositions(stock, i)

    def manageOpenPositions(self, stock, i):
        # Close out for loss when long

        if (
                (self.openTradesMap[stock.stockName].cashRisk > 0) and
                (stock.stockData["Low"][i] <= self.openTradesMap[stock.stockName].loss)
        ):
            close = closedTradeClass.closedTrade(round(self.openTradesMap[stock.stockName].fillPrice, 2),
                                                 round(self.openTradesMap[stock.stockName].loss, 2),
                                                 self.openTradesMap[stock.stockName].quantity,
                                                 self.openTradesMap[stock.stockName].fillTime,
                                                 stock.stockData["Date"][i], stock.stockName)
            print(
                "CLOSED LONG LOSS: " + str(close.stockName) +
                " AT PRICE: " + str(close.closedPrice) +
                " CHANGE: " + str(close.change) +
                " OPENED DATE: " + str(close.startDate) +
                " CLOSED DATE: " + str(close.endDate) +
                " CASH GAIN: " + str(round(close.closedPrice * close.quantity, 2)) +
                " QUANTITY: " + str(close.quantity))

            if (close.change * -1 < .005 * self.currentNet):
                self.longLoss2 += 1
            else:
                self.longLoss1 += 1

            self.closedTrades.append(close)
            self.currentNet = self.currentNet + close.change
            self.cashAvailable = self.cashAvailable + close.closedPrice * close.quantity
            del self.openTradesMap[stock.stockName]

            return

        # Close out for a loss when short
        if (
                (self.openTradesMap[stock.stockName].cashRisk < 0) and
                (stock.stockData["High"][i] >= self.openTradesMap[stock.stockName].loss)
        ):
            close = closedTradeClass.closedTrade(round(self.openTradesMap[stock.stockName].fillPrice, 2),
                                                 round(self.openTradesMap[stock.stockName].loss, 2),
                                                 self.openTradesMap[stock.stockName].quantity,
                                                 self.openTradesMap[stock.stockName].fillTime,
                                                 stock.stockData["Date"][i], stock.stockName)
            print(
                "CLOSED SHORT LOSS: " + str(close.stockName) +
                " AT PRICE: " + str(close.closedPrice) +
                " CHANGE IN CASH: " + str(close.change) +
                " OPENED DATE: " + str(close.startDate) +
                " CLOSED DATE: " + str(close.endDate) +
                " QUANTITY: " + str(close.quantity))

            if (close.change * -1 < .005 * self.currentNet):
                self.shortLoss2 += 1
            else:
                self.shortLoss1 += 1

            self.closedTrades.append(close)
            self.currentNet = self.currentNet + close.change
            self.cashAvailable = self.cashAvailable - close.closedPrice * close.quantity
            del self.openTradesMap[stock.stockName]

            return

        # First profit when long
        if (
                (self.openTradesMap[stock.stockName].cashRisk > 0) and
                (stock.stockData["High"][i] >= round(self.openTradesMap[stock.stockName].profit, 2)) and
                (self.openTradesMap[stock.stockName].firstFill)
        ):
            close = closedTradeClass.closedTrade(round(self.openTradesMap[stock.stockName].fillPrice, 2),
                                                 round(self.openTradesMap[stock.stockName].profit, 2),
                                                 self.openTradesMap[stock.stockName].quantity - int(
                                                     self.openTradesMap[stock.stockName].quantity * .5),
                                                 self.openTradesMap[stock.stockName].fillTime,
                                                 stock.stockData["Date"][i], stock.stockName)
            print(
                "CLOSED LONG PROFIT1: " + str(close.stockName) +
                " AT PRICE: " + str(close.closedPrice) +
                " CHANGE IN CASH: " + str(close.change) +
                " OPENED DATE: " + str(close.startDate) +
                " CLOSED DATE: " + str(close.endDate) +
                " QUANTITY: " + str(close.quantity))

            self.longProfit1 += 1

            self.closedTrades.append(close)
            self.currentNet = self.currentNet + close.change
            self.cashAvailable = self.cashAvailable + close.closedPrice * close.quantity
            self.openTradesMap[stock.stockName].modifyProfit()

        # Second profit when long
        if (
                (self.openTradesMap[stock.stockName].cashRisk > 0) and
                (stock.stockData["High"][i] >= round(self.openTradesMap[stock.stockName].profit, 2)) and
                (self.openTradesMap[stock.stockName].firstFill == False)
        ):
            close = closedTradeClass.closedTrade(round(self.openTradesMap[stock.stockName].fillPrice, 2),
                                                 round(self.openTradesMap[stock.stockName].profit, 2),
                                                 self.openTradesMap[stock.stockName].quantity,
                                                 self.openTradesMap[stock.stockName].fillTime,
                                                 stock.stockData["Date"][i], stock.stockName)
            print(
                "CLOSED LONG PROFIT2: " + str(close.stockName) +
                " AT PRICE: " + str(close.closedPrice) +
                " CHANGE IN CASH: " + str(close.change) +
                " OPENED DATE: " + str(close.startDate) +
                " CLOSED DATE: " + str(close.endDate) +
                " QUANTITY: " + str(close.quantity))

            self.longProfit2 += 1

            self.closedTrades.append(close)
            self.currentNet = self.currentNet + close.change
            self.cashAvailable = self.cashAvailable + close.closedPrice * close.quantity
            del self.openTradesMap[stock.stockName]
            return

        # First profit when short
        if (
                (self.openTradesMap[stock.stockName].cashRisk < 0) and
                (stock.stockData["Low"][i] <= round(self.openTradesMap[stock.stockName].profit, 2)) and
                (self.openTradesMap[stock.stockName].firstFill == True)
        ):
            close = closedTradeClass.closedTrade(round(self.openTradesMap[stock.stockName].fillPrice, 2),
                                                 round(self.openTradesMap[stock.stockName].profit, 2),
                                                 self.openTradesMap[stock.stockName].quantity - int(
                                                     self.openTradesMap[stock.stockName].quantity * .5),
                                                 self.openTradesMap[stock.stockName].fillTime,
                                                 stock.stockData["Date"][i], stock.stockName)
            print(
                "CLOSED SHORT PROFIT1: " + str(close.stockName) +
                " AT PRICE: " + str(close.closedPrice) +
                " CHANGE IN CASH: " + str(close.change) +
                " OPENED DATE: " + str(close.startDate) +
                " CLOSED DATE: " + str(close.endDate) +
                " QUANTITY: " + str(close.quantity))

            self.shortProfit1 += 1

            self.closedTrades.append(close)
            self.currentNet = self.currentNet + close.change
            self.cashAvailable = self.cashAvailable - close.closedPrice * close.quantity
            self.openTradesMap[stock.stockName].modifyProfit()

        # Second profit when short
        if (
                (self.openTradesMap[stock.stockName].cashRisk < 0) and
                (stock.stockData["Low"][i] <= round(self.openTradesMap[stock.stockName].profit, 2)) and
                (self.openTradesMap[stock.stockName].firstFill == False)
        ):
            close = closedTradeClass.closedTrade(round(self.openTradesMap[stock.stockName].fillPrice, 2),
                                                 round(self.openTradesMap[stock.stockName].profit, 2),
                                                 self.openTradesMap[stock.stockName].quantity,
                                                 self.openTradesMap[stock.stockName].fillTime,
                                                 stock.stockData["Date"][i], stock.stockName)
            print(
                "CLOSED SHORT PROFIT2: " + str(close.stockName) +
                " AT PRICE: " + str(close.closedPrice) +
                " CHANGE IN CASH: " + str(close.change) +
                " OPENED DATE: " + str(close.startDate) +
                " CLOSED DATE: " + str(close.endDate) +
                " QUANTITY: " + str(close.quantity))

            self.shortProfit2 += 1

            self.closedTrades.append(close)
            self.currentNet = self.currentNet + close.change
            self.cashAvailable = self.cashAvailable - close.closedPrice * close.quantity
            del self.openTradesMap[stock.stockName]
            return

    def binarySearch(self, arr, key, high, low, currentDate):
        while low <= high:
            mid = int((high + low) // 2)
            if key.stockData[key.stockData["Date"] == currentDate]["Adj Close"].values[0] > \
                    arr[mid].stockData[arr[mid].stockData["Date"] == currentDate]["Adj Close"].values[0]:
                high = mid - 1
            else:
                low = mid + 1

        return low

    def getData(self):
        backTestList = set(webscrapeIndices.getNasdaq100List())

        webscrapeIndices.getYFData("QQQ", self.start, self.end, self.interval, directory)
        webscrapeIndices.getYFData("SPY", self.start, self.end, self.interval, directory)
        for ticker in backTestList:
            webscrapeIndices.getYFData(ticker, self.start, self.end, self.interval, directory)

    def insertionSortOnPrice(self, stocks, currentDate):
        updateStocks = []

        for i in range(0, len(stocks)):
            if currentDate in stocks[i].stockData['Date'].values:
                # print(stocks[i].stockData['Date'].values[0])
                updateStocks.append(stocks[i])

        for i in range(1, len(updateStocks)):
            key = updateStocks[
                i]  # updateStocks[i].stockData[updateStocks[i].stockData['Date'] == currentDate]["Adj Close"].values[0]
            index = self.binarySearch(updateStocks[:i], key, i - 1, 0, currentDate)
            updateStocks = updateStocks[:index] + [key] + updateStocks[index:i] + updateStocks[i + 1:]

        return updateStocks

    def backtest(self):
        # Union both S&P 500 and Nasdaq 100 Data
        backTestList = set(webscrapeIndices.getNasdaq100List())
        stocks = []
        stockMap = {}

        # Put all stock objects into a list of stocks
        count = 0
        for ticker in backTestList:
            if os.path.exists(os.path.join(directory, f'{ticker}.csv')):
                stocks.append(Stock(pd.read_csv(os.path.join(directory, f'{ticker}.csv')), ticker))

        for i in range(0, len(stocks)):
            stockMap[stocks[i].stockName] = stocks[i]

        # Initialize current date and open and closed trades to nothing

        # Change S&P 500 and Nasdaq Data for 2018 to 2022 to 2023 Data for 2010 data all
        nasdaq = indexClass.Index(pd.read_csv(os.path.join(directory, f'QQQ.csv')), "QQQ")
        sp = indexClass.Index(pd.read_csv(os.path.join(directory, f'SPY.csv')), "SPY")

        for i in range(199, len(nasdaq.indexData)):
            # Update cash every time
            self.cashAvailable = self.currentNet * 3 - (self.currentNet * 3 - self.cashAvailable)
            print(nasdaq.indexData["Date"][i])
            # Every time we use margin (available cash is less than twice the current net worth)
            if (self.cashAvailable <= self.currentNet * 2):
                print("Interest Charged!")
                self.cashAvailable = self.cashAvailable - (6000 - self.cashAvailable) * (.0974 / 250)
                self.currentNet = self.currentNet - (6000 - self.cashAvailable) * (.0974 / 250)

            print("Available cash " + str(self.cashAvailable))

            currentDate = nasdaq.indexData["Date"][i]

            # Largest price to smallest price
            sortedStocks = self.insertionSortOnPrice(stocks, currentDate)

            if self.cashAvailable > 0:
                if nasdaq.indexData["Adj Close"][i] >= nasdaq.ema200Data[i - 199] and sp.indexData["Adj Close"][i] >= \
                        sp.ema200Data[i - 199]:
                    j = 0
                    while (self.cashAvailable > 0) and (j < len(sortedStocks)):
                        self.manageLongTrades(sortedStocks[j], i)
                        j += 1

                # Close is below ema for that day for both indices so uptrend
                elif nasdaq.indexData["Adj Close"][i] < nasdaq.ema200Data[i - 199] and sp.indexData["Adj Close"][i] < \
                        sp.ema200Data[i - 199]:
                    j = 0
                    while (self.cashAvailable > 0) and (j < len(sortedStocks)):
                        self.manageShortTrades(sortedStocks[j], i)
                        j += 1

                else:
                    openList = []
                    for key in self.openTradesMap:
                        openList.append(key)

                    for l in range(0, len(openList)):
                        k = i - stockMap[openList[l]].dateOffset
                        if (i < len(stockMap[openList[l]].stockData)):
                            self.manageOpenPositions(stockMap[openList[l]], k)

            else:
                openList = []
                for key in self.openTradesMap:
                    openList.append(key)

                for l in range(0, len(openList)):
                    k = i - stockMap[openList[l]].dateOffset
                    if (i < len(stockMap[openList[l]].stockData)):
                        self.manageOpenPositions(stockMap[openList[l]], k)

        print("\n\nCLOSED POSITIONS")

        for i in range(0, len(self.closedTrades)):
            print("Ticker " + str(self.closedTrades[i].stockName) + " Opened: " + str(self.closedTrades[i].startPrice) + \
                  " For -" + str(self.closedTrades[i].startPrice * self.closedTrades[i].quantity) + " Closed: " + str(
                self.closedTrades[i].closedPrice) + "For +" + str(
                self.closedTrades[i].closedPrice * self.closedTrades[i].quantity) + \
                  "Change: " + str(self.closedTrades[i].change) + " Quantity: " + str(
                self.closedTrades[i].quantity) + "\n")

        print("\nCURRENT OPEN POSITIONS")
        for key in self.openTradesMap:
            print("Ticker " + str(key) + " Opened: " + str(self.openTradesMap[key].fillPrice) + \
                  " Quantity: " + str(self.openTradesMap[key].quantity) + "Time: " + str(
                self.openTradesMap[key].fillTime) + "\n")

        print(self.currentNet)

        print("\nTRADE STATS")

        print("Long Profit1 Number: " + str(self.longProfit1))
        print("Long Profit2 Number: " + str(self.longProfit1))

        print("\n")

        print("Short Profit1 Number: " + str(self.shortProfit1))
        print("Short Profit2 Number: " + str(self.shortProfit2))

        print("\n")
        print("Long Loss1 Number: " + str(self.longLoss1))
        print("Long Loss2 Number: " + str(self.longLoss2))

        print("\n")
        print("Short Loss1 Number: " + str(self.shortLoss1))
        print("Short Loss1 Number: " + str(self.shortLoss1))


trade = tradingAlgorithmMaster()
trade.getData()
trade.backtest()
# print(webscrapeIndices.getNasdaq100List())

# stock = Stock(webscrapeIndices.getYFData("ABNB", trade.start, trade.end, trade.interval), 'ABNB')
# print(stock.stockData["Date"])
# trade.backtest()
# stock = Stock(pd.read_csv(os.path.join('S&P 500 and Nasdaq Data for 2018',f'QQQ.csv')), "QQQ")
# print(stock.dateOffset)

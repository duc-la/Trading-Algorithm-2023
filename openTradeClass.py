class openTrade:
    def __init__(self, fillTime, fillPrice, atr, cashRisk, cond, cashAvailable):
        self.fillTime = fillTime
        self.fillPrice = fillPrice

        self.cashRisk = cashRisk
        self.marginLimitQuantity = cashAvailable #* 2
        self.profitMultiplier = 1.5
        self.firstFill = True

        if cashRisk > 0:
            self.loss = cond - atr
            self.profit = fillPrice + (fillPrice - self.loss) #round(fillPrice + (fillPrice - self.loss), 2)
            self.quantity = min(int(cashRisk / (self.fillPrice - self.loss)), int(self.marginLimitQuantity / self.fillPrice))

        else:
            self.loss = cond + atr
            self.profit = round(fillPrice - (self.loss-fillPrice), 2)
            self.quantity = min(int(cashRisk / (self.fillPrice + self.loss)), int(self.marginLimitQuantity / self.fillPrice))


    def modifyProfit(self):
        #print(self.profit)
        self.firstFill = False
        if self.cashRisk > 0:
            self.profit = self.fillPrice + (self.fillPrice - self.loss) * self.profitMultiplier
        else:
            self.profit = self.fillPrice - (self.loss+self.fillPrice) * self.profitMultiplier

        #print(self.profit)
        self.quantity = int(self.quantity * .5)
        self.loss = self.fillPrice
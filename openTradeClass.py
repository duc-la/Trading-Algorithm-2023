class openTrade:
    def __init__(self, fillTime, fillPrice, atr, cashRisk, cond, cashAvailable):
        self.fillTime = fillTime
        self.fillPrice = fillPrice

        self.cashRisk = cashRisk
        self.marginLimitQuantity = cashAvailable * 2
        self.firstFill = True

        if cashRisk > 0:
            self.loss = cond - atr
            self.profit = round(fillPrice + (fillPrice - self.loss), 2)
            self.quantity = min(int(cashRisk / (self.fillPrice - self.loss)), int(self.marginLimitQuantity / self.fillPrice))

        else:
            self.loss = cond + atr
            self.profit = round(fillPrice - (self.loss-fillPrice), 2)
            self.quantity = min(int(cashRisk / (self.fillPrice + self.loss)), int(self.marginLimitQuantity / self.fillPrice))


    def modifyProfit(self):
        print(self.profit)
        self.firstFill = False
        if self.cashRisk > 0:
            self.profit = self.fillPrice + (self.fillPrice - self.loss) * 1.5
        else:
            self.profit = self.fillPrice - (self.loss+self.fillPrice) * 1.5

        print(self.profit)
        self.quantity = int(self.quantity * .5)
        self.loss = self.fillPrice
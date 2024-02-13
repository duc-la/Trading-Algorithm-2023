class closedTrade:
    def __init__(self, startPrice, closedPrice, quantity, startDate, endDate, ticker):
        self.startDate = startDate
        self.stockName = ticker
        self.endDate = endDate
        self.startPrice = startPrice
        self.closedPrice = closedPrice
        self.quantity = quantity
        self.change = (closedPrice - startPrice) * quantity
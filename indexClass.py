from stockClass import calculateEMA
class Index:
    """This class will represent a stock index object similar to stock object but only needs EMA values and prices
        Author: Duc La
        Date: 1/1/2024
    """

    def __init__(self, indexDF, indexTicker):
        # Stock Data
        self.indexData = indexDF
        self.indexName = indexTicker

        # EMA
        self.ema200Data = calculateEMA(indexDF, 200)

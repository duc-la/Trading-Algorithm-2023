import os
import requests
from bs4 import BeautifulSoup
import re
import csv

def getNasdaq100List():
    """This function gets the list of current tickers in the Nasdaq 100
    Returns:
        None - the website can't be accessed
        List - representing all tickers in the Nasdaq 100 if website is accessed
    """

    url = f'https://www.cnbc.com/nasdaq-100/'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soupString = str(soup)
        index = soupString.find("chartIssueDetail")
        indices = []

        while index != -1:
            indices.append(index)
            index = soupString.find("chartIssueDetail", index + 1)

        tickerString = soupString[indices[0]: indices[len(indices) - 1]]

        pattern = re.compile(r'{"symbol":"([^"]+)"')

        # Find all matches in the substring
        matches = pattern.findall(tickerString)

        return matches
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None


# This function gets the list of current tickers in the S&P 500
# return: a list of strings representing the tickers
def getSP500List():
    """This function gets the list of current tickers in the S&P 500
    Returns:
            None - the website can't be accessed
            List - representing all tickers in the S&P 500 if website is accessed
    """

    url1 = f'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'
    headers1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response1 = requests.get(url1, headers=headers1)

    if response1.status_code == 200:
        soup1 = BeautifulSoup(response1.text, 'html.parser')
        soupString1 = str(soup1)
        index1 = soupString1.find('<td><a class="external text"')
        indices1 = []

        # 2-503
        while index1 != -1:
            indices1.append(index1)
            index1 = soupString1.find('<td><a class="external text"', index1 + 1)

        tickerString1 = soupString1[indices1[0]: indices1[len(indices1) - 1]]

        pattern1 = re.compile(r'rel="nofollow">([A-Z]+)</a>')

        # Find all matches in the substring
        matches1 = pattern1.findall(tickerString1)

        return matches1


    else:
        print(f"Failed to retrieve the page. Status code: {response1.status_code}")


def getYFData(ticker, period1, period2, interval, directory):
    """This function gets the pandas dataframe of stock data for a specific ticker by scraping yahoo finance
        Args:
            ticker - ticker information to find dataframe
            period1 - starting period for information in data frame
            period2 - ending period for information in data frame
            interval - how data should be divided (1d, 1w, 1m)

        Returns:
                None - the website can't be accessed
                Dataframe - representing price data for the ticker
        """



    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(query_string, headers=headers)



    if response.status_code == 200:
        with open(os.path.join(directory, f'{ticker}.csv'), 'w') as f:
            writer = csv.writer(f)
            for line in response.iter_lines():
                writer.writerow(line.decode('utf-8').split(','))

    else:
        return None
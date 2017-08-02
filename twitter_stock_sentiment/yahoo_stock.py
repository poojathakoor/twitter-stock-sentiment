from urllib.request import Request, urlopen
from urllib.parse import urlencode

class YahooStock:

    def _request(self, symbol, stat):
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
        req = Request(url)
        resp = urlopen(req)
        return str(resp.read().decode('utf-8').strip())

    def get_price(self, symbol):
        return self._request(symbol, 'l1')

    def get_change(self, symbol):
        return self._request(symbol, 'c1')
	
    def get_company_name(self, symbol):
        return self._request(symbol, 'n')
    
    def get_today_open(self, symbol):
        return self._request(symbol, 'o')
	
    def get_historical_prices(self, symbol, start_date, end_date):
        '''
        Get historical prices for the given ticker symbol.
        Date format is 'YYYY-MM-DD'
        Returns a nested dictionary (dict of dicts).
        outer dict keys are dates ('YYYY-MM-DD')
        '''
        params = urlencode({
            's': symbol,
            'a': int(start_date[5:7]) - 1,
            'b': int(start_date[8:10]),
            'c': int(start_date[0:4]),
            'd': int(end_date[5:7]) - 1,
            'e': int(end_date[8:10]),
            'f': int(end_date[0:4]),
            'g': 'd',
            'ignore': '.csv',
        })
        url = 'http://real-chart.finance.yahoo.com/table.csv?%s' % params
        req = Request(url)
        resp = urlopen(req)
        content = str(resp.read().decode('utf-8').strip())
        daily_data = content.splitlines()
        hist_dict = dict()
        keys = daily_data[0].split(',')
        for day in daily_data[1:]:
            day_data = day.split(',')
            date = day_data[0]
            hist_dict[date] = \
                {keys[1]: day_data[1],
                keys[2]: day_data[2],
                keys[3]: day_data[3],
                keys[4]: day_data[4],
                keys[5]: day_data[5],
                keys[6]: day_data[6]}
        return hist_dict
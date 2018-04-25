from bitstamp import client, BitstampError
from requests import HTTPError
from .broker import RealBroker, NotConnectedError, OrderNotFoundError
from .order import OrderStatus, Order
from .balance import Balance

"""
Bitstamp exchange Broker implementation
"""

class Bitstamp():
    name = "Bitstamp"

class RealBitstamp(RealBroker,Bitstamp):
    max_requests_per_frame = 600
    request_timeframe = 60 # sec

    def __init__(self, **auth):
        self.trading_pairs = set()
        self.connect(**auth)

    def connect(self, **auth):
        """ auth_params =
            {
            username:<username>,
            key:<apikey>,
            secret:<apisecret>
            }
        """

        self.connected = False
        try:
            if 'username'   not in auth: raise AuthError("Username is mandatory.")
            if 'key'        not in auth: raise AuthError("Key is mandatory.")
            if 'secret'     not in auth: raise AuthError("Secret is mandatory.")
            self.bitstamp = client.Trading(**auth)
            self._get_supported_pairs()
            self.connected = True
        except ValueError, BitstampError, HTTPError as e:
            self.status = str(e)

    def _get_supported_pairs(self):
        '''Load trading pairs'''

        if not self.connected: raise NotConnectedError
        pairs = filter(lambda r: r['trading'] == "Enabled", self.bitstamp.trading_pairs_info())
        self.trading_pairs = { TradingPair(p['name']) for p in pairs }

    def supported_pairs(self):
        '''Return trading pairs'''
        return  self.trading_pairs

    def transactions(self, ):
        '''returns recent transactions'''
        raw = self.bitstamp.user_transactions()
        return [ s for s in raw if s['type']=='2' ]

    def update_balance(self):
        '''Update balance info from the server'''
        if not self.connected: raise NotConnectedError
        response = self.bitstamp.account_balance(base=None, quote=None)
        fx = "_balance"
        rawbal = {l[:-len(fx)]:v for l,v in response.items() if l.endswith(fx)}
        self.balance = Balance(rawbal)

    def update_order(self, order):
        '''sync order info with bitstamp'''
        if not self.connected: raise NotConnectedError

        if type(order) is str :
            try:
                order = self.orders[order]
            except:
                raise ValueError("Order not found.")

        try:
            result = self.bitstamp.order_status(order_id)
        except client.BitstampError as e:
            order.status = OrderStatus.Removed
            return order

        translate = {
            'In Queue': OrderStatus.Pending,
            'Open':     OrderStatus.Open,
            'Finished': OrderStatus.Closed,
        }
        order.extra = result.transactions
        try:
            order.status = translate[result.status]
        except KeyErrror:
            pass

        # sum of base transactions
        base = order.pair.base.url_form()
        order.filled = sum [x[base] for x in result.transactions]
        return order


class TestBitstamp(TestBroker,Bitstamp):
    pass

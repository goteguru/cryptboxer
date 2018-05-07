import cmd, json, time
import threading
from configparser import SafeConfigParser, NoSectionError
import asyncio
import sys

quit_requested = False
mycounter = 0

# dict(config.items("Bitstamp"))
class CryptoGladiator(cmd.Cmd) :
    version = 'v0.01 beta'
    intro = "CryptoBoxer %s. I'm waiting for you command."%version
    prompt =  "G> "
    ruler = '-'
    start_time = 0
    tick = 0

    def preloop(self):
        self._get_pairs()
        def timer_callback():
            self.tick += 1
            self._bgprocess = threading.Timer(2,timer_callback)
            self._bgprocess.start()
        timer_callback()
        self.start_time = time.time()

    def postloop(self):
        self._bgprocess.cancel()

    def do_info(self, arg):
        'Report status information'
        td = time.time() - self.start_time
        days, secs = divmod(td, 60*60*24)
        hours,secs = divmod(secs, 60*60)
        minutes,secs = divmod(secs, 60)
        print(
                'Running time: {0:.0f} day {1:.0f} hours {2:.0f} mins {3:.1f} secs'
            .format(days,hours,minutes, secs)
        )
        print("counter:", mycounter)

    def do_quit(self,arg):
        global quit_requested
        quit_requested = True
        print("Weapons down. Peace.")
        return True

    def do_ticker(self,arg):
        '''Bitstamp ticker'''
        print("ticker")

    def _get_pairs(self):
        '''Load trading pairs'''
        print("pairs")

    def do_pairs(self,arg):
        '''Get Trading pairs '''
        for p in self._get_pairs():
            print( "{name:>8} {url_symbol:>8} {description}".format(**p) )


    def do_balance(self,arg):
        "Active ballance of the account"
        print("balance")

    def do_transactions(self,arg):
        "Show my transactions"
        print("transactions")

    def do_orders(self,arg):
        "Show Orders"
        print("orders")

    def do_order(self,arg):
        '''Report single order '''
        print("orders")

    def do_bids(self,arg):
        "Show (relevant) bids"
        lastprice = float(self.api.ticker()['last'])
        allbids = self.api.order_book()['bids']
        okbids = [ b for b in allbids if abs( float(b[0])/lastprice - 1) < 0.01 ]
        print(okbids)

    def report(self,d):
        for k,v in d.items():
            print( "{key:>16}:{value!s:>16}".format(key=k,value=v))

    def table(self,table):
        if len(table) == 0 :
            print ("none")
            return

        keys = table[0].keys()
        header = "\t".join( keys )
        rowtemplate = "\t".join( [ '{'+k+'}' for k in keys] )

        print(header)
        for row in table :
            print( rowtemplate.format(**row) )


async def counter():
    global mycounter
    while not quit_requested:
        await asyncio.sleep(2)
        mycounter += 2

if __name__ == '__main__':
    config = SafeConfigParser()
    config.read("CryptoGladiator.conf")
    try:
        exlist = config.get("Main", "exchanges")
        for exname in [x.strip() for x in exlist.split(',')]:
            apikey = config.get(exname, "api_key")
            secret = config.get(exname, "api_secret")
            print (exname,apikey,secret)

    except (KeyError, NoSectionError) as e:
        print(e)
        sys.exit()
    loop = asyncio.get_event_loop()
    cmd = loop.run_in_executor(executor=None, func=CryptoGladiator().cmdloop)
    futures = asyncio.gather(counter(),cmd)
    print(futures)
    try:
        loop.run_until_complete(futures)
    except ValueError:
        print ("name error excepted")

    finally:
        loop.close()

from expressoptionchain.option_stream import OptionStream
from expressoptionchain.helper import get_secrets
from expressoptionchain.option_chain import OptionChainFetcher
from datetime import datetime, timedelta

date_now = datetime.now().strftime('%Y-%m-%d')
# the option stream start should be in main module
if __name__ == '__main__':
    # by default secrets are fetched from ~/.kite/secrets
    secrets = get_secrets("d:\python_code\secret.json")  # or get_secrets(filename)

    # or
    # secrets = {
    #     'api_key': 'your_api_key',
    #     'api_secret': 'your_api_secret',
    #     'access_token': 'generated_access_token'
    # }

    # there is no limit on the number of symbols to subscribe to
    #symbols = ['NFO:NIFTY']


    criteria = {'name': 'percentage', 'properties': {'value': 12.5}}

    # stream = OptionStream(symbols, secrets,
    #                       expiry='23-02-2023',
    #                       criteria=criteria,
    #                       redis_config=RedisConfig(db=1)
    #                       )


    symbols = ['NFO:HDFCBANK',
               'NFO:AXISBANK',
               'NFO:ICICIBANK',
               'NFO:SBIN',
               'NFO:KOTAKBANK',
               'NFO:INDUSINDBK',
               'NFO:BAJFINANCE',
               'NFO:BAJAJFINSV',
               'NFO:RELIANCE',
               'NFO:TCS',
               'NFO:INFY'
               ]

    #### MONTHLY EXPIRY FOR STOCKS AND BN AND NIFTY
    ExpiryDate = '28-12-2023'

    with open('Expiry.txt', 'w') as file:
        file.write(ExpiryDate)

    stream = OptionStream(symbols,secrets,criteria=criteria,
                          expiry=ExpiryDate)

    # start the stream in a background thread
    # start will return once the subscription is started and the first ticks are received
    # this usually takes 20 sec.

    # By default, threaded is False. This allows you to run this process in foreground while you fetch the option chain
    # somewhere else.
    stream.start(threaded=True)

    # start fetching option chain
    option_chain_fetcher = OptionChainFetcher()

    # option chain for each trading symbol can be fetched in 3 ms
    # option_chain = option_chain_fetcher.get_option_chain('NFO:BANKNIFTY')

    # fetch option chain in bulk
    # option_chains = option_chain_fetcher.get_option_chains(
    #   ['NFO:BANKNIFTY'])
    # print(option_chains)
    # do some processing here

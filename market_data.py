

class Deribit:
    def __init__(self, expiry, strikes):
        self.ws = None
        self.expiry_code = expiry
        self.strikes = strikes
        self.instrument_data = {}
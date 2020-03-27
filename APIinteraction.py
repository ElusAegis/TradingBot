import requests as rq
from JSONconverter import parse_json_bytes


class Api:
    @staticmethod
    def handle_status_code(status_code, request):
        if status_code == 301:
            raise Warning("Being redirected!")
        elif status_code == 400:
            raise ConnectionError("Bad request {}!".format(request))
        elif status_code == 401:
            raise ConnectionRefusedError("Unauthenticated!")
        elif status_code == 403:
            raise ConnectionRefusedError("Forbidden access!")
        elif status_code == 404:
            raise ConnectionError("Server was not found!")
        elif status_code == 503:
            raise ConnectionRefusedError("Server is not ready for request!")
        else:
            raise ConnectionError("Unknown status code: {}!".format(status_code))


class BinanceApi(Api):
    @staticmethod
    def handle_status_code(status_code, request):
        if status_code == 429:
            raise RuntimeError("Request limit reached!")
        elif status_code == 418:
            raise RuntimeError("Banned API!")
        elif status_code == 1000:
            raise ConnectionError("Unknown error for request: {}!".format(request))
        elif status_code == 1001:
            raise ConnectionError("Disconnected!")
        elif status_code == 1002:
            raise ConnectionRefusedError("Unauthorised!")
        elif status_code == 1003:
            raise ConnectionRefusedError("Too many requests!")
        elif status_code == 1007:
            raise ConnectionRefusedError("Timeout!")
        elif status_code == 1022:
            raise ConnectionError("Invalid signature!")
        else:
            Api.handle_status_code(status_code, request)

    @staticmethod
    def conv_to_time(time_str):
        if time_str == "MINUTE":
            return 60
        elif time_str == "HOUR":
            return 3600
        elif time_str == "DAY":
            return 86400
        else:
            return 1

    def build_request(self, request_spec):
        return self.base_endpoint + request_spec

    def __init__(self, safe=False):
        self.safe = safe
        self.api_key = "usSziTXvOCyDwC3foIlDHwH89DYJzbV6p0SrZ5MW9vKS6egRbfkLu21RYNur2AjI"
        self.base_endpoint = "https://api.binance.com"

        info_request = "/api/v3/exchangeInfo"
        request = self.build_request(info_request)
        response = rq.get(request)

        self.connected = response.status_code == 200

        if self.connected and safe:
            self.exchange_info = parse_json_bytes(response.content)
            self.rq_balance_1m = self.exchange_info["rateLimits"][0]["limit"] - int(response.headers["X-MBX-USED-WEIGHT-1M"])
        elif self.connected:
            self.rq_balance_1m = 2000 - int(response.headers["X-MBX-USED-WEIGHT-1M"])


    def get_info(self):

        info_request = "/api/v3/exchangeInfo"
        request = self.build_request(info_request)
        response = rq.get(request)

        if response.status_code != 200:
            self.handle_status_code(response.status_code, response.request.url)

        response_parsed = parse_json_bytes(response.content)

        return response_parsed

    def get_cur_price(self, symbol):

        cur_price_request = "/api/v3/avgPrice"
        request = self.base_endpoint + cur_price_request
        params = {"symbol": symbol}

        response = rq.get(request, params=params)
        status_code = response.status_code

        if status_code != 200:
            self.handle_status_code(status_code, response.request.url)

        if self.safe:
            self.rq_balance_1m = self.exchange_info["rateLimits"][0]["limit"] - int(response.headers["X-MBX-USED-WEIGHT-1M"])
        else:
            self.rq_balance_1m = 2000 - int(response.headers["X-MBX-USED-WEIGHT-1M"])

        response_parsed = parse_json_bytes(response.content)

        return response_parsed["price"]

    def get_rq_balance(self):
        return self.rq_balance_1m


if (__name__ == "__main__"):
    api = BinanceApi()

    bnAPI = BinanceApi()
    if bnAPI.connected:
        while True:
            print(bnAPI.get_cur_price("LTCBTC"))
            print(bnAPI.get_rq_balance())

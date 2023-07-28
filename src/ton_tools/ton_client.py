import httpx
import urllib
import os

from typing import List

CONTRACT_TYPE = os.getenv('CONTRACT_TYPE')
TON_REST_API_SERVER = os.getenv('TON_REST_API_SERVER')
TONCENTER_URL = os.getenv('TONCENTER_URL')
TONCENTER_TOKEN = os.getenv('TONCENTER_TOKEN')

TGR_DEFAULT_WALLET = os.getenv('TGR_DEFAULT_WALLET')


class TonClient:
    __contract_types: List[str] = ['simpleR1', 'simpleR2', 'simpleR3', 'v2R1', 'v2R2', 'v3R1', 'v3R2', 'v4R1', 'v4R2']
    jettons = {
        'TGR': {
            'address': TGR_DEFAULT_WALLET,
        },
    }

    def __init__(self, contract_type: str, server: str, provider: str, provider_key: str) -> None:

        if contract_type not in self.__contract_types:
            raise Exception('Unknown type of wallet contract!')

        self.contract_type = contract_type
        self.server = server
        self.provider = provider
        self.provider_key = provider_key

    async def create_wallet(self):
        return await self.send('createWallet')

    async def get_balance(self, address: str):
        return await self.send('getBalance', {'address': address})

    async def get_transaction(self, address: str):
        return await self.send('getTransaction', {'address': address})

    async def send_transaction(self, mnemonics: str, to_address: str, amount: int, payload: str | None = None):
        return await self.send('sendTransaction', {
            'mnemonics': mnemonics,
            'toAddress': to_address,
            'amount': amount,
            'payload': payload,
        })

    async def send_transaction_jetton(self, mnemonics: str, to_address: str, amount: int, jetton: str):
        if jetton not in self.jettons:
            raise Exception('Unknown jetton!')

        return await self.send('sendTransaction', {
            'mnemonics': mnemonics,
            'toAddress': to_address,
            'amount': amount,
            'jetton': jetton,
        })

    async def send(self, method: str, data: dict = None) -> dict:
        if not data:
            data = {}

        query_data = {
            'provider': self.provider,
            'providerKey': self.provider_key,
            'type': self.contract_type,
            'jettons': self.jettons,
        }
        query = self.http_build_query({**query_data, **data})
        try:
            response_data = await self.request(f'{self.server}/{method}?{query}')
            if response_data['status'] == True:
                return {
                    'status': 'success',
                    'result': response_data['result'],
                }
            return {
                'status': 'error',
                'error': response_data['error'],
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Error on request: {e}',
            }

    async def request(self, url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

    def http_build_query(self, data: dict) -> str:
        def flatten_dict(d, parent_key=''):
            items = []
            for k, v in d.items():
                new_key = f'{parent_key}[{k}]' if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        params = flatten_dict(data)
        return urllib.parse.urlencode(params)


def get_ton_client():
    return TonClient(
        contract_type=CONTRACT_TYPE,
        server=TON_REST_API_SERVER,
        provider=TONCENTER_URL,
        provider_key=TONCENTER_TOKEN,
    )

def get_available_jettons():
    return list(TonClient.jettons.keys())
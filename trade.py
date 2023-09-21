import os
from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from web3 import Web3
import time
w3 = Web3(Web3.HTTPProvider(os.getenv("ENDPOINT")))
from web3.middleware import construct_sign_and_send_raw_middleware

decimals_abi = [
    # 合约的其他方法和事件
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]
allowence_abi = [
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]
approve_abi = [
    {
        "constant": False,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
swap_abi = [{"inputs": [{"internalType": "uint256","name": "amountOutMin","type": "uint256"},{"internalType": "address[]","name": "path","type": "address[]"},{"internalType": "address","name": "to","type": "address"},{"internalType": "uint256","name": "deadline","type": "uint256"}],"name": "swapExactETHForTokensSupportingFeeOnTransferTokens","outputs": [],"stateMutability": "payable","type": "function"}, {"inputs": [{"internalType": "uint256","name": "amountIn","type": "uint256"},{"internalType": "uint256","name": "amountOutMin","type": "uint256"},{"internalType": "address[]","name": "path","type": "address[]"},{"internalType": "address","name": "to","type": "address"},{"internalType": "uint256","name": "deadline","type": "uint256"}],"name": "swapExactTokensForETHSupportingFeeOnTransferTokens","outputs": [],"stateMutability": "nonpayable","type": "function"}]

# class DecimalInput(BaseModel):
#     """Inputs for decimal"""

#     tokenBuyDecimal: str = Field(description="Token to swap in")
#     tokenSellDecimal: str = Field(description="Token to swap out")

class TradeInput(BaseModel):
    """Inputs for trade"""

    side: str = Field(description="Side of trade")
    amount: str = Field(description="Amount of token to trade")
    token: str = Field(description="Token to trade")


# class DecimalTool(BaseTool):
#     name = "decimal"
#     description = """
#         Useful when you want to swap tokens.
#         You should enter the amount of token to swap in and out.
#         You should enter the token to swap in and out.
#         """
#     args_schema: Type[BaseModel] = DecimalInput

#     def _run(self, tokenBuy: str, tokenSell: str):
#         response = [18, 18]
#         print("------------------")
#         time.sleep(1)
#         print("------------------")
#         return response
    
#     def _arun(self, tokenBuy: str, tokenSell: str):
#         raise NotImplementedError("trade does not support async")
  

class TradeTool(BaseTool):
    name = "trade"
    description = """
        Useful when you want to swap tokens.
        You should enter the amount of token to swap in and out.
        You should enter the token to swap in and out.
        """
    args_schema: Type[BaseModel] = TradeInput
    return_direct: bool = True

    def _run(self, side: str, amount: str, token: str):
        # response = trade(amountBuy, amountSell, tokenBuy, tokenSell)
        # print(side)
        wallet = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(wallet))
        
        if side=="buy":
            print('buy')
            swap_contract = w3.eth.contract(address=os.getenv('ROUTE'), abi=swap_abi)
            swap = swap_contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(0, [os.getenv("WRAPTOKEN"), token], wallet.address, int(time.time()) + 1000).transact({'from': wallet.address, 'value': Web3.to_wei(amount, 'ether')})
            print(swap.hex())
        else:
            decimals_contract = w3.eth.contract(address=token, abi=decimals_abi)
            decimals = decimals_contract.functions.decimals().call()
            allowence_contract = w3.eth.contract(address=token, abi=allowence_abi)
            allowence = allowence_contract.functions.allowance(wallet.address, os.getenv('ROUTE')).call()
            if allowence < float(amount) * 10 ** int(decimals):
                print('waiting for approve')
                approve_contract = w3.eth.contract(address=amount, abi=approve_abi)
                approve = approve_contract.functions.approve(os.getenv('ROUTE'), float(amount) * 10 ** int(decimals)).transact({'from': wallet.address})
                print(approve.hex())
                print('sell')
            swap_contract = w3.eth.contract(address=os.getenv('ROUTE'), abi=swap_abi)
            swap = swap_contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(int(float(amount) * 10 ** int(decimals)), 0, [token, os.getenv("WRAPTOKEN")], wallet.address, int(time.time()) + 1000).transact({'from': wallet.address})
            print(swap.hex())
            
        # print(decimals)
        # print(allowence)
        print("------------------")
        print("------------------")
        return "success"
    
    def _arun(self, amountBuy: str, amountSell: str, tokenBuy: str, tokenSell: str):
        raise NotImplementedError("trade does not support async")
    
from brownie import *

def main():
    acct = accounts.load("rskdeployer")
    
    #deploy cotract and mint tokens
    earlyAccessToken = accounts[0].deploy(EarlyAccessToken, "Sovryn Early Access Token", "SEAT")
    earlyAccessToken.mint(acct)
    earlyAccessToken.mint('0x65299AddC002DD792797288eE6599772D20970Da')
    
    #todo load contracts
    contractSUSD = Contract.from_abi("loanToken", address="0xd8D25f03EBbA94E15Df2eD4d6D38276B595593c1", abi=LoanTokenLogicStandard.abi, owner=acct)
    contractWRBTC = Contract.from_abi("loanToken", address="0xa9DcDC63eaBb8a2b6f39D7fF9429d88340044a7A", abi=LoanTokenLogicStandard.abi, owner=acct)
    
    #set the early access token
    contractSUSD.setEarlyAccessToken(earlyAccessToken.address)
    contractWRBTC.setEarlyAccessToken(earlyAccessToken.address)
    
    #update the owner of the early access token
    earlyAccessToken.transferOwnership('0x417621fC0035893FDcD5dd09CaF2f081345bfB5C')
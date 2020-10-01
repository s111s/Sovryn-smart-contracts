#!/usr/bin/python3

from brownie import *
from scripts.deploy_protocol import deployProtocol
from scripts.deploy_loanToken import deployLoanTokens
from scripts.deploy_tokens import deployTokens, readTokens, deployWRBTC
from scripts.deploy_multisig import deployMultisig

import shared
import json
from munch import Munch

'''
Deploys all of the contracts.
1. deploys the tokens or reads exsiting token contracts.
    if configData contains token addresses, use the given addresses
    else, deploy new tokens
2. deploys the base protocol contracts.
3. deploys, configures and tests the loan token contracts.
4. writes the relevant contract addresses into swap_test.json.
'''
def main():
    global configData

    #owners = [accounts[0], accounts[1], accounts[2]]
    requiredConf=2
    configData = {} # deploy new tokens
    configData = {
        'WRBTC': '0x542fDA317318eBF1d3DEAf76E0b632741A7e677d',
        'SUSD': '0xE700691Da7B9851F2F35f8b8182C69C53ccad9DB',
        'medianizer': '0x7b19bb8e6c5188ec483b784d6fb5d807a77b21bf'
    }
    

    thisNetwork = network.show_active()

    if thisNetwork == "development":
        acct = accounts[0]
    elif thisNetwork == "testnet" or thisNetwork == "rsk-mainnet":
        acct = accounts.load("rskdeployer")
    else:
        raise Exception("network not supported")
    
    if('WRBTC' in configData and 'SUSD' in configData):
        tokens = readTokens(acct, configData['WRBTC'], configData['SUSD'])
    elif('SUSD' in configData):
        tokens = deployWRBTC(acct, configData['SUSD'])
    else:
        tokens = deployTokens(acct)
        
    if(not 'medianizer' in configData):
        medianizer = deployMoCMockup(acct)
        configData['medianizer'] = medianizer.address
        
    sovryn = deployProtocol(acct, tokens, configData['medianizer'])
    (loanTokenSUSD, loanTokenWRBTC, loanTokenSettingsSUSD, loanTokenLogicSUSD,
     loanTokenSettingsWRBTC, loanTokenLogicWRBTC) = deployLoanTokens(acct, sovryn, tokens)
     
    
    setTransactionLimit(acct, loanTokenSUSD, loanTokenSettingsSUSD, loanTokenLogicSUSD, tokens.susd.address, tokens.wrbtc.address)
    setTransactionLimit(acct, loanTokenWRBTC, loanTokenSettingsWRBTC, loanTokenLogicWRBTC, tokens.susd.address, tokens.wrbtc.address)   

    #deployMultisig(sovryn, acct, owners, requiredConf)
    
    configData["sovrynProtocol"] = sovryn.address
    configData["WRBTC"] = tokens.wrbtc.address
    configData["SUSD"] = tokens.susd.address
    configData["loanTokenSettingsSUSD"] = loanTokenSettingsSUSD.address
    configData["loanTokenSUSD"] = loanTokenSUSD.address
    configData["loanTokenSettingsWRBTC"] = loanTokenSettingsWRBTC.address
    configData["loanTokenRBTC"] = loanTokenWRBTC.address

    with open('./scripts/swap_test.json', 'w') as configFile:
        json.dump(configData, configFile)

def deployMoCMockup(acct):
    priceFeedMockup = acct.deploy(PriceFeedsMoCMockup)
    priceFeedMockup.setHas(True)
    priceFeedMockup.setValue(11653e18)
    return priceFeedMockup
    
    
def setTransactionLimit(acct, loanToken, loanTokenSettings, loanTokenLogic, SUSD, RBTC):
    localLoanToken = Contract.from_abi("loanToken", address=loanToken.address, abi=LoanToken.abi, owner=accounts[0])
    localLoanToken.setTarget(loanTokenSettings.address)
    localLoanToken = Contract.from_abi("loanToken", address=loanToken.address, abi=LoanTokenSettingsLowerAdmin.abi, owner=accounts[0])
    localLoanToken.setTransactionLimits([SUSD, RBTC],[21e18, 0.0021e18])
    localLoanToken = Contract.from_abi("loanToken", address=loanToken.address, abi=LoanToken.abi, owner=accounts[0])
    localLoanToken.setTarget(loanTokenLogic.address)
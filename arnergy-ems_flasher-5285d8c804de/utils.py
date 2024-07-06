import os
import json
import requests
from pathlib import Path  
from datetime import datetime 
bundle_dir = Path(__file__).parent
config = json.load(open(os.path.join(bundle_dir,'config.json'), 'r'))

def fetch_device_details(cid:str)->dict:
    """
        Description: Utility function for fetching the device setup certificate, and private key from the solar base API 
        Args: 
            cid (str) : Customer ID i.e. 416813
    """
    URL="https://iot-solarbase.arnergy.com/device/setup"
    payload = {
        "CID": cid
    }
    response = requests.post(URL, json=payload, timeout=10)
    print(response)
    if(response.status_code == 200):
        data = response.json()
        return data 
    else:
        return None

def format_flash_cid(cid:str)->str:
    """
        Description: Format the CID 
        Args: 
            cid (str) : Customer ID
    """
    return "101"+cid+"\0"

def format_flash_certificate(certificate:str)->list:
    """
        Description: Format the client certificate, break into chunks 
        Args: 
            certificate (str) : The client certificate 
    """
    y = [certificate[l:l+32] for l in range(0, len(certificate), 32)]
    final = map(lambda x: "1041"+"{:04d}".format(y.index(x)*32)+"{:04d}".format(len(certificate)-y.index(x)*32)+x, y)
    return list(final)
    
def format_flash_private_key(private_key:str)->list:
    """
        Description: Format the private key, break into chunks
        Args: 
            private_key (str) : The private key 
    """
    y = [private_key[l:l+32] for l in range(0, len(private_key), 32)]
    final = map(lambda x: "1042"+"{:04d}".format(y.index(x)*32)+"{:04d}".format(len(private_key)-y.index(x)*32)+x, y)
    return list(final)
        
def format_flash_network(name:str, mode:int=1, format:str='sim')->str:
    """
        Description: Format the network APN
        Args: 
            name (str) : The name of the SIM card 
            mode (int) : 1 for SIM1, 2 for SIM2
    """
    apn_map = config["NETWORKS"]
    if format=='sim':
        apn = apn_map[name]
    else:
        apn = name
    
    if mode==1:
        return "109"+apn 
    else:
        return "108"+apn

def format_system_type(name:str)->str:
    """
        Description: Format the System Type 
        Args:
            name (str) : The name of the System Type i.e. HV_SINGLE
    """
    system_types = map(lambda x:x.lower(),["5.4kWh System","5.4kWh System with TOPBMU","HV_SINGLE","HV_MULTIPLE"])
    system_types_map = dict(zip(system_types,[0,1,2,3]))
    name = name.lower()
    return "118"+str(system_types_map[name])

def format_log(log:str)->str:
    """
        Description: Format the log 
        Args:
            log (str): The log 
    """
    return f"{str(datetime.now())} - {log}"

if __name__ == "__main__":
    fetch_device_details("416813")
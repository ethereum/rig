def eth_to_gwei(eth):
    return eth * (10 ** 9)

def gwei_to_eth(gwei):
    return float(gwei) / (10 ** 9)
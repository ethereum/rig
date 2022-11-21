---
title: 'RSA adaptive root bounty instances'
description: 'Bounties for breaking RSA Assumptions.'
---

To improve the cryptanalysis of new RSA assumptions needed for Verifiable Delay Functions (VDFs), in addition to the [previous paper bounties](/bounties/rsa/bounties), the Ethereum Foundation announced the following bounties for solving concrete instances of the [adaptive root problem](/bounties/rsa/assumptions) at the Stanford Blockchain Conference 2020:

## Challenges

### Challenge 0 -- CLAIMED

This bounty has now been claimed. That means you cannot redeem this bounty anymore but obviously feel free to use it to test your algorithms.

```
Modulus: 0xbdbbd27309fc78576ef48a2ed1fd835f9a35c4b23ab4191d476fc54245a04c588af
1c7b600c5009bcc064b58afa126aa49eca0c7dc02a92b1750b833172e85226e88290494fc11f1fd
3e78e788e5
Bounty: 1 ETH
```

### Challenge 1

```
Modulus: 0x7e50b8b8b973dd6422b77048168d24729c96c1144b4982a7871598af00fd908d485
41594d47bc80ae03db5ca666f8ceff7d36bafeff7701d0de71a79b552fac7a431928761a42d8186
97920a0c8274100fe3950fd2591c50888432c685ac2d5f
Bounty: 4 ETH
```

### Challenge 2

```
Modulus: 0xa8046dd12415b1ccf11d841a39a39287bf2c761c7779e8bfef7fa7886793ea326b9
ecc7c4cb600688595e64b26ee45685919473bc09862f8783d24fea6433decc2500f724f0c26b000
7f76af9cda8f9b3576acfa3206c3432f03358184259dbbd813032cfb21634d6df7957a1bf1676ae
b90750d85f6715c351c595a14fe373b
Bounty: 8 ETH
```

### Challenge 3

```
Modulus: 0x7efce54e174bb141d000b4375659f45ac1e3e9ccc1afcde85cc98b7b6ce62645736
1e90d1d9fe0af72ba63f3b0d20af8084bd6f981584af1e9197288811e72afaf488a1360e4d5d6f9
b08220e16dd05860bd571e3171eb10dcc60241bf6f64cf03ddfb0556aa9a61e9850874e442564c0
20cf283813f5215d36281748b766ffa8a3486cd70686b5590d499a1a72d9baa87c0dc223c8f5b71
d18fd24888b2872f0530be8cde0f7be8f591848bc210f2966dcaab6853d09bfd550ebdcd244c394
cc83ac19ec75bf8b82774719555483cc2e3fbac3201c1aa518d25fdb37d50e56f3515ad5e4609d2
52fa7ded3b5123c0abc8a0ce137ef9989843d1452b87ccca6b
Bounty: 16 ETH
```

## How to redeem

In order to redeem a bounty, you must be able to solve an instance of the adaptive root problem modulo the given modulus. The exact documentation on how to solve such an instance can be found in the readme to the [contract repository](https://github.com/dankrad/rsa-bounty).

The bounty contract is deployed at address [0x62A940646e8F9FCEAc28454414Bb6133a54055Ea](https://etherscan.io/address/0x62a940646e8f9fceac28454414bb6133a54055ea) on the Ethereum blockchain.

If you need help redeeming a bounty please write to [dankrad@ethereum.org](mailto:dankrad@ethereum.org).

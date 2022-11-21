---
title: 'Legendre PRF Bounties for concrete instances'
description: 'Bounties on breaking the Legendre PRF.'
---

In addition to the [algorithmic bounties](/bounties/legendre-prf/algorithmic-bounties) announced at CRYPTO'19 in order to improve the state of cryptanalysis of the Legendre PRF, the Ethereum Foundation also wants to encourage concrete algorithmic development. In total, there are five key recovery challenges for the Legendre PRF -- if you can find the key belonging to the output bits below, you will be rewarded the bounties.

## Redeeming the bounties

The smart contract for redeeming the bounties is now live at [0x64af032181669383a370aE6e4b438ee26bB559b7](https://etherscan.io/address/0x64af032181669383a370ae6e4b438ee26bb559b7).

You can find instructions on claiming the bounties using the smart contract [here](/bounties/legendre-prf/smart-contract-instructions).

### Test challenge

```
Prime: 0x000000000000000000000000000000000000000000000000000000ffffffffa9
Challenge value (First 256 bytes): 782408b40187dec329043bcf60b4d9769c1a567bac18bf18aab7bd7bb484b16
e674842ce9f8d1788fe213a7d89f5677ac056c364a18d13cc726c898a39e4574204759df225b755faf4c23f797cd78495b2
fab46d396a0fc9c290f4fc863e856cb9fd6c8935aa34c0c19fca115e1f803d5e2cd9c0d9dcace708c1d9d956f4ce780b67b
1a8eb43b4f9e10e253e6991ae7fe4ef8e52fb9083db0ffc609979e395840369ad121b7db0b5b5ec134254a52947acfcb22a
092b33476e5302888869d2e261bd0cc7dd347d1bcede0cca8cd980f32cad329c2d3af752ca5b2f1c8ff0ddab0526ff55a45
94470ab7912775a67dfc3cea477a00ca4d37d49612315bccc5ef3
```

**Full challenge bits:** [test.bin](/instances/test.bin)

There is no bounty on this challenge. Use this to test your algorithm. You should find the key:

```
Key: 0x0000000000000000000000000000000000000000000000000000004e2dea1f3c
```

### Challenge 0 -- CLAIMED

This challenge has been claimed! Congratulations to Ward Beullens and Tim Beyne.

Unfortunately, this means you cannot win 1 ETH anymore, but you can still use this challenge to test your algorithm.

```
Prime: 0x000000000000000000000000000000000000000000000000ffffffffffffffc5
Bounty: 1 ETH
Challenge value (First 256 bytes): 574fb3b032a69799873a3335cf928752b630e7785d76276845ed02e3fd290b0
a118c35585f940cf1bf4183bf377301a2b9dba8f9acd3d937026cdc0097994c59feca7e0926f91a0eb64c29391b5a7e1cfd
f30d7346e0da11214f5e280f29644fd09092ab9ecb761fe23f4c4b71fe4cf8e4964577ed41a2a71edb3229d196ce7bafc81
babb01eebd972b9e87ad4663d4a43ed4ecbe4c7fc3f33a4b8e75f42e936cb9985441ca0bc5fee50793ccfdddbbc56e06f9b
83d739211f988610cdc8a31a13f25927d6cd7c86774d7eb56c6d08d0c13bf81137426a20ca6dd4e2a4de3340c476c537b17
2989ac5e7bc6966cfcea47bddceec01b36c49c5a7fbdeae9479f9
```

**Full challenge bits:** [0.bin](/instances/0.bin)

The correct key for this challenge is:

```
Key: 0x000000000000000000000000000000000000000000000000090644c931a3fba5
```

### Challenge 1 -- CLAIMED

This challenge has been claimed, see transaction on [etherscan](https://etherscan.io/tx/0xb9ee411d12356bf56685283ca42f5c6b5b9b644d0b37bc2e729aa395eedb0ec8).

Unfortunately, this means you cannot win 2 ETH anymore, but you can still use this challenge to test your algorithm.

```
Prime: 0x0000000000000000000000000000000000000000000003ffffffffffffffffdd
Bounty: 2 ETH
Challenge value (First 256 bytes): 5bfc5abb616dcb96eb812884d9be93ef9f42ed96079ab60230a3f874b15a965
36e85568932a1d06d120da7eae0aabf2aa23915be33f4c2613ce858d72c830fb511eef1dd6d08dc1323d96d9a6e938bc870
dfea145938ea8628c2a03a6349289cad65e65eea7c5b0209f44daadccb258ecc8b0aa638c8f0020f53a011f8bb0cb374099
28d98773a157442087b5970473965b5d0bb33cd6340b15da4c9019eef98a1e009d0c4a0924013e33b648edacc4d3cd0077d
335773913d7ea7de8302a3d8de66f44e54ce7ca834971f895d748a9558765ba3f1530c3f47af8979a5d33f61ff8289ea3bc
86bff8849a59d5302e1bbea33048b71d5e9ef93cd5d98716d8c35
```

**Full challenge bits:** [1.bin](/instances/1.bin)

The correct key for this challenge is

```
Key: 0x000000000000000000000000000000000000000000000384f17db02976dcf63d
```

### Challenge 2 -- CLAIMED

This challenge has been claimed.

Unfortunately, this means you cannot win 4 ETH anymore, but you can still use this challenge to test your algorithm.

```
Prime: 0x0000000000000000000000000000000000000000000fffffffffffffffffffdd
Bounty: 4 ETH
Challenge value (First 256 bytes): bafca94ade9b5201633be31512efcaec7cbe64cbfd2806e83ca398ee34209e0
1a14bc727418baa31692ebc91681018527738fea54c9f1d45233fff8de5cce971b2111e012374f10ee3fbca4e276313ba8f
fed1f400f1d5e046ffad63b6f48caecb7668b263190d1b0d822397b1fd72cf6a5c24f80af7254240bb432a6bb518588950e
82b07e63980bbdd754ce80b39090ba04c52e4e186f42f75e7f9bd097fdf23105f123a7b95101dd053e66d84a2ddbc939815
986ca510e29f2864df6a513f143800f79cc62bfed7d4b2ba0a128090ac2e7a2b4857bb703cd425f941d8e47c80ef243a770
5f05beef1c4a0d2dabb1cbc22bca06bd935ca25a7237ffee5bfcc
```

**Full challenge bits:** [2.bin](/instances/2.bin)

The correct key for this challenge is

```
Key: 0x0000000000000000000000000000000000000000000027aaa97c746c22e12d04
```

### Challenge 3

```
Prime: 0x000000000000000000000000000000000000000ffffffffffffffffffffffff1
Bounty: 8 ETH
Challenge value (First 256 bytes): 8544ea9871766a120112b6106bb0a2e6e34c5f0951dfb43a59932f879c3e0d9
562081fa5ad54e94fd7002046eaf9f2303d7572a1aabe6592a4906e20a096128a01e919fff32afd2a1979deb5153f5a7910
1a00065b4dbd7d16edbef103f180f8ee75e2950c7073911b4e51bb8ce4caf97b7f66b81d816c08b71a34015a097a5933ec7
dbca5a3d838c243a5168fb5a67cfb66c1bc7144ab026312cae2507cabf2f5a515b29bace620e38586de37e1985cabe8edff
b058daad0015a8928ffdbdb7f4bcbaf637c534855b8c22f45434bfcba01c27fe730f835cca95af3094b6f97e58e53680f20
08c4c3b0d7fa5dc6a34e8fa3bd427498c5a37a2bf464c2cacba72
```

**Full challenge bits:** [3.bin](/instances/3.bin)

These values will be used by the bounty smart contract to check the correctness of the solution:

```
Check value: 0x0000000000000000000000000008544ea9871766a120112b6106bb0a2e6e34c5
Check length: 148
```

### Challenge 4

```
Prime: 0x000000000000000000000000000fffffffffffffffffffffffffffffffffff59
Bounty: 16 ETH
Challenge value (First 256 bytes): aaf064eee3a15f46755777368a8abc00f274ea7a4ed4790e598067b2e671de7
686d281f889b28490de26b223cb0bbfb12ae6d9fee7aa0cf0d7f539a8f27eb2a71b991621f351f02ba0815e11e915655e4f
348bb574fc0a856cb104f8e8df38a2330b4713ec6bc23781a4a5b1c1e906689bff0d78068b5250208cdf76b589c03a0d557
26f9947a2b3978bead45d38a1647bc596cf27e509764f2d24114a01e2a8ca03982593a32eda0deafaeb6306ab00c78e6319
e2486a9a4016075ae1191314083e776405376a1a73a393f8220f8b1f8f5fde8e88bde5a312429a228e57fe96f036888167b
9dfdb86337baf82fc617632e91386ab4959d51e43156ba9cf980b
```

**Full challenge bits:** [4.bin](/instances/4.bin)

These values will be used by the bounty smart contract to check the correctness of the solution:

```
Check value: 0x000000000000000000000000000aaf064eee3a15f46755777368a8abc00f274e
Check length: 148
```

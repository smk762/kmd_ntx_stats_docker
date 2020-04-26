#!/usr/bin/env python3
import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress

class KMD_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 60,
                       'SCRIPT_ADDR': 85,
                       'SECRET_KEY': 188}

bitcoin.params = KMD_CoinParams

notary_pubkeys = {
    "madmax_NA": "0237e0d3268cebfa235958808db1efc20cc43b31100813b1f3e15cc5aa647ad2c3",
    "alright_AR": "020566fe2fb3874258b2d3cf1809a5d650e0edc7ba746fa5eec72750c5188c9cc9",
    "strob_NA": "0206f7a2e972d9dfef1c424c731503a0a27de1ba7a15a91a362dc7ec0d0fb47685",
    "hunter_EU": "0378224b4e9d8a0083ce36f2963ec0a4e231ec06b0c780de108e37f41181a89f6a",
    "phm87_SH": "021773a38db1bc3ede7f28142f901a161c7b7737875edbb40082a201c55dcf0add",
    "chainmakers_NA": "02285d813c30c0bf7eefdab1ff0a8ad08a07a0d26d8b95b3943ce814ac8e24d885",
    "indenodes_EU": "0221387ff95c44cb52b86552e3ec118a3c311ca65b75bf807c6c07eaeb1be8303c",
    "blackjok3r_SH": "021eac26dbad256cbb6f74d41b10763183ee07fb609dbd03480dd50634170547cc",
    "chainmakers_EU": "03fdf5a3fce8db7dee89724e706059c32e5aa3f233a6b6cc256fea337f05e3dbf7",
    "titomane_AR": "023e3aa9834c46971ff3e7cb86a200ec9c8074a9566a3ea85d400d5739662ee989",
    "fullmoon_SH": "023b7252968ea8a955cd63b9e57dee45a74f2d7ba23b4e0595572138ad1fb42d21",
    "indenodes_NA": "02698c6f1c9e43b66e82dbb163e8df0e5a2f62f3a7a882ca387d82f86e0b3fa988",
    "chmex_EU": "0281304ebbcc39e4f09fda85f4232dd8dacd668e20e5fc11fba6b985186c90086e",
    "metaphilibert_SH": "0284af1a5ef01503e6316a2ca4abf8423a794e9fc17ac6846f042b6f4adedc3309",
    "ca333_DEV": "02856843af2d9457b5b1c907068bef6077ea0904cc8bd4df1ced013f64bf267958",
    "cipi_NA": "02858904a2a1a0b44df4c937b65ee1f5b66186ab87a751858cf270dee1d5031f18",
    "pungocloud_SH": "024dfc76fa1f19b892be9d06e985d0c411e60dbbeb36bd100af9892a39555018f6",
    "voskcoin_EU": "034190b1c062a04124ad15b0fa56dfdf34aa06c164c7163b6aec0d654e5f118afb",
    "decker_DEV": "028eea44a09674dda00d88ffd199a09c9b75ba9782382cc8f1e97c0fd565fe5707",
    "cryptoeconomy_EU": "0290ab4937e85246e048552df3e9a66cba2c1602db76e03763e16c671e750145d1",
    "etszombi_EU": "0293ea48d8841af7a419a24d9da11c34b39127ef041f847651bae6ab14dcd1f6b4",
    "karasugoi_NA": "02a348b03b9c1a8eac1b56f85c402b041c9bce918833f2ea16d13452309052a982",
    "pirate_AR": "03e29c90354815a750db8ea9cb3c1b9550911bb205f83d0355a061ac47c4cf2fde",
    "metaphilibert_AR": "02adad675fae12b25fdd0f57250b0caf7f795c43f346153a31fe3e72e7db1d6ac6",
    "zatjum_SH": "02d6b0c89cacd58a0af038139a9a90c9e02cd1e33803a1f15fceabea1f7e9c263a",
    "madmax_AR": "03c5941fe49d673c094bc8e9bb1a95766b4670c88be76d576e915daf2c30a454d3",
    "lukechilds_NA": "03f1051e62c2d280212481c62fe52aab0a5b23c95de5b8e9ad5f80d8af4277a64b",
    "cipi_AR": "02c4f89a5b382750836cb787880d30e23502265054e1c327a5bfce67116d757ce8",
    "tonyl_AR": "02cc8bc862f2b65ad4f99d5f68d3011c138bf517acdc8d4261166b0be8f64189e1",
    "infotech_DEV": "0345ad4ab5254782479f6322c369cec77a7535d2f2162d103d666917d5e4f30c4c",
    "fullmoon_NA": "032c716701fe3a6a3f90a97b9d874a9d6eedb066419209eed7060b0cc6b710c60b",
    "etszombi_AR": "02e55e104aa94f70cde68165d7df3e162d4410c76afd4643b161dea044aa6d06ce",
    "node-9_EU": "0372e5b51e86e2392bb15039bac0c8f975b852b45028a5e43b324c294e9f12e411",
    "phba2061_EU": "03f6bd15dba7e986f0c976ea19d8a9093cb7c989d499f1708a0386c5c5659e6c4e",
    "indenodes_AR": "02ec0fa5a40f47fd4a38ea5c89e375ad0b6ddf4807c99733c9c3dc15fb978ee147",
    "and1-89_EU": "02736cbf8d7b50835afd50a319f162dd4beffe65f2b1dc6b90e64b32c8e7849ddd",
    "komodopioneers_SH": "032a238a5747777da7e819cfa3c859f3677a2daf14e4dce50916fc65d00ad9c52a",
    "komodopioneers_EU": "036d02425916444fff8cc7203fcbfc155c956dda5ceb647505836bef59885b6866",
    "d0ct0r_NA": "0303725d8525b6f969122faf04152653eb4bf34e10de92182263321769c334bf58",
    "kolo_DEV": "02849e12199dcc27ba09c3902686d2ad0adcbfcee9d67520e9abbdda045ba83227",
    "peer2cloud_AR": "02acc001fe1fe8fd68685ba26c0bc245924cb592e10cec71e9917df98b0e9d7c37",
    "webworker01_SH": "031e50ba6de3c16f99d414bb89866e578d963a54bde7916c810608966fb5700776",
    "webworker01_NA": "032735e9cad1bb00eaababfa6d27864fa4c1db0300c85e01e52176be2ca6a243ce",
    "pbca26_NA": "03a97606153d52338bcffd1bf19bb69ef8ce5a7cbdc2dbc3ff4f89d91ea6bbb4dc",
    "indenodes_SH": "0334e6e1ec8285c4b85bd6dae67e17d67d1f20e7328efad17ce6fd24ae97cdd65e",
    "pirate_NA": "0255e32d8a56671dee8aa7f717debb00efa7f0086ee802de0692f2d67ee3ee06ee",
    "lukechilds_AR": "025c6a73ff6d750b9ddf6755b390948cffdd00f344a639472d398dd5c6b4735d23",
    "dragonhound_NA": "0224a9d951d3a06d8e941cc7362b788bb1237bb0d56cc313e797eb027f37c2d375",
    "fullmoon_AR": "03da64dd7cd0db4c123c2f79d548a96095a5a103e5b9d956e9832865818ffa7872",
    "chainzilla_SH": "0360804b8817fd25ded6e9c0b50e3b0782ac666545b5416644198e18bc3903d9f9",
    "titomane_EU": "03772ac0aad6b0e9feec5e591bff5de6775d6132e888633e73d3ba896bdd8e0afb",
    "jeezy_EU": "037f182facbad35684a6e960699f5da4ba89e99f0d0d62a87e8400dd086c8e5dd7",
    "titomane_SH": "03850fdddf2413b51790daf51dd30823addb37313c8854b508ea6228205047ef9b",
    "alien_AR": "03911a60395801082194b6834244fa78a3c30ff3e888667498e157b4aa80b0a65f",
    "pirate_EU": "03fff24efd5648870a23badf46e26510e96d9e79ce281b27cfe963993039dd1351",
    "thegaltmines_NA": "02db1a16c7043f45d6033ccfbd0a51c2d789b32db428902f98b9e155cf0d7910ed",
    "computergenie_NA": "03a78ae070a5e9e935112cf7ea8293f18950f1011694ea0260799e8762c8a6f0a4",
    "nutellalicka_SH": "02f7d90d0510c598ce45915e6372a9cd0ba72664cb65ce231f25d526fc3c5479fc",
    "chainstrike_SH": "03b806be3bf7a1f2f6290ec5c1ea7d3ea57774dcfcf2129a82b2569e585100e1cb",
    "hunter_SH": "02407db70ad30ce4dfaee8b4ae35fae88390cad2b0ba0373fdd6231967537ccfdf",
    "alien_EU": "03bb749e337b9074465fa28e757b5aa92cb1f0fea1a39589bca91a602834d443cd",
    "gt_AR": "0348430538a4944d3162bb4749d8c5ed51299c2434f3ee69c11a1f7815b3f46135",
    "patchkez_SH": "03f45e9beb5c4cd46525db8195eb05c1db84ae7ef3603566b3d775770eba3b96ee",
    "decker_AR": "03ffdf1a116300a78729608d9930742cd349f11a9d64fcc336b8f18592dd9c91bc"
}

notary_pubkeys_3P = {
    "madmax_NA": "02ef81a360411adf71184ff04d0c5793fc41fd1d7155a28dd909f21f35f4883ac1",
    "alright_AR": "036a6bca1c2a8166f79fa8a979662892742346cc972b432f8e61950a358d705517",
    "strob_NA": "02049202f3872877e81035549f6f3a0f868d0ad1c9b0e0d2b48b1f30324255d26d",
    "hunter_EU": "0378224b4e9d8a0083ce36f2963ec0a4e231ec06b0c780de108e37f41181a89f6a",
    "phm87_SH": "03889a10f9df2caef57220628515693cf25316fe1b0693b0241419e75d0d0e66ed",
    "chainmakers_NA": "030e4822bddba10eb50d52d7da13106486651e4436962078ee8d681bc13f4993e9",
    "indenodes_EU": "03a416533cace0814455a1bb1cd7861ce825a543c6f6284a432c4c8d8875b7ace9",
    "blackjok3r_SH": "03d23bb5aad3c20414078472220cc5c26bc5aeb41e43d72c99158d450f714d743a",
    "chainmakers_EU": "034f8c0a504856fb3d80a94c3aa78828c1152daf8ccc45a17c450f32a1e242bb0c",
    "titomane_AR": "0358cd6d7460654a0ddd5125dd6fa0402d0719999444c6cc3888689a0b4446136a",
    "fullmoon_SH": "0275031fa79846c5d667b1f7c4219c487d439cd367dd294f73b5ecd55b4e673254",
    "indenodes_NA": "02b3908eda4078f0e9b6704451cdc24d418e899c0f515fab338d7494da6f0a647b",
    "chmex_EU": "03e5b7ab96b7271ecd585d6f22807fa87da374210a843ec3a90134cbf4a62c3db1",
    "metaphilibert_SH": "03b21ff042bf1730b28bde43f44c064578b41996117ac7634b567c3773089e3be3",
    "ca333_DEV": "029c0342ce2a4f9146c7d1ee012b26f5c2df78b507fb4461bf48df71b4e3031b56",
    "cipi_NA": "034406ac4cf94e84561c5d3f25384dd59145e92fefc5972a037dc6a44bfa286688",
    "pungocloud_SH": "0203064e291045187927cc35ed350e046bba604e324bb0e3b214ea83c74c4713b1",
    "voskcoin_EU": "037bfd946f1dd3736ddd2cb1a0731f8b83de51be5d1be417496fbc419e203bc1fe",
    "decker_DEV": "02fca8ee50e49f480de275745618db7b0b3680b0bdcce7dcae7d2e0fd5c3345744",
    "cryptoeconomy_EU": "037d04b7d16de61a44a3fc766bea4b7791023a36675d6cee862fe53defd04dd8f2",
    "etszombi_EU": "02f65da26061d1b9f1756a274918a37e83086dbfe9a43d2f0b35b9d2f593b31907",
    "karasugoi_NA": "024ba10f7f5325fd6ec6cab50c5242d142d00fab3537c0002097c0e98f72014177",
    "pirate_AR": "0353e2747f89968741c24f254caec24f9f49a894a0039ee9ba09234fcbad75c77d",
    "metaphilibert_AR": "0239e34ad22957bbf4c8df824401f237b2afe8d40f7a645ecd43e8f27dde1ab0da",
    "zatjum_SH": "03643c3b0a07a34f6ae7b048832e0216b935408dfc48b0c7d3d4faceb38841f3f3",
    "madmax_AR": "038735b4f6881925e5a9b14275af80fa2b712c8bd57eef26b97e5b153218890e38",
    "lukechilds_NA": "024607d85ea648511fa50b13f29d16beb2c3a248c586b449707d7be50a6060cf50",
    "cipi_AR": "025b7655826f5fd3a807cbb4918ef9f02fe64661153ca170db981e9b0861f8c5ad",
    "tonyl_AR": "03a8db38075c80348889871b4318b0a79a1fd7e9e21daefb4ca6e4f05e5963569c",
    "infotech_DEV": "0399ff59b0244103486a94acf1e4a928235cb002b20e26a6f3163b4a0d5e62db91",
    "fullmoon_NA": "02adf6e3cb8a3c94d769102aec9faf2cb073b7f2979ce64efb1161a596a8d16312",
    "etszombi_AR": "03c786702b81e0122157739c8e2377cf945998d36c0d187ec5c5ff95855848dfdd",
    "node-9_EU": "024f2402daddee0c8169ccd643e5536c2cf95b9690391c370a65c9dd0169fc3dc6",
    "phba2061_EU": "02dc98f064e3bf26a251a269893b280323c83f1a4d4e6ccd5e84986cc3244cb7c9",
    "indenodes_AR": "0242778789986d614f75bcf629081651b851a12ab1cc10c73995b27b90febb75a2",
    "and1-89_EU": "029f5a4c6046de880cc95eb448d20c80918339daff7d71b73dd3921895559d7ca3",
    "komodopioneers_SH": "02ae196a1e93444b9fcac2b0ccee428a4d9232a00b3a508484b5bccaedc9bac55e",
    "komodopioneers_EU": "03c7fef345ca6b5326de9d5a38498638801eee81bfea4ca8ffc3dacac43c27b14d",
    "d0ct0r_NA": "0235b211469d7c1881d30ab647e0d6ddb4daf9466f60e85e6a33a92e39dedde3a7",
    "kolo_DEV": "03dc7c71a5ef7104f81e62928446c4216d6e9f68d944c893a21d7a0eba74b1cb7c",
    "peer2cloud_AR": "0351c784d966dbb79e1bab4fad7c096c1637c98304854dcdb7d5b5aeceb94919b4",
    "webworker01_SH": "0221365d89a6f6373b15daa4a50d56d34ad1b4b8a48a7fd090163b6b5a5ecd7a0a",
    "webworker01_NA": "03bfc36a60194b495c075b89995f307bec68c1bcbe381b6b29db47af23494430f9",
    "pbca26_NA": "038319dcf74916486dbd506ac866d184c17c3202105df68c8335a1a1079ef0dfcc",
    "indenodes_SH": "031d1584cf0eb4a2d314465e49e2677226b1615c3718013b8d6b4854c15676a58c",
    "pirate_NA": "034899e6e884b3cb1f491d296673ab22a6590d9f62020bea83d721f5c68b9d7aa7",
    "lukechilds_AR": "031ee242e67a8166e489c0c4ed1e5f7fa32dff19b4c1749de35f8da18befa20811",
    "dragonhound_NA": "022405dbc2ea320131e9f0c4115442c797bf0f2677860d46679ac4522300ce8c0a",
    "fullmoon_AR": "03cd152ae20adcc389e77acad25953fc2371961631b35dc92cf5c96c7729c2e8d9",
    "chainzilla_SH": "03fe36ff13cb224217898682ce8b87ba6e3cdd4a98941bb7060c04508b57a6b014",
    "titomane_EU": "03d691cd0914a711f651082e2b7b27bee778c1309a38840e40a6cf650682d17bb5",
    "jeezy_EU": "022bca828b572cb2b3daff713ed2eb0bbc7378df20f799191eebecf3ef319509cd",
    "titomane_SH": "038c2a64f7647633c0e74eec93f9a668d4bf80214a43ed7cd08e4e30d3f2f7acfb",
    "alien_AR": "024f20c096b085308e21893383f44b4faf1cdedea9ad53cc7d7e7fbfa0c30c1e71",
    "pirate_EU": "0371f348b4ac848cdfb732758f59b9fdd64285e7adf769198771e8e203638db7e6",
    "thegaltmines_NA": "03e1d4cec2be4c11e368ff0c11e80cd1b09da8026db971b643daee100056b110fa",
    "computergenie_NA": "02f945d87b7cd6e9f2173a110399d36b369edb1f10bdf5a4ba6fd4923e2986e137",
    "nutellalicka_SH": "035ec5b9e88734e5bd0f3bd6533e52f917d51a0e31f83b2297aabb75f9798d01ef",
    "chainstrike_SH": "0221f9dee04b7da1f3833c6ea7f7325652c951b1c239052b0dadb57209084ca6a8",
    "hunter_SH": "02407db70ad30ce4dfaee8b4ae35fae88390cad2b0ba0373fdd6231967537ccfdf",
    "alien_EU": "022b85908191788f409506ebcf96a892f3274f352864c3ed566c5a16de63953236",
    "gt_AR": "0307c1cf89bd8ed4db1b09a0a98cf5f746fc77df3803ecc8611cf9455ec0ce6960",
    "patchkez_SH": "03d7c187689bf829ca076a30bbf36d2e67bb74e16a3290d8a55df21d6cb15c80c1",
    "decker_AR": "02a85540db8d41c7e60bf0d33d1364b4151cad883dd032878ea4c037f67b769635" 
}

known_addresses = {
    "RY7kqi4ePxMPGxwawkiT6rK6vncVfxdQRb":"dwy_EU",
    "RFE6nkXV7QKBs9MA7pn7dTNRBS8UGjDGaM":"dwy_SH",
    "RC2C7HpNyqxqV8Tw5fQq6Bh412fywXYaKL":"dwy_SH"
}

for notary in notary_pubkeys:
    addr = str(P2PKHBitcoinAddress.from_pubkey(x(notary_pubkeys[notary])))
    known_addresses[addr] = notary

for notary in notary_pubkeys_3P:
    addr = str(P2PKHBitcoinAddress.from_pubkey(x(notary_pubkeys_3P[notary])))
    known_addresses[addr] = notary
# Request ledger — actin-code-inventory-001

Byte cap: 1,048,576. Text-file cap: 5 including README.  This ledger is
updated after each retained response; bytes are response-body bytes.

| # | UTC observed | Request | Status | Body bytes | SHA-256 | Kind | Cumulative bytes |
| --- | --- | --- | ---: | ---: | --- | --- | ---: |
| 01 | 2026-09-29T12:02:58Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/commits/main` | 200 | 3,070 | `6d0296eb8eb5e1dc12cde64af5cbc90064efefbb29297300de91bac21715d1d2` | metadata | 3,070 |
| 02 | 2026-09-29T12:03:29Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/trees/c5b54f0ff429515519a8355ef309aa07e28598e1` | 200 | 2,532 | `d4ac47f2ca5d053719a1efd55cb8afe57e84619cecaf362b73223ca5baf49933` | metadata | 5,602 |
| 03 | 2026-09-29T12:04:28Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/blobs/f041d570f5c78bbc078d15447061b5df3bcb096a` | 200 | 100 | `da8698ba6d4800cd35caf6203d6f91740cde3ab18ef077bd3ebf8a5913c54a31` | text 1/5: README | 5,702 |
| 04 | 2026-09-29T12:04:53Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/trees/2e4b1ece0abb8ac05e36e423199e5b0b2a6c8607` | 200 | 2,771 | `43f7a84fcbda95b7277c682b3db9962021502009b9d89da7fd049162729ce993` | metadata | 8,473 |
| 05 | 2026-09-29T12:05:19Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/trees/60756719f1cc57e9afdf427d3fa439af4638f1a8` | 200 | 1,440 | `5d4a681d405dac827ea39e5a86a71b928f9bb1f3d9d8ed05325be461ba01b806` | metadata | 9,913 |
| 06 | 2026-09-29T12:05:44Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/trees/0c0d6ee84efc52cfe9010ec112d170b0842ee220` | 200 | 795 | `396ca9f6765b9b1fac5b3ead7f8e24a7ce889ed040c566f8358ad5bc4ca128e2` | metadata | 10,708 |
| 07 | 2026-09-29T12:06:11Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/trees/002a1f7d16a11500d94c3efc39ddc86db951daef` | 200 | 9,926 | `b9b2344e80f5ffa9efe138a3c493e57b23b4adc0cbafd5c3f78e6a9deb365f3e` | metadata | 20,634 |
| 08 | 2026-09-29T12:06:38Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/trees/59c361f5a4e5b9e3a72b20989c4b856dbc2881f4` | 200 | 3,356 | `e8d6b284df4adcf7c8eb624bc0c5c4e7268faa2b41849d91db81bec69f7f3468` | metadata | 23,990 |
| 09 | 2026-09-29T12:07:02Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/trees/c222b1ffb0b983b25d962d25bbe63d9995e55c64` | 200 | 2,734 | `c09573e36996622166eab323896fa834b20866d4b686f6dc70521fc1dded42f4` | metadata | 26,724 |
| 10 | 2026-09-29T12:07:37Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/blobs/ff728ebcc796c1761d3baa5b5d54204cd4d484d0` | 200 | 20,869 | `206e2cde3ffd6e919600427092925d7398c9c443fdc33e196cd773199ace8840` | text 2/5: `vary_spring_stiffness0000.cym` | 47,593 |
| 11 | 2026-09-29T12:08:27Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/blobs/b04b928ca84b7d6d268a140cebdecf5410e2a6fc` | 200 | 20,873 | `ac5da423536de0c3e4353c2576daf72631236acea36a426879bec07d9612f762` | text 3/5: `vary_spring_stiffness0008.cym` | 68,466 |
| 12 | 2026-09-29T12:08:55Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/blobs/9101d2bca8c800f832417d6456c43c15c1ab931d` | 200 | 20,850 | `0f525e70dac57fc0975c76b4dd606e8c7a9191506989d9326e40cab3b9ac24e5` | text 4/5: `endocytosis.cym` | 89,316 |
| 13 | 2026-09-29T12:09:28Z | `GET /repos/DrubinBarnes/Akamatsu_CME_manuscript/git/blobs/dc0d515d885023a8ba43eed6afc9d605621ff956` | 200 | 172,514 | `fa3caea61d948662ed05869a0788f0bcb696d0b2d7170d8f443a5037eed6457d` | text 5/5: `plot_multiple_param_sweeps_Akamatsu_2019.ipynb` | 261,830 |

No failed response has been retained so far. `01-commit.json` pins the current
branch tip at `e0d5426515abaa37fdc9cd3151e108480a0337eb`; this is a current
repository identity, not evidence that it is the paper-version revision.

The root tree supplies the Git blob SHA `f041d570f5c78bbc078d15447061b5df3bcb096a`
for the retained README; response-body SHA-256 is listed in the table.

The root/cytosim/sweep trees supply Git blob SHA
`ff728ebcc796c1761d3baa5b5d54204cd4d484d0` for retained configuration text.

The plotting tree supplies Git blob SHA
`dc0d515d885023a8ba43eed6afc9d605621ff956` for the retained notebook. The
five-text-file cap is now exhausted. All 13 retained requests returned HTTP 200;
failed-response count is zero. Total retained response bytes are 261,830, below
the 1,048,576-byte cap.

# DASC Figshare manifest provenance

## Exact inventory snapshot

* **Source URL:** `https://api.figshare.com/v2/articles/12198225`
* **Retrieved:** 2026-09-22T11:53:24Z (UTC file timestamp, on this host).
* **Snapshot:** `figshare-article-12198225.json`, 165,380 bytes, UTF-8 without
  BOM, SHA-256
  `b13a66d30bf527e333018e75eec0f74aed4a6b07096d4a2cb05b130235fee8eb`.
* **Inventory asserted by this exact JSON:** article ID 12198225; DOI
  `10.35092/yhjc.12198225.v1`; 469 files; total deposited size
  223,348,360,171 bytes; article `modified_date` 2023-05-31T08:56:35Z.
  The JSON's `files` array has 466 names ending `.tif.bz2` and three small
  sidecars.
* **Published Figshare per-file checksum fields:** each member has
  `supplied_md5` and `computed_md5`.  The API reports equal values for both
  locally downloaded sidecars.  Figshare did not provide a checksum for the
  article JSON response itself, so the SHA-256 above is a local provenance hash,
  not a publisher checksum.

## Retained payloads and hash checks

| File | Source URL | Bytes | Local SHA-256 | Local MD5 / Figshare `supplied_md5` / `computed_md5` |
| --- | --- | ---: | --- | --- |
| `Readme.docx` | `https://ndownloader.figshare.com/files/22438982` | 20,054 | `470484fbbf0aa4fa3354faf3980f0b0897bceaf551e275e16c479ebb2b123162` | `0df773328eb8714b23145ee6139b2fff` / same / same |
| `metadata.xlsx` | `https://ndownloader.figshare.com/files/22438985` | 11,520 | `7917726ec1f85982fca9a18c5d2eb0396ccc94e39a97d7e2f6547734ee7d5610` | `9f0e1067a07bcd5016ab3ef16ce97e1b` / same / same |

`Decompression.m` is present only in the manifest: Figshare file ID 22439129,
1,944 bytes, published MD5
`5273b76884797f8244c3a434ce622b88` (both API MD5 fields agree).  It was not
downloaded.  No image, archive, or movie payload was retrieved.

# Solnix RSA-2048 boot manifest profile

Solnix's detached boot-manifest signature uses RSA-2048 with RSASSA-PSS and
SHA-256. The PSS salt length equals the digest length (32 bytes). The versioned
header is:

```text
SOLNIX-BOOT-MANIFEST 1 SHA256 RSA-PSS-2048
```

The host-side signer is [`tools/secure-boot/boot-manifest.py`](../tools/secure-boot/boot-manifest.py).
It builds a canonical manifest from the selected illumos boot root, hashes
stored boot-file bytes with SHA-256, signs the exact manifest bytes, and checks
the manifest against the boot root again during verification. RSA-2048
signatures are 256 bytes.

Create the release key offline and keep it outside this repository and all boot
payloads:

```sh
umask 077
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 \
  -out solnix-manifest-private.pem
openssl pkey -in solnix-manifest-private.pem -pubout \
  -out solnix-manifest-public.pem
```

Sign and verify a staged boot root:

```sh
python3 tools/secure-boot/boot-manifest.py sign \
  /path/to/staged-root solnix-manifest-private.pem /path/to/output-bundle
python3 tools/secure-boot/boot-manifest.py verify \
  /path/to/staged-root solnix-manifest-public.pem /path/to/output-bundle
```

The EFI loader must pin Solnix's public key in authenticated loader code and
verify the complete manifest using SHA-256, RSA-PSS, and a 32-byte salt before
parsing or consuming manifest entries. A public key supplied beside the
manifest is not a trust anchor. The loader must compare each file digest to
this authenticated manifest and expose the same verified bytes to consumers.
The upstream patch files in this repository provide boot-file integration
references; they do not change the Solnix key or manifest profile.

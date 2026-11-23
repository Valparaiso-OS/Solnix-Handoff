# Solnix security port references

This repository collects the selected Secure Boot changes from [Valparaiso-illumos-gate](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate) as reviewable patch files for Solnix porting. The patches preserve the upstream diffs and commit identities.

Solnix uses the separate RSA-PSS-2048 manifest profile in [the signer](tools/secure-boot/boot-manifest.py) and [profile notes](docs/secure-boot-rsa2048.md). The Valparaiso patches are loader-integration references; Solnix's manifest identity and key profile are its own.

## Contents

### EFI loader manifest verification

Apply these commits in order as a reference series, after reviewing them against Solnix's pinned illumos-gate revision:

1. [`b6ff990eb62c`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/b6ff990eb62c)
2. [`40ad515cb878`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/40ad515cb878)
3. [`bf95fd2bf49f`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/bf95fd2bf49f)
4. [`fc52726ee6b1`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/fc52726ee6b1)
5. [`84ebebd20d81`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/84ebebd20d81)
6. [`59e2a2050065`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/59e2a2050065)
7. [`499cb370fe9b`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/499cb370fe9b)
8. [`8f04bcb1c704`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/8f04bcb1c704)
9. [`b0a977313b06`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/b0a977313b06)

These changes authenticate loader configuration and Forth includes, kernel and compressed boot archive inputs, constrain module loading and boot-root selection, and snapshot manifest-listed optional configuration.

### Supporting integration changes

- [`0464cf7f8515`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/0464cf7f8515) conditionally compiles the interactive helper for the enforcing EFI loader build.
- [`604bc6c2f107`](https://github.com/Valparaiso-OS/Valparaiso-illumos-gate/commit/604bc6c2f107) preserves signed EFI images byte-for-byte during `installboot`.

Patch files are under `patches/`; filenames use the full upstream commit SHA prefix. `security-roadmap.md` is the Solnix-focused security proposal.

## Porting notes

The patches are upstream reference changes, not a Solnix-ready branch. Review each diff against Solnix's own loader and installboot revisions, adapt paths and policy to Solnix, and use Solnix-owned keys and manifest identity. The Valparaiso QA manifest profile and keys are not part of this repository. Preserve the upstream illumos licensing and attribution when adapting source changes.

Build and test each layer on a disposable Solnix image, including valid boot, tampered-input rejection, installation/update preservation, rollback, and recovery. Record the exact Solnix revision and test environment with results.

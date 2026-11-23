# Solnix security roadmap proposal

This is a proposal for Solnix, adapted from security work documented in Valparaiso's
security roadmap. Valparaiso test results are not evidence that Solnix implements or
passes these controls. Solnix-specific source review and reproducible tests are required
before making any implementation or release claim.

## Current Solnix baseline

Solnix already documents private vulnerability reporting and coordinated disclosure,
Ed25519 signatures for binary cache paths, offline custody of the cache signing key,
and numbered key rotation. Keep that policy as the canonical reporting and cache-trust
document. This roadmap covers host, build, boot, and workload security.

## Priorities

### 1. Establish a repeatable baseline

- Record the exact Solnix and illumos revisions, target architecture, image type, and
  package/cache state for each security review.
- Inventory enabled SMF services, effective privileges, network listeners, package
  publishers and signature policy, boot configuration, ZFS datasets, and backup paths.
- Keep secrets, private keys, and credential values out of inventories and logs.
- Re-run the inventory on a fresh image for each supported architecture; do not
  generalize x86_64 evidence to aarch64, RISC-V, or SPARC.

### 2. Harden services and package builds

- Run service workers as dedicated unprivileged identities where supported. Review
  SMF method contexts, privileges, writable paths, inherited descriptors, and service
  dependencies; grant each service only what it needs.
- Put operations requiring elevated privileges behind narrow helpers and native,
  explicit authorization. Test both allowed and denied operations.
- For packages built from source, evaluate stack protection, immediate binding, and
  non-executable stack settings using the illumos toolchain and link-editor. Audit
  compiler commands and resulting ELF objects on clean builds. Do not assume GNU/Linux
  flags or protections work unchanged.
- Evaluate PIE, RELRO, heap protections, and control-flow protections against the
  actual Solnix runtime linker and kernel. Verify runtime mappings and negative cases
  before treating build flags as an effective control.

### 3. Protect boot, upgrades, and recovery

- Document the trust chain for install media, boot files, kernel, Nix closures, and
  binary-cache signatures, including key custody, rotation, revocation, and recovery.
- Test modified boot inputs and unsigned or incorrectly signed store paths in disposable
  environments. Record the exact rejection point and verify rollback remains available.
- Evaluate ZFS native encryption and key recovery for boot environments and backups.
  Test upgrade, rollback, failed unlock, and recovery before changing defaults.
- Treat ZFS checksums, Nix hashes, and cache signatures as distinct controls; none alone
  proves that the running root is authenticated.

### 4. Constrain workloads

- Use illumos zones for compatible workloads and document their host/guest boundaries.
  Treat LX-branded zones as a separate compatibility and isolation surface; validate
  them independently from native zones.
- Evaluate per-service filesystem and privilege restrictions using stable illumos
  interfaces. Any new confinement mechanism needs inherited-policy tests, denial tests,
  failure-mode handling, and audit coverage.
- Keep secrets out of application files, databases, and logs. Validate credential
  storage and its permissions on the actual desktop or service stack before claiming
  secure-memory or hardware-backed protection.

### 5. Assess cryptographic and supply-chain posture

- Record the configured Nix substituters and trusted public keys, verify cache signatures,
  and document the independent channel used to authenticate key changes.
- Inventory package source revisions, build provenance, binary-cache signing, TLS
  endpoints, SSH policy, certificates, and backup encryption. Never record key material.
- Assess cryptographic agility and post-quantum migration against the libraries,
  firmware, package clients, and remote peers Solnix actually supports. Keep experimental
  interoperability results separate from release claims.

## Acceptance evidence

A security control is considered implemented only when Solnix source or configuration
shows it, a clean build or fresh installation includes it, and a reproducible test checks
both the expected behavior and a relevant failure or denial case. Record platform,
architecture, image revision, and test boundary. VM results do not establish physical
firmware or all-hardware support.

## Deferred or platform-specific work

Valparaiso's OpenIndiana installer integration, its observed ASLR/noexecstack/
forbidnullmap profile, and experimental secure-boot loader are not assumed to apply
to Solnix. Solnix's manifest profile uses RSA-PSS-2048 with SHA-256. Reassess other
controls against Solnix's own source, toolchain, illumos revision, service
configuration, and supported hardware before adopting them.

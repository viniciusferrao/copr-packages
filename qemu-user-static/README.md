# qemu-user-static

RPM packaging for qemu-user-static on RHEL/EL 9 and 10.

**COPR:** https://copr.fedorainfracloud.org/coprs/viniciusferrao/qemu-user-static/

## Install

```bash
sudo dnf copr enable viniciusferrao/qemu-user-static
sudo dnf install qemu-user-static

# Or install only a specific architecture (e.g., x86_64 on ppc64le)
sudo dnf install qemu-user-static-x86
```

## About

`qemu-user-static` provides statically-linked QEMU user-mode emulation
binaries, enabling execution of foreign-architecture binaries inside
chroots and containers (e.g., running x86_64 binaries on ppc64le).

Red Hat deliberately excludes `qemu-user-static` from RHEL and EPEL — only
`qemu-kvm` is shipped. The Fedora `qemu` SRPM contains the `qemu-user-static`
subpackage, but it's disabled for RHEL builds via `%global user_static 0`.

This package is built from the Fedora dist-git SRPM with minimal patches to
re-enable the user-static subpackages on EL.

## How it works

The Fedora `qemu` SRPM (obtained via `fedpkg`) is patched and rebuilt. The
patch is minimal:

1. **Enable `user_static` on RHEL** — removes the `%if 0%{?rhel}` block that
   sets `user_static` to 0
2. **Add `pcre-static` for EL9** — glib2 on EL9 uses pcre1 (not pcre2), and
   the static linker needs `-lpcre`
3. **Replace `%autorelease`/`%autochangelog`** — produces clean `.elN` release
   tags instead of `.fcNN`

See [qemu-user-static-el.patch](qemu-user-static-el.patch) for the exact diff
from the upstream Fedora f44 spec.

## Files in this directory

```
qemu-user-static-el.patch   # Diff of our changes vs upstream Fedora spec
UPDATE-RUNBOOK.md            # Step-by-step update procedure
```

The full qemu spec (~3400 lines) and source tarball (~130 MB) are not included
in this repo. They live on the build server at `~/qemu-build/qemu/` (a fedpkg
dist-git clone).

## Targets

| EL version | ppc64le | x86_64 | Notes |
|------------|---------|--------|-------|
| EL10 | Yes | Yes | No extra COPR repos needed |
| EL9 | Yes | Yes | Needs AlmaLinux 9 CRB repo (shows "modified" on COPR) |
| EL8 | No | No | Requires meson >= 0.61.3; EL8 has 0.49 |

## Running standalone x86_64 binaries on ppc64le (optional)

The default binfmt_misc configuration is designed for container/chroot use
cases. To run standalone dynamically-linked x86_64 binaries directly on a
ppc64le host, additional setup is needed. See the
[COPR project instructions](https://copr.fedorainfracloud.org/coprs/viniciusferrao/qemu-user-static/)
or [UPDATE-RUNBOOK.md](UPDATE-RUNBOOK.md) for details.

**Limitation:** Binaries using JIT compilation (e.g., Node.js, Bun/JSC) will
not work under QEMU user-mode emulation due to TCG translation limitations.

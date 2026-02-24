# po4a - PO for anything

Updated po4a package from Fedora Rawhide for Enterprise Linux.

## Overview

- **Version:** 0.74 (from Fedora Rawhide / f44)
- **COPR:** https://copr.fedorainfracloud.org/coprs/viniciusferrao/po4a/
- **Upstream:** https://github.com/mquinson/po4a
- **Targets:** EL9 (ppc64le, x86_64), EL10 (ppc64le, x86_64)

## Why?

EL9 ships po4a 0.63 and EL10 ships 0.69 in CRB. This COPR provides the
latest upstream release (0.74) with EL-specific compatibility patches.

EL8 is **not supported** — po4a 0.74 requires Pod::Simple >= 3.43
(`_output_is_for_JustPod` API), and EL8 only has Pod::Simple 3.35.

## Patches

1. **`po4a-0.74-no-syntax-keyword-try.patch`** — Replaces
   `Syntax::Keyword::Try` with Perl's built-in `eval{}` in `Text.pm`.
   The `perl-Syntax-Keyword-Try` package is not available on EL9 and
   only in CRB on EL10. The single try/catch usage is trivially
   equivalent to eval.

2. **`po4a-0.74-fix-perlio-encoding.patch`** — Fixes a PerlIO
   `:encoding` buffer boundary bug in Perl 5.32 (EL9). Replaces
   PerlIO-based `:encoding(UTF-8)` file writes with manual
   `Encode::encode()` + raw I/O in `TransTractor.pm`. This bug causes
   spurious `\x{fffd}` errors when multi-byte characters span PerlIO
   internal buffer boundaries. Fixed upstream in Perl 5.36+.

## Install

```bash
dnf copr enable viniciusferrao/po4a
dnf install po4a
```

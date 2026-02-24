# po4a Update Runbook

## Overview

| Field | Value |
|-------|-------|
| COPR project | https://copr.fedorainfracloud.org/coprs/viniciusferrao/po4a/ |
| Upstream | https://github.com/mquinson/po4a |
| Fedora dist-git | https://src.fedoraproject.org/rpms/po4a |
| Chroots | epel-9-ppc64le, epel-9-x86_64, epel-10-ppc64le, epel-10-x86_64 |
| Workspace | `~/po4a-build/` |
| Spec location | `~/po4a-build/po4a/po4a.spec` |

## When to update

- New upstream po4a release on GitHub
- New Fedora Rawhide spec changes (check dist-git)
- New EL major version to support

## Package details

- **Architecture:** noarch (pure Perl)
- **Build system:** `perl Build.PL` / `./Build` / `./Build install`
- **Source:** Single tarball from GitHub, no Fedora-specific sources
- **Tests:** `./Build test || :` (non-fatal, some tests are flaky)

## Patches

| Patch | Purpose | May be removable when... |
|-------|---------|--------------------------|
| `po4a-0.74-no-syntax-keyword-try.patch` | Replace `Syntax::Keyword::Try` with `eval{}` in `Text.pm` | `perl-Syntax-Keyword-Try` is available in EPEL for all target EL versions |
| `po4a-0.74-fix-perlio-encoding.patch` | Fix PerlIO `:encoding` buffer bug in `TransTractor.pm` | EL9 is no longer a target (bug is in Perl 5.32, fixed in 5.36+) |

## Update procedure

### Step 1: Sync Fedora dist-git

```bash
cd ~/po4a-build/po4a
git pull
```

Or re-clone if needed:

```bash
cd ~/po4a-build
rm -rf po4a
fedpkg clone -a po4a --branch rawhide
```

### Step 2: Download source tarball

```bash
cd ~/po4a-build/po4a
spectool -g po4a.spec
```

### Step 3: Update spec for EL

Key changes from Fedora spec:

1. Set `Release: 1%{?dist}`
2. Add `Patch0: po4a-<version>-no-syntax-keyword-try.patch`
3. Add `Patch1: po4a-<version>-fix-perlio-encoding.patch`
4. Remove `BuildRequires: perl(Syntax::Keyword::Try)`
5. Remove `BuildRequires: texlive-kpathsea-bin` and `Requires: texlive-kpathsea-bin`
   (this subpackage does not exist on EL; `texlive-kpathsea` alone is sufficient)
6. Replace `%changelog` with a single entry
7. Verify patches still apply to the new version

### Step 4: Regenerate patches if version changed

Extract the new tarball and verify the patches apply:

```bash
cd ~/po4a-build
tar xzf po4a/po4a-<version>.tar.gz
cd po4a-<version>
patch -p1 --dry-run < ../po4a/po4a-<version>-no-syntax-keyword-try.patch
patch -p1 --dry-run < ../po4a/po4a-<version>-fix-perlio-encoding.patch
```

If patches don't apply, recreate them against the new source.

### Step 5: Build SRPM

```bash
cd ~/po4a-build/po4a
rpmbuild -bs po4a.spec \
  --define "_topdir $HOME/po4a-build/rpmbuild" \
  --define "_sourcedir $PWD" \
  --define "_srcrpmdir $PWD"
```

### Step 6: Submit to COPR

```bash
cd ~/po4a-build/po4a
copr-cli build viniciusferrao/po4a po4a-*.src.rpm
```

### Step 7: Verify installation

```bash
sudo dnf upgrade po4a
po4a --version
```

### Step 8: Update GitHub docs

```bash
cd ~/po4a-build/copr-packages
cp ~/po4a-build/po4a/po4a.spec po4a/
cp ~/po4a-build/po4a/po4a-*.patch po4a/
# Update README.md version references if needed
git add po4a/
git commit -m "po4a: update to <version>"
git push
```

## Key gotchas

- **Syntax::Keyword::Try** is used in ONE file (`lib/Locale/Po4a/Text.pm`)
  for a single try/catch around `YAML::Tiny->read_string()`. Trivially
  replaced with `eval{}`.

- **PerlIO encoding bug** manifests during `./Build` (not tests) when
  generating translated German man pages. Multi-byte UTF-8 characters
  at PerlIO internal buffer boundaries produce spurious `\x{fffd}`
  errors. Only affects Perl < 5.36.

- **texlive-kpathsea-bin** does not exist as a separate subpackage on
  EL. The `texlive-kpathsea` package alone provides everything needed.

- **EL8 is incompatible** with po4a >= 0.69. The `SimplePod/Parser.pm`
  module uses `Pod::Simple::_output_is_for_JustPod()` which was added
  in Pod::Simple 3.43. EL8 has Pod::Simple 3.35 (Perl 5.26).

- **perl(Unicode::GCString)** is in PowerTools on EL8 and AppStream on
  EL9/EL10. COPR chroots typically have these enabled.

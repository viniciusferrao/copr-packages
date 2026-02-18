# CDE COPR Update Runbook

## Overview

CDE (Common Desktop Environment) is the classic UNIX desktop environment based
on Motif. The official release is 2.5.3, with 45 post-release patches applied
for C23/GCC 15 compatibility, security fixes, and bug fixes.

Unlike qemu-user-static (which is ported from a Fedora SRPM), the CDE package
is built from scratch using a custom spec file. CDE is not in Fedora or EPEL.

- **COPR project:** https://copr.fedorainfracloud.org/coprs/viniciusferrao/cde/
- **Upstream:** https://sourceforge.net/projects/cdesktopenv/
- **Chroots:** epel-10-ppc64le, epel-10-x86_64, epel-9-ppc64le, epel-9-x86_64, epel-8-ppc64le, epel-8-x86_64
- **Spec:** ~/rpmbuild/SPECS/cde.spec
- **Sources:** ~/rpmbuild/SOURCES/

## When to update

- A new CDE release is published on SourceForge
- Important commits land upstream (security fixes, new platform support)
- A new EL version is released

## Package structure

The RPM is split into three subpackages:

- **cde** — binaries, config, systemd service, desktop session file
- **cde-libs** — shared libraries (libDtSvc, libDtWidget, libDtHelp, libcsa, libtt)
- **cde-devel** — headers and unversioned .so symlinks

CDE installs to `/usr/dt` (its native, non-relocatable prefix — hardcoded in
216+ source files).

## Source files

All source files live in `~/rpmbuild/SOURCES/`:

| File | Purpose |
|------|---------|
| `cde-2.5.3.tar.gz` | Official release tarball from SourceForge |
| `cde-2.5.3-post-release-fixes.patch` | 45 post-release commits (C23/GCC15, security, bugs) |
| `dt.conf` | `/etc/ld.so.conf.d/dt.conf` — adds `/usr/dt/lib` to linker path |
| `dt.sh` | `/etc/profile.d/dt.sh` — adds `/usr/dt/bin` to PATH (bash) |
| `dt.csh` | `/etc/profile.d/dt.csh` — adds `/usr/dt/bin` to PATH (csh) |
| `dtspc` | `/etc/xinetd.d/dtspc` — CDE subprocess control xinetd config |
| `fonts.alias` | Font alias file for CDE bitmap fonts |
| `fonts.dir` | Font directory file for CDE bitmap fonts |

## Updating to a new CDE release

### Step 1: Download the new tarball

```bash
cd ~/rpmbuild/SOURCES
curl -LO "https://downloads.sourceforge.net/cdesktopenv/cde-VERSION.tar.gz"
```

### Step 2: Update the patch (if needed)

If the new release includes all the post-release fixes, the patch can be
dropped. If not, regenerate it:

```bash
# Clone upstream git
git clone https://git.code.sf.net/p/cdesktopenv/code cde-git
cd cde-git

# Create patch from release tag to latest
git diff cde-VERSION..HEAD -- cde/ > ~/rpmbuild/SOURCES/cde-VERSION-post-release-fixes.patch
```

If the new release already includes all commits, remove the `Patch0:` line
and the `%patch -P0 -p2` line from the spec.

### Step 3: Update the spec file

Edit `~/rpmbuild/SPECS/cde.spec`:

```bash
vi ~/rpmbuild/SPECS/cde.spec
```

Changes needed:

**a) Update Version:**

```spec
Version:        NEW_VERSION
```

**b) Reset Release to 1:**

```spec
Release:        1%{?dist}
```

**c) Update Source0 if the URL pattern changed:**

```spec
Source0:        https://downloads.sourceforge.net/cdesktopenv/cde-NEW_VERSION.tar.gz
```

**d) Update or remove Patch0:**

If keeping the patch:
```spec
Patch0:         cde-NEW_VERSION-post-release-fixes.patch
```

If the new release includes everything:
```spec
# Remove the Patch0: line entirely
# Also remove: %patch -P0 -p2  (in %prep)
```

**e) Add a changelog entry:**

```spec
%changelog
* Thu Jun 05 2026 Vinicius Ferrão <vinicius@ferrao.net.br> - NEW_VERSION-1
- Update to CDE NEW_VERSION
```

### Step 4: Build the SRPM

```bash
rpmbuild -bs ~/rpmbuild/SPECS/cde.spec
```

The SRPM will be in `~/rpmbuild/SRPMS/cde-VERSION-RELEASE.*.src.rpm`.

### Step 5: Test locally with mock (optional but recommended)

```bash
mock -r alma+epel-10-ppc64le --rebuild ~/rpmbuild/SRPMS/cde-*.src.rpm \
    --resultdir ~/cde-build/results/el10-ppc64le/ \
    --no-clean 2>&1 | tee ~/cde-build/results/el10-ppc64le/build.log
```

### Step 6: Submit to COPR

Build for all chroots:

```bash
copr-cli build cde ~/rpmbuild/SRPMS/cde-*.src.rpm
```

Or build for specific chroots:

```bash
copr-cli build cde ~/rpmbuild/SRPMS/cde-*.src.rpm \
    --chroot epel-10-ppc64le --chroot epel-10-x86_64

copr-cli build cde ~/rpmbuild/SRPMS/cde-*.src.rpm \
    --chroot epel-9-ppc64le --chroot epel-9-x86_64

copr-cli build cde ~/rpmbuild/SRPMS/cde-*.src.rpm \
    --chroot epel-8-ppc64le --chroot epel-8-x86_64
```

Watch progress:

```bash
copr-cli watch-build BUILD_ID
```

### Step 7: Verify

```bash
sudo dnf clean metadata
sudo dnf upgrade cde
rpm -q cde
```

### Step 8: Clean up old builds (optional)

```bash
python3 -c "
import copr.v3
client = copr.v3.Client.create_from_config_file()
for b in client.build_proxy.get_list('viniciusferrao', 'cde'):
    print(f'Build {b.id}: {b.state} - {b.source_package.get(\"version\", \"?\")}')"
```

## Key spec details and gotchas

### Motif DisplayP.h config.h conflict

CDE's build includes Motif's `DisplayP.h` which tries to include `<config.h>`.
This conflicts with CDE's own build. The fix is in `%prep`:

```spec
echo '#include "cde_config.h"' > include/config.h
```

This redirects the include to CDE's actual config header. **Do not remove this.**

### Docs build is disabled

The documentation build is broken (dthelp_htag2 crashes), so the spec uses:

```spec
./configure --disable-docs
```

If a future release fixes the docs build, you can try removing `--disable-docs`.

### RPATH in binaries

CDE binaries have RPATH set to `/usr/dt/lib`. RPM normally rejects this, so
the spec suppresses the check:

```spec
%install
export QA_RPATHS=0x0002
```

This is intentional — CDE's libraries live in `/usr/dt/lib`, not in a standard
path, so RPATH is needed for the binaries to find them.

### x86_64 PIE fix

RHEL's hardened linker on x86_64 requires PIE objects. CDE's internal ksh93
build system doesn't use autoconf CFLAGS, so `-fPIE` must be injected manually:

```spec
%ifarch x86_64 i686
sed -i "s/CCFLAGS='/CCFLAGS='-fPIE /" programs/dtksh/Makefile
%endif
```

This was the cause of the Release 1 -> Release 2 bump. **Do not remove this.**

### sessreg availability across EL versions

The `sessreg` command is packaged differently per EL version:

| EL version | Package providing sessreg |
|------------|--------------------------|
| EL10 | `sessreg` (standalone) |
| EL9 | Not available — a stub is created during build |
| EL8 | `xorg-x11-server-utils` |

The spec handles this with conditionals:

```spec
%if 0%{?rhel} >= 10
BuildRequires:  sessreg
%endif
%if 0%{?rhel} == 8
BuildRequires:  xorg-x11-server-utils
%endif
```

And for EL9, a dummy sessreg is created in `%build`:

```spec
%if 0%{?rhel} == 9
mkdir -p _buildbin
echo '#!/bin/sh' > _buildbin/sessreg
chmod +x _buildbin/sessreg
export PATH="$(pwd)/_buildbin:$PATH"
%endif
```

### CDE is NOT relocatable

CDE has `/usr/dt` hardcoded in 216+ source files. **Do not attempt to change
the prefix** to `/usr` or any other FHS-compliant path — it will break in
subtle and catastrophic ways. The `/usr/dt` prefix is intentional and the
`dt.conf`, `dt.sh`, and `dt.csh` files handle library and PATH integration.

## Mock configs for local builds

| Target | Mock config |
|--------|-------------|
| EL10 ppc64le | `alma+epel-10-ppc64le` |
| EL9 ppc64le | `rocky+epel-9-ppc64le` |
| EL8 ppc64le | `alma+epel-8-ppc64le` |

## Adding a new EL version

```bash
copr-cli modify cde --chroot epel-11-ppc64le --chroot epel-11-x86_64
```

Then check:
- Is `sessreg` available as a standalone package? Update the conditionals.
- Do all BuildRequires resolve? Check for renamed/removed packages.
- Submit a test build and review the logs.

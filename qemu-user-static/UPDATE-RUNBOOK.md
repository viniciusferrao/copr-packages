# qemu-user-static COPR Update Runbook

## Overview

This COPR project builds `qemu-user-static` from the Fedora `qemu` SRPM with
minimal patches to enable the user-static subpackages on RHEL/EL. Red Hat
deliberately disables these in EPEL.

- **COPR project:** https://copr.fedorainfracloud.org/coprs/viniciusferrao/qemu-user-static/
- **Chroots:** epel-10-ppc64le, epel-10-x86_64, epel-9-ppc64le, epel-9-x86_64
- **Workspace:** ~/qemu-build/qemu/

## When to update

- A new stable Fedora release ships a new qemu version
- A security fix is released for qemu
- You want to add support for a new EL version

## Step 1: Find the latest Fedora branch

```bash
cd ~/qemu-build/qemu
git fetch --all
git branch -r | grep "origin/f4"
```

Pick the highest numbered stable branch (e.g., f44, f45, etc.).
Rawhide (`origin/rawhide`) tracks the next unreleased Fedora and may have
unstable dependencies — prefer the latest numbered branch.

Check the version:

```bash
git show origin/f45:qemu.spec | grep -E "^(Version|Epoch):"
```

## Step 2: Switch branch and download sources

```bash
cd ~/qemu-build/qemu
git checkout -b f45 origin/f45    # adjust branch name
fedpkg sources                     # downloads tarball from lookaside cache
```

## Step 3: Apply patches to qemu.spec

Three changes are needed. All are in `qemu.spec`:

### 3a. Enable user_static on RHEL

Find this block (around line 64):

```spec
%global user_static 1
%if 0%{?rhel}
# EPEL/RHEL do not have required -static builddeps
%global user_static 0
%endif
```

Replace with just:

```spec
%global user_static 1
```

### 3b. Add pcre-static for EL9

Find the `%if %{user_static}` BuildRequires block:

```spec
%if %{user_static}
BuildRequires: glibc-static
BuildRequires: glib2-static
BuildRequires: zlib-static
%endif
```

Add pcre-static for EL9 (glib2 on EL9 uses pcre1, not pcre2):

```spec
%if %{user_static}
BuildRequires: glibc-static
BuildRequires: glib2-static
BuildRequires: zlib-static
%if 0%{?rhel} && 0%{?rhel} < 10
BuildRequires: pcre-static
%endif
%endif
```

**Note:** This patch is only needed as long as EL9 is a target. EL10+ uses
pcre2, and glib2-static pulls pcre2-static automatically.

### 3c. Replace %autorelease and %autochangelog

Newer Fedora specs use `%autorelease` which produces `X.fcNN` release tags.
Replace with clean numbering for EL:

Find:

```spec
Release: %autorelease -p -e %{rcver}
%else
Release: %autorelease
```

Replace with:

```spec
Release: 0.1.%{rcver}%{?dist}
%else
Release: 1%{?dist}
```

At the bottom, find:

```spec
%changelog
%autochangelog
```

Replace with a manual entry:

```spec
%changelog
* Thu Jun 05 2026 Vinicius Ferrão <vinicius@ferrao.net.br> - 2:VERSION-1
- Rebuild from Fedora NN for EL9/EL10
- Enable user-static subpackages on RHEL
```

Adjust the date (`date +"%a %b %d %Y"`), VERSION, and Fedora number.

## Step 4: Build the SRPM

```bash
cd ~/qemu-build/qemu
fedpkg srpm
```

This produces `qemu-VERSION-RELEASE.fcNN.src.rpm`. The `.fcNN` in the SRPM
filename is normal — COPR rebuilds with the correct `.elN` dist tag.

## Step 5: Submit to COPR

Build for all chroots:

```bash
copr-cli build qemu-user-static ~/qemu-build/qemu/qemu-*.src.rpm
```

Or build for specific chroots:

```bash
copr-cli build qemu-user-static ~/qemu-build/qemu/qemu-*.src.rpm \
    --chroot epel-10-ppc64le --chroot epel-10-x86_64

copr-cli build qemu-user-static ~/qemu-build/qemu/qemu-*.src.rpm \
    --chroot epel-9-ppc64le --chroot epel-9-x86_64
```

Watch progress:

```bash
copr-cli watch-build BUILD_ID
```

## Step 6: Verify

```bash
sudo dnf clean metadata
sudo dnf upgrade qemu-user-static-x86
qemu-x86_64-static --version
```

## Step 7: Clean up old builds (optional)

List builds:

```bash
python3 -c "
import copr.v3
client = copr.v3.Client.create_from_config_file()
for b in client.build_proxy.get_list('viniciusferrao', 'qemu-user-static'):
    print(f'Build {b.id}: {b.state} - {b.source_package.get(\"version\", \"?\")}')"
```

Delete a specific build:

```bash
python3 -c "
import copr.v3
client = copr.v3.Client.create_from_config_file()
client.build_proxy.delete(BUILD_ID)"
```

## Troubleshooting

### EL10 build fails with zlib-ng-compat version mismatch

The EL10 chroots must NOT have an AlmaLinux CRB extra repo — CentOS Stream 10
CRB is already built into COPR's epel-10 chroots. Adding AlmaLinux CRB causes
version conflicts between `zlib-ng-compat-static` and `zlib-ng-compat-devel`.

Check and clear:

```bash
python3 -c "
import copr.v3
client = copr.v3.Client.create_from_config_file()
for c in ['epel-10-ppc64le', 'epel-10-x86_64']:
    ch = client.project_chroot_proxy.get('viniciusferrao', 'qemu-user-static', c)
    print(f'{c}: {ch.additional_repos}')
    # To clear:
    # client.project_chroot_proxy.edit('viniciusferrao', 'qemu-user-static', c, additional_repos=[])"
```

### EL9 build fails with "cannot find -lpcre"

The EL9 chroots need the AlmaLinux 9 CRB repo for `pcre-static`:

```bash
python3 -c "
import copr.v3
client = copr.v3.Client.create_from_config_file()
client.project_chroot_proxy.edit('viniciusferrao', 'qemu-user-static', 'epel-9-ppc64le',
    additional_repos=['https://repo.almalinux.org/almalinux/9/CRB/ppc64le/os/'])
client.project_chroot_proxy.edit('viniciusferrao', 'qemu-user-static', 'epel-9-x86_64',
    additional_repos=['https://repo.almalinux.org/almalinux/9/CRB/x86_64/os/'])"
```

This causes the "modified" label on EL9 chroots — that is expected and unavoidable.

### EL8 is not supported

qemu 9.1.3+ requires meson >= 0.61.3. EL8 ships meson 0.49. Not fixable.

### Adding a new EL version (e.g., EL11)

```bash
copr-cli modify qemu-user-static --chroot epel-11-ppc64le --chroot epel-11-x86_64
```

Then submit a build. Check if the new EL version needs any spec adjustments
(static library package names, CRB availability, etc.).

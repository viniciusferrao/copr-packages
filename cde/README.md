# CDE - Common Desktop Environment

RPM packaging for CDE 2.5.3 on RHEL/EL 8, 9, and 10.

**COPR:** https://copr.fedorainfracloud.org/coprs/viniciusferrao/cde/

## Install

```bash
sudo dnf copr enable viniciusferrao/cde
sudo dnf install cde
```

## About

CDE (Common Desktop Environment) is the classic UNIX desktop environment based
on Motif. Originally developed by a consortium including HP, IBM, Sun, and
Novell, it was open-sourced in 2012 and is actively maintained.

CDE is not available in Fedora, RHEL, or EPEL. This package builds it from
source with a custom spec file.

## Package contents

- **cde** — binaries, configuration, systemd service (`dtlogin.service`),
  X session file, xinetd configs
- **cde-libs** — shared libraries (libDtSvc, libDtWidget, libDtHelp, libcsa, libtt)
- **cde-devel** — headers and development symlinks

CDE installs to `/usr/dt` (its native, non-relocatable prefix).

## Files in this directory

```
cde.spec            # RPM spec file
sources/
├── dt.conf         # /etc/ld.so.conf.d/dt.conf — adds /usr/dt/lib to linker path
├── dt.sh           # /etc/profile.d/dt.sh — adds /usr/dt/bin to PATH (bash)
├── dt.csh          # /etc/profile.d/dt.csh — adds /usr/dt/bin to PATH (csh)
├── dtspc           # /etc/xinetd.d/dtspc — CDE subprocess control config
├── fonts.alias     # Font alias file for CDE bitmap fonts
└── fonts.dir       # Font directory file for CDE bitmap fonts
UPDATE-RUNBOOK.md   # Step-by-step update procedure
```

The tarball (`cde-2.5.3.tar.gz`) and patch (`cde-2.5.3-post-release-fixes.patch`)
are too large for this repo. They live on the build server at `~/rpmbuild/SOURCES/`.

- **Tarball:** https://downloads.sourceforge.net/cdesktopenv/cde-2.5.3.tar.gz
- **Patch:** Generated from upstream git (45 post-release commits for C23/GCC 15
  compatibility, security fixes, and bug fixes). See UPDATE-RUNBOOK.md for
  instructions on regenerating it.

## Targets

| EL version | ppc64le | x86_64 | Notes |
|------------|---------|--------|-------|
| EL10 | Yes | Yes | |
| EL9 | Yes | Yes | sessreg stub needed (not packaged) |
| EL8 | Yes | Yes | |

Name:           cde
Version:        2.5.3
Release:        2%{?dist}
Summary:        Common Desktop Environment

License:        LGPL-2.1-or-later
URL:            https://sourceforge.net/projects/cdesktopenv/
Source0:        https://downloads.sourceforge.net/cdesktopenv/cde-%{version}.tar.gz
Source1:        dt.conf
Source2:        dt.sh
Source3:        dt.csh
Source4:        dtspc
Source5:        fonts.alias
Source6:        fonts.dir

# 45 post-release commits: C23/GCC 15 compat, security fixes, bug fixes
Patch0:         cde-2.5.3-post-release-fixes.patch

%global cde_prefix /usr/dt

%{?systemd_requires}
BuildRequires:  systemd-rpm-macros
BuildRequires:  autoconf automake libtool gcc gcc-c++ make bison flex ksh m4 ncompress
BuildRequires:  motif-devel libXt-devel libXmu-devel libXft-devel libXinerama-devel libXpm-devel libXaw-devel
BuildRequires:  libX11-devel libXext-devel libXScrnSaver-devel libXdmcp-devel libXrender-devel libXp-devel
BuildRequires:  libXau-devel libICE-devel libSM-devel libjpeg-turbo-devel freetype-devel openssl-devel
BuildRequires:  tcl-devel ncurses-devel libtirpc-devel lmdb-devel libutempter-devel pam-devel
BuildRequires:  rpcgen xorg-x11-xbitmaps opensp mkfontscale bdftopcf xrdb

# sessreg availability differs across EL versions
%if 0%{?rhel} >= 10
BuildRequires:  sessreg
%endif
%if 0%{?rhel} == 8
BuildRequires:  xorg-x11-server-utils
%endif

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       ksh
Requires:       ncompress
Requires:       rpcbind
Requires:       motif

%description
CDE is the Common Desktop Environment, the classic UNIX desktop
environment based on Motif. Originally developed by a consortium
including HP, IBM, Sun, and Novell, it was open-sourced in 2012
and is actively maintained.

%package libs
Summary:        Shared libraries for CDE

%description libs
Shared libraries required by CDE and applications built against it.

%package devel
Summary:        Development files for CDE
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       motif-devel%{?_isa}

%description devel
Header files and development libraries for building applications
against the CDE libraries (libDtSvc, libDtWidget, libDtHelp, etc.).

%prep
%setup -q
%patch -P0 -p2
echo '#include "cde_config.h"' > include/config.h

%build
%if 0%{?rhel} == 9
mkdir -p _buildbin
echo '#!/bin/sh' > _buildbin/sessreg
chmod +x _buildbin/sessreg
export PATH="$(pwd)/_buildbin:$PATH"
%endif

./autogen.sh

CFLAGS="${CFLAGS:-%optflags}" CXXFLAGS="${CXXFLAGS:-%optflags}" \
LDFLAGS="${LDFLAGS:-%{?__global_ldflags}}" \
./configure --disable-docs

# ksh93 internal build system does not use autoconf CFLAGS; on x86_64
# RHEL hardened linker requires PIE objects, so inject -fPIE into ksh93 CCFLAGS
%ifarch x86_64 i686
sed -i "s/CCFLAGS='/CCFLAGS='-fPIE /" programs/dtksh/Makefile
%endif

%make_build

%install
export QA_RPATHS=0x0002
%make_install DESTDIR=%{buildroot}

# Remove libtool archives and static libraries
find %{buildroot} -name '*.la' -delete
find %{buildroot} -name '*.a' -delete

# Remove docs installed to CDE prefix root
rm -f %{buildroot}%{cde_prefix}/CONTRIBUTORS
rm -f %{buildroot}%{cde_prefix}/COPYING
rm -f %{buildroot}%{cde_prefix}/HISTORY
rm -f %{buildroot}%{cde_prefix}/README.md
rm -f %{buildroot}%{cde_prefix}/copyright

# systemd service
install -D -m 0644 contrib/rc/systemd/dtlogin.service \
    %{buildroot}%{_unitdir}/dtlogin.service

# Desktop session file
install -D -m 0644 contrib/desktopentry/cde.desktop \
    %{buildroot}%{_datadir}/xsessions/cde.desktop

# xinetd configs
install -d %{buildroot}%{_sysconfdir}/xinetd.d
install -m 0600 contrib/xinetd/ttdbserver %{buildroot}%{_sysconfdir}/xinetd.d/ttdbserver
install -m 0600 contrib/xinetd/cmsd %{buildroot}%{_sysconfdir}/xinetd.d/cmsd
install -m 0600 %{SOURCE4} %{buildroot}%{_sysconfdir}/xinetd.d/dtspc

# ld.so configuration
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/ld.so.conf.d/dt.conf

# PATH profile scripts
install -D -m 0755 %{SOURCE2} %{buildroot}%{_sysconfdir}/profile.d/dt.sh
install -D -m 0755 %{SOURCE3} %{buildroot}%{_sysconfdir}/profile.d/dt.csh

# Font config
install -D -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/dt/config/xfonts/C/fonts.alias
install -D -m 0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/dt/config/xfonts/C/fonts.dir

# Variable data directory
install -d -m 1777 %{buildroot}/var/dt

%post
%systemd_post dtlogin.service
grep -qE '^dtspc' /etc/services 2>/dev/null || \
    echo -e 'dtspc\t6112/tcp\t# CDE subprocess control' >> /etc/services

%preun
%systemd_preun dtlogin.service

%postun
%systemd_postun_with_restart dtlogin.service

%ldconfig_scriptlets libs

%files
%license COPYING
%doc CONTRIBUTORS HISTORY README.md
# CDE base directory
%dir %{cde_prefix}
%{cde_prefix}/bin
%{cde_prefix}/appconfig
%{cde_prefix}/app-defaults
%{cde_prefix}/config
%{cde_prefix}/infolib
%{cde_prefix}/backdrops
%{cde_prefix}/palettes
%{cde_prefix}/share
%{cde_prefix}/lib/nls
%{cde_prefix}/lib/dtksh
%{cde_prefix}/lib/cde
%{cde_prefix}/libexec
%{cde_prefix}/etc
# PAM configuration
%config(noreplace) %{_sysconfdir}/pam.d/dtlogin
%config(noreplace) %{_sysconfdir}/pam.d/dtsession
# System configuration
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/dt.conf
%config(noreplace) %{_sysconfdir}/profile.d/dt.sh
%config(noreplace) %{_sysconfdir}/profile.d/dt.csh
%config(noreplace) %{_sysconfdir}/dt
%config(noreplace) %{_sysconfdir}/xinetd.d/cmsd
%config(noreplace) %{_sysconfdir}/xinetd.d/dtspc
%config(noreplace) %{_sysconfdir}/xinetd.d/ttdbserver
# Variable data
%attr(1777, root, root) /var/dt
# systemd and session
%{_unitdir}/dtlogin.service
%{_datadir}/xsessions/cde.desktop

%files libs
%license COPYING
%dir %{cde_prefix}/lib
%{cde_prefix}/lib/libDt*.so.*
%{cde_prefix}/lib/libcsa.so.*
%{cde_prefix}/lib/libtt.so.*

%files devel
%{cde_prefix}/include
%{cde_prefix}/lib/libDt*.so
%{cde_prefix}/lib/libcsa.so
%{cde_prefix}/lib/libtt.so

%changelog
* Sun Feb 08 2026 CDE Builder <builder@versatushpc.com.br> - 2.5.3-2
- Fix x86_64 build: inject -fPIE into ksh93 internal build system
  (RHEL hardened linker requires PIE objects on x86_64)
* Sun Feb 08 2026 CDE Builder <builder@versatushpc.com.br> - 2.5.3-1
- CDE 2.5.3 release
- 45 post-release patches: C23/GCC 15 compat, security fixes (tmpnam to mkstemp),
  bug fixes (dtwm hourglass, dtmail dead code), XKB migration
- CDE native /usr/dt prefix
- Split into cde, cde-libs, cde-devel subpackages
- systemd integration with dtlogin.service
- EL8/EL9/EL10 support with sessreg conditionals

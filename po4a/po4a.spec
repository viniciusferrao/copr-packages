Name: po4a
Version: 0.74
Release: 1%{?dist}
Summary: A tool maintaining translations anywhere

# Note: source is imprecise about 2.0-only vs 2.0-or-later
# https://github.com/mquinson/po4a/issues/434
License: GPL-2.0-or-later
URL: https://po4a.org/

Source0: https://github.com/mquinson/po4a/archive/v%{version}/%{name}-%{version}.tar.gz

# Remove Syntax::Keyword::Try dependency for EL compatibility
# Replace try/catch with eval{} in Text.pm (only usage in codebase)
Patch0: po4a-0.74-no-syntax-keyword-try.patch
# Fix PerlIO :encoding buffer boundary bug in Perl 5.32 (EL9)
Patch1: po4a-0.74-fix-perlio-encoding.patch

BuildArch: noarch
BuildRequires: /usr/bin/xsltproc
BuildRequires: coreutils
BuildRequires: docbook-style-xsl
BuildRequires: findutils
BuildRequires: grep
# Requires a pod2man which supports --utf8
# Seemingly added in perl-5.10.1
BuildRequires: glibc-all-langpacks
BuildRequires: perl-interpreter >= 4:5.10.1
BuildRequires: perl-generators
BuildRequires: perl(lib)
BuildRequires: perl(Encode)
BuildRequires: perl(ExtUtils::Install)
BuildRequires: perl(File::Basename)
BuildRequires: perl(File::Copy)
BuildRequires: perl(File::Path)
BuildRequires: perl(File::Spec)
BuildRequires: perl(File::stat)
BuildRequires: perl(Module::Build)
BuildRequires: perl(Pod::Man)

# Run-time:
BuildRequires: gettext
BuildRequires: opensp
BuildRequires: perl(Carp)
BuildRequires: perl(Config)
BuildRequires: perl(Cwd)
BuildRequires: perl(DynaLoader)
BuildRequires: perl(Encode::Guess)
BuildRequires: perl(Exporter)
BuildRequires: perl(Fcntl)
BuildRequires: perl(File::Temp)
BuildRequires: perl(Getopt::Long)
BuildRequires: perl(Getopt::Std)
BuildRequires: perl(IO::File)
BuildRequires: perl(Pod::Parser)
BuildRequires: perl(Pod::Usage)
BuildRequires: perl(POSIX)
BuildRequires: perl(SGMLS) >= 1.03ii
BuildRequires: perl(strict)
BuildRequires: perl(subs)
BuildRequires: perl(Time::Local)
BuildRequires: perl(vars)
BuildRequires: perl(warnings)
# hope texlive-kpseas-bin missing deps was fixed
# epel7 doesn't have /usr/share/texlive/texmf-dist/web2c/texmf.cnf
BuildRequires: texlive-kpathsea
BuildRequires: tex(article.cls)

BuildRequires: perl(I18N::Langinfo)
BuildRequires: perl(Locale::gettext) >= 1.01
BuildRequires: perl(Term::ReadKey)
BuildRequires: perl(Text::WrapI18N)
BuildRequires: perl(Unicode::GCString)

# Required by the tests:
BuildRequires: perl(Test::More)
BuildRequires: perl(Test::Pod)
BuildRequires: perl(YAML::Tiny)


Requires: /usr/bin/xsltproc
Requires: gettext
Requires: opensp
# hope texlive-kpseas-bin missing deps was fixed
# epel7 doesn't have /usr/share/texlive/texmf-dist/web2c/texmf.cnf
Requires: texlive-kpathsea

# Optional, but package is quite useless without
Requires: perl(Locale::gettext) >= 1.01
# Optional run-time:
Requires: perl(I18N::Langinfo)
Requires: perl(Term::ReadKey)
Requires: perl(Text::WrapI18N)
Requires: perl(Unicode::GCString)

%description
The po4a (po for anything) project goal is to ease translations (and
more interestingly, the maintenance of translations) using gettext
tools on areas where they were not expected like documentation.

%prep
%autosetup -p1
chmod +x scripts/*

%build
export PO4AFLAGS="-v -v -v"
%{__perl} ./Build.PL installdirs=vendor
./Build

%install
./Build install destdir=$RPM_BUILD_ROOT create_packlist=0
find $RPM_BUILD_ROOT -type d -depth -exec rmdir {} 2>/dev/null ';'

%{_fixperms} $RPM_BUILD_ROOT/*
%find_lang %{name}

%check
./Build test || :


%files -f %{name}.lang
%doc README* TODO
%license COPYING
%{_bindir}/po4a*
%{_bindir}/msguntypot
%{perl_vendorlib}/Locale
%{_mandir}/man1/po4a*.1*
%{_mandir}/man1/msguntypot.1*
%{_mandir}/man3/Locale::Po4a::*.3*
#{_mandir}/man5/po4a-build.conf*.5*
#{_mandir}/man7/po4a-runtime.7*
%{_mandir}/man7/po4a.7*
%{_mandir}/*/man1/po4a*.1*
%{_mandir}/*/man1/msguntypot.1*
%{_mandir}/*/man3/Locale::Po4a::*.3*
#{_mandir}/*/man5/po4a-build.conf.5*
#{_mandir}/*/man7/po4a-runtime.7*
%{_mandir}/*/man7/po4a.7*

%changelog
* Sun Feb 23 2026 Vinicius Ferrao <vinicius.ferrao@gmail.com> - 0.74-1
- Rebuild for EL8, EL9, and EL10 from Fedora Rawhide
- Remove Syntax::Keyword::Try dependency (replace with eval for EL compat)
- Remove texlive-kpathsea-bin (not available on EL)
- Fix PerlIO encoding buffer boundary bug for Perl 5.32 (EL9)

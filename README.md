# COPR Packages for RHEL/EL

RPM packaging and build infrastructure for software not available in RHEL or
EPEL, published via [Fedora COPR](https://copr.fedorainfracloud.org/coprs/viniciusferrao/).

## Packages

| Package | Version | Targets | COPR |
|---------|---------|---------|------|
| [CDE](cde/) | 2.5.3 | EL8, EL9, EL10 (ppc64le + x86_64) | [viniciusferrao/cde](https://copr.fedorainfracloud.org/coprs/viniciusferrao/cde/) |
| [DHCP](dhcp/) | 4.4.3-P1 | EL10 (ppc64le + x86_64) | [viniciusferrao/dhcp](https://copr.fedorainfracloud.org/coprs/viniciusferrao/dhcp/) |
| [po4a](po4a/) | 0.74 | EL9, EL10 (ppc64le + x86_64) | [viniciusferrao/po4a](https://copr.fedorainfracloud.org/coprs/viniciusferrao/po4a/) |
| [qemu-user-static](qemu-user-static/) | 10.2.0 | EL9, EL10 (ppc64le + x86_64) | [viniciusferrao/qemu-user-static](https://copr.fedorainfracloud.org/coprs/viniciusferrao/qemu-user-static/) |

## Build Environment

### Prerequisites

- A RHEL/EL or Fedora build machine with ppc64le or x86_64 architecture
- User must be a member of the `mock` group
- **Tools:** mock, copr-cli, fedpkg, rpmbuild, rpmdevtools

```bash
sudo dnf install mock copr-cli fedpkg rpm-build rpmdevtools
sudo usermod -aG mock $USER
```

### COPR API token

`copr-cli` requires an API token stored at `~/.config/copr`. Obtain one from
https://copr.fedorainfracloud.org/api/ and create the file with:

```ini
[copr-cli]
login = <your_login>
username = <your_copr_username>
token = <your_api_token>
copr_url = https://copr.fedorainfracloud.org
```

### Mock configs for local ppc64le builds

| Target | Mock config |
|--------|-------------|
| EL10 ppc64le | `alma+epel-10-ppc64le` |
| EL9 ppc64le | `alma+epel-9-ppc64le` |
| EL8 ppc64le | `alma+epel-8-ppc64le` |

x86_64 builds are done via COPR (cross-builds not supported in mock on ppc64le).

### COPR chroot configuration

COPR builds against CentOS Stream (not AlmaLinux), so be aware of:

- **epel-10 chroots:** CentOS Stream 10 CRB is included by default. **Do not**
  add an AlmaLinux 10 CRB extra repo — it causes version conflicts.
- **epel-9 chroots:** CRB is **not** included by default. Packages needing CRB
  (like static libraries) require adding an AlmaLinux 9 CRB repo via
  `additional_repos` in the chroot config. This shows a "modified" label on
  COPR — that is expected and unavoidable.

### COPR CLI basics

```bash
# Create a project
copr-cli create PROJECT_NAME --chroot epel-10-ppc64le --chroot epel-10-x86_64 \
    --description "..." --instructions "..."

# Submit a build
copr-cli build PROJECT_NAME /path/to/package.src.rpm

# Submit to specific chroots only
copr-cli build PROJECT_NAME /path/to/package.src.rpm \
    --chroot epel-10-ppc64le --chroot epel-10-x86_64

# Watch a build
copr-cli watch-build BUILD_ID

# Manage chroot settings (e.g., add extra repos)
python3 -c "
import copr.v3
client = copr.v3.Client.create_from_config_file()
client.project_chroot_proxy.edit('viniciusferrao', 'PROJECT', 'epel-9-ppc64le',
    additional_repos=['https://repo.almalinux.org/almalinux/9/CRB/ppc64le/os/'])"

# List builds
python3 -c "
import copr.v3
client = copr.v3.Client.create_from_config_file()
for b in client.build_proxy.get_list('viniciusferrao', 'PROJECT'):
    print(f'Build {b.id}: {b.state} - {b.source_package.get(\"version\", \"?\")}')"

# Delete a build
python3 -c "
import copr.v3
client = copr.v3.Client.create_from_config_file()
client.build_proxy.delete(BUILD_ID)"
```

## Directory layout on the build server

```
~/rpmbuild/                     # CDE packaging (standard rpmbuild tree)
├── SPECS/cde.spec
├── SOURCES/                    # tarball, patch, config files
└── SRPMS/

~/cde-build/                    # CDE build results
├── results/{el10,el9,el8}-ppc64le/
└── copr-logs/

~/dhcp-build/                   # DHCP packaging
└── rpms-dhcp/                  # git clone of VersatusHPC/rpms-dhcp
    ├── dhcp.spec
    ├── *.patch                 # Fedora/CentOS patches
    └── build/SRPMS/

~/po4a-build/                   # po4a packaging
├── po4a/                       # fedpkg dist-git clone (rawhide)
│   ├── po4a.spec               # patched spec
│   ├── po4a-0.74.tar.gz        # source tarball
│   ├── po4a-0.74-no-syntax-keyword-try.patch
│   └── po4a-0.74-fix-perlio-encoding.patch
└── copr-packages/              # GitHub docs repo clone

~/qemu-build/                   # qemu-user-static packaging
├── qemu/                       # fedpkg dist-git clone
│   ├── qemu.spec               # patched spec
│   └── qemu-10.2.0.tar.xz     # source tarball
├── results/el10-ppc64le/
└── UPDATE-RUNBOOK.md
```

# ISC DHCP for EL10

RPM packaging for ISC DHCP 4.4.3-P1 on RHEL/EL 10.

**COPR:** https://copr.fedorainfracloud.org/coprs/viniciusferrao/dhcp/

## Install

```bash
sudo dnf copr enable viniciusferrao/dhcp
sudo dnf install dhcp-server
```

Or for the client only:

```bash
sudo dnf install dhcp-client
```

## About

The ISC DHCP package was removed from RHEL 10 in favor of Kea. However, many
environments still require the classic ISC dhcpd server. This package builds
the last maintained version (4.4.3-P1) for EL10.

ISC announced the end of maintenance for ISC DHCP as of the end of 2022. This
package is provided as-is by VersatusHPC.

## Subpackages

- **dhcp-server** — ISC DHCP server (dhcpd)
- **dhcp-client** — ISC DHCP client (dhclient)
- **dhcp-relay** — ISC DHCP relay agent (dhcrelay)
- **dhcp-common** — Common files for DHCP
- **dhcp-libs** — Shared libraries

## Source

The spec file, patches, and build instructions are maintained in a separate
repository: https://github.com/VersatusHPC/rpms-dhcp

## Targets

| EL version | ppc64le | x86_64 | Notes |
|------------|---------|--------|-------|
| EL10 | Yes | Yes | Package removed from RHEL 10 |
| EL9 | N/A | N/A | Available in base repos |
| EL8 | N/A | N/A | Available in base repos |

## Update procedure

```bash
cd ~/dhcp-build/rpms-dhcp
git pull
rpmdev-spectool --get-files --sources ./dhcp.spec
mock -r alma+epel-10-ppc64le --buildsrpm --spec ./dhcp.spec --sources . --resultdir ./build/SRPMS
copr-cli build dhcp ./build/SRPMS/*.src.rpm
```

# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel

%global _scl_prefix %{ns_dir}
%global scl_name_base    %{ns_name}-php
%global scl_macro_base   %{ns_name}_php
%global scl_name_version 82
%global scl              %{scl_name_base}%{scl_name_version}
%scl_package %scl

Summary:       Package that installs PHP 8.2
Name:          %scl_name
Version:       8.2.23
Vendor:        cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define        release_prefix 1
Release:       %{release_prefix}%{?dist}.cpanel
Group:         Development/Languages
License:       GPLv2+

Source0:       macros-build
Source1:       README.md
Source2:       LICENSE
Source3:       whm_feature_addon

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: scl-utils-build
BuildRequires: help2man
# Temporary work-around
BuildRequires: iso-codes

Requires:      %{?scl_prefix}php-common
Requires:      %{?scl_prefix}php-cli

# Our code requires that pear be installed when the meta package is installed
Requires:      %{?scl_prefix}pear

%description
This is the main package for %scl Software Collection,
that install PHP 8.2 language.


%package runtime
Summary:   Package that handles %scl Software Collection.
Group:     Development/Languages
Requires:  scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary:   Package shipping basic build configuration
Group:     Development/Languages
Requires:  scl-utils-build

%description build
Package shipping essential configuration macros
to build %scl Software Collection.


%package scldevel
Summary:   Package shipping development files for %scl
Group:     Development/Languages

Provides:  ea-php-scldevel = %{version}
Conflicts: ea-php-scldevel > %{version}, ea-php-scldevel < %{version}

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.


%prep
%setup -c -T

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# generate rpm macros file for depended collections
cat << EOF | tee scldev
%%scl_%{scl_macro_base}         %{scl}
%%scl_prefix_%{scl_macro_base}  %{scl_prefix}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable
install -D -m 644 scldev %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
install -D -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7
mkdir -p %{buildroot}/opt/cpanel/ea-php82/root/etc
mkdir -p %{buildroot}/opt/cpanel/ea-php82/root/usr/share/doc
mkdir -p %{buildroot}/opt/cpanel/ea-php82/root/usr/include
mkdir -p %{buildroot}/opt/cpanel/ea-php82/root/usr/share/man/man1
mkdir -p %{buildroot}/opt/cpanel/ea-php82/root/usr/bin
mkdir -p %{buildroot}/opt/cpanel/ea-php82/root/usr/var/cache
mkdir -p %{buildroot}/opt/cpanel/ea-php82/root/usr/var/tmp
mkdir -p %{buildroot}/opt/cpanel/ea-php82/root/usr/%{_lib}
mkdir -p %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures
install %{SOURCE3} %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures/%{name}

# Even if this package doesn't use it we need to do this because if another
# package does (e.g. pear licenses) it will be created and unowned by any RPM
%if 0%{?_licensedir:1}
mkdir %{buildroot}/%{_licensedir}
%endif

%scl_install

tmp_version=$(echo %{scl_name_version} | sed -re 's/([0-9])([0-9])/\1\.\2/')
sed -e 's/@SCL@/%{scl_macro_base}%{scl_name_version}/g' -e "s/@VERSION@/${tmp_version}/g" %{SOURCE0} \
  | tee -a %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Remove empty share/[man|locale]/ directories
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/man/ -type d -empty -delete
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale/ -type d -empty -delete
mkdir -p %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files


%files runtime
%defattr(-,root,root)
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*
%dir /opt/cpanel/ea-php82/root/etc
%dir /opt/cpanel/ea-php82/root/usr
%dir /opt/cpanel/ea-php82/root/usr/share
%dir /opt/cpanel/ea-php82/root/usr/share/doc
%dir /opt/cpanel/ea-php82/root/usr/include
%dir /opt/cpanel/ea-php82/root/usr/share/man
%dir /opt/cpanel/ea-php82/root/usr/bin
%dir /opt/cpanel/ea-php82/root/usr/var
%dir /opt/cpanel/ea-php82/root/usr/var/cache
%dir /opt/cpanel/ea-php82/root/usr/var/tmp
%dir /opt/cpanel/ea-php82/root/usr/%{_lib}
%attr(644, root, root) /usr/local/cpanel/whostmgr/addonfeatures/%{name}
%if 0%{?_licensedir:1}
%dir %{_licensedir}
%endif

%files build
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl}-config


%files scldevel
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Fri Sep 20 2024 Cory McIntire <cory@cpanel.net> - 8.2.23-1
- EA-12399: Update ea-php82 from v8.2.22 to v8.2.23

* Thu Aug 01 2024 Cory McIntire <cory@cpanel.net> - 8.2.22-1
- EA-12308: Update ea-php82 from v8.2.21 to v8.2.22

* Tue Jul 09 2024 Cory McIntire <cory@cpanel.net> - 8.2.21-1
- EA-12275: Update ea-php82 from v8.2.20 to v8.2.21

* Thu Jun 06 2024 Cory McIntire <cory@cpanel.net> - 8.2.20-1
- EA-12194: Update ea-php82 from v8.2.19 to v8.2.20

* Thu May 09 2024 Cory McIntire <cory@cpanel.net> - 8.2.19-1
- EA-12141: Update ea-php82 from v8.2.18 to v8.2.19

* Thu Apr 11 2024 Cory McIntire <cory@cpanel.net> - 8.2.18-1
- EA-12085: Update ea-php82 from v8.2.17 to v8.2.18

* Thu Mar 14 2024 Cory McIntire <cory@cpanel.net> - 8.2.17-1
- EA-12016: Update ea-php82 from v8.2.16 to v8.2.17

* Thu Feb 15 2024 Cory McIntire <cory@cpanel.net> - 8.2.16-1
- EA-11977: Update ea-php82 from v8.2.15 to v8.2.16

* Thu Jan 18 2024 Cory McIntire <cory@cpanel.net> - 8.2.15-1
- EA-11919: Update ea-php82 from v8.2.14 to v8.2.15

* Wed Jan 03 2024 Travis Holloway <t.holloway@cpanel.net> - 8.2.14-1
- EA-11893: Update ea-php82 from v8.2.13 to v8.2.14

* Tue Nov 28 2023 Julian Brown <julian.brown@cpanel.net> - 8.2.13-2
- ZC-11419: Correct Ubuntu build issues

* Thu Nov 23 2023 Cory McIntire <cory@cpanel.net> - 8.2.13-1
- EA-11823: Update ea-php82 from v8.2.12 to v8.2.13

* Thu Oct 26 2023 Cory McIntire <cory@cpanel.net> - 8.2.12-1
- EA-11774: Update ea-php82 from v8.2.11 to v8.2.12

* Mon Oct 02 2023 Cory McIntire <cory@cpanel.net> - 8.2.11-1
- EA-11717: Update ea-php82 from v8.2.10 to v8.2.11

* Thu Aug 31 2023 Cory McIntire <cory@cpanel.net> - 8.2.10-1
- EA-11658: Update ea-php82 from v8.2.9 to v8.2.10

* Wed Aug 16 2023 Cory McIntire <cory@cpanel.net> - 8.2.9-1
- EA-11619: Update ea-php82 from v8.2.8 to v8.2.9

* Fri Jul 07 2023 Cory McIntire <cory@cpanel.net> - 8.2.8-1
- EA-11539: Update ea-php82 from v8.2.7 to v8.2.8

* Thu Jun 08 2023 Cory McIntire <cory@cpanel.net> - 8.2.7-1
- EA-11478: Update ea-php82 from v8.2.6 to v8.2.7

* Mon May 16 2023 Brian Mendoza <brian.mendoza@cpanel.net> - 8.2.6-2
- ZC-10936: Clean up Makefile and remove debug-package-nil

* Thu May 11 2023 Cory McIntire <cory@cpanel.net> - 8.2.6-1
- EA-11413: Update ea-php82 from v8.2.5 to v8.2.6

* Thu Apr 13 2023 Cory McIntire <cory@cpanel.net> - 8.2.5-1
- EA-11355: Update ea-php82 from v8.2.4 to v8.2.5

* Thu Mar 16 2023 Cory McIntire <cory@cpanel.net> - 8.2.4-1
- EA-11301: Update ea-php82 from v8.2.3 to v8.2.4

* Tue Feb 14 2023 Cory McIntire <cory@cpanel.net> - 8.2.3-1
- EA-11226: Update ea-php82 from v8.2.2 to v8.2.3

* Thu Feb 02 2023 Cory McIntire <cory@cpanel.net> - 8.2.2-1
- EA-11200: Update ea-php82 from v8.2.1 to v8.2.2

* Mon Jan 09 2023 Brian Mendoza <brian.mendoza@cpanel.net> - 8.2.1-2
- ZC-10585: Build for C7

* Thu Jan 05 2023 Cory McIntire <cory@cpanel.net> - 8.2.1-1
- EA-11136: Update ea-php82 from v8.2.0 to v8.2.1

* Fri Oct 07 2022 Brian Mendoza <brian.mendoza@cpanel.net> - 8.2.0-1
- ZC-10359: Initial Build

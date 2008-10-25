#
# Available build options:
%bcond_with	checkpath	# enable check if php execution is within DOCUMENT_ROOT of the vhost
#
%define		mod_name	suphp
%define 	apxs		/usr/sbin/apxs
Summary:	Apache module: suPHP - execute PHP scripts with the permissions of their owners
Summary(pl.UTF-8):	Moduł do apache: suPHP - uruchamianie skryptów PHP z uprawnieniami ich właścicieli
Name:		apache-mod_%{mod_name}
Version:	0.6.3
Release:	1
License:	GPL
Group:		Networking/Daemons/HTTP
Source0:	http://www.suphp.org/download/%{mod_name}-%{version}.tar.gz
# Source0-md5:	756e8893857fefed087a89959a87645a
Source1:	%{name}.logrotate
Source2:	%{name}.conf
Source3:	%{name}-suphp.conf
Patch0:		%{name}-apr.patch
Patch1:		%{name}-compiler-flags.patch
Patch2:		%{name}-apache_version.patch
URL:		http://www.suphp.org/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.0.52-2
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libstdc++-devel
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	apache(modules-api) = %apache_modules_api
Requires:	php-cgi
Conflicts:	logrotate < 3.7-4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		apacheconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)/conf.d
%define		apachelibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)

%description
suPHP is a tool for executing PHP scripts with the permissions of
their owners. It consists of an Apache module (mod_suphp) and a setuid
root binary (suphp) that is called by the Apache module to change the
uid of the process executing the PHP interpreter.

%description -l pl.UTF-8
suPHP jest narzędziem pozwalającym na wykonywanie skryptów w PHP z
uprawnieniami ich właścicieli. Składa się z modułu (mod_suphp) oraz
programu (suphp) z ustawionym bitem suid, który uruchamiany jest przez
moduł w celu zmiany uid procesu uruchamiającego interpreter PHP.

%prep
%setup -q -n %{mod_name}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
APACHE_VERSION=$(rpm -q --qf '%{V}' apache-devel); export APACHE_VERSION
%configure \
	--%{?with_checkpath:en}%{!?with_checkpath:dis}able-checkpath \
	--with-apache-user=http \
	--with-min-uid=500 \
	--with-min-gid=1000 \
	--with-apxs=%{apxs} \
	--disable-checkuid \
	--disable-checkgid \
	--with-setid-mode=owner \
	--with-logfile=/var/log/httpd/suphp_log

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{apachelibdir},%{_datadir}/suphp}
install -d $RPM_BUILD_ROOT%{apacheconfdir}

install src/suphp $RPM_BUILD_ROOT%{_sbindir}
install src/apache2/.libs/mod_%{mod_name}.so $RPM_BUILD_ROOT%{apachelibdir}
install %{SOURCE2} $RPM_BUILD_ROOT%{apacheconfdir}/70_mod_%{mod_name}.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{mod_name}.conf

install -d $RPM_BUILD_ROOT/etc/logrotate.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/apache-mod_suphp

install doc/suphp.conf-example $RPM_BUILD_ROOT%{_datadir}/suphp

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service -q httpd restart

%postun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%doc README AUTHORS ChangeLog doc
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{apacheconfdir}/*_mod_%{mod_name}.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{mod_name}.conf
%attr(755,root,root) %{apachelibdir}/*.so
%attr(4755,root,root) %{_sbindir}/suphp
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/*
%dir %{_datadir}/suphp
%{_datadir}/suphp/*

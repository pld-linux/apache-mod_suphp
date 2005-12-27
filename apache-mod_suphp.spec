#
# Available build options:
%bcond_with	checkpath	# enable check if php execution is within DOCUMENT_ROOT of the vhost
#
%define		mod_name	suphp
%define 	apxs		/usr/sbin/apxs
Summary:	Apache module: suPHP - execute PHP scripts with the permissions of their owners
Summary(pl):	Modu³ do apache: suPHP - uruchamianie skryptów PHP z uprawnieniami ich w³a¶cicieli
Name:		apache-mod_%{mod_name}
Version:	0.6.0
Release:	4
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.suphp.org/download/%{mod_name}-%{version}.tar.gz
# Source0-md5:	fa89691101b9ebf18f4922b1382186c6
Source1:	%{name}.logrotate
Source2:	%{name}.conf
Patch0:		%{name}-apr.patch
Patch1:		%{name}-compiler-flags.patch
Patch2:		%{name}-apache_version.patch
URL:		http://www.suphp.org/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.0.52-2
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libstdc++-devel
Requires:	apache(modules-api) = %apache_modules_api
Requires:	php-cgi
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
suPHP is a tool for executing PHP scripts with the permissions of
their owners. It consists of an Apache module (mod_suphp) and a setuid
root binary (suphp) that is called by the Apache module to change the
uid of the process executing the PHP interpreter.

%description -l pl
suPHP jest narzêdziem pozwalaj±cym na wykonywanie skryptów w PHP z
uprawnieniami ich w³a¶cicieli. Sk³ada siê z modu³u (mod_suphp) oraz
programu (suphp) z ustawionym bitem suid, który uruchamiany jest przez
modu³ w celu zmiany uid procesu uruchamiaj±cego interpreter PHP.

%prep
%setup -q -n %{mod_name}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
chmod 755 configure
export APACHE_VERSION=$(rpm -q --qf '%%{version}' apache-apxs)
%configure \
	%{?with_checkpath: --enable-checkpath} \
	%{!?with_checkpath: --disable-checkpath} \
	--with-apache-user=http \
	--with-min-uid=500 \
	--with-min-gid=1000 \
	--with-apxs=%{apxs} \
	--disable-checkuid \
	--disable-checkgid

# FIXME: I don't know anything about libtool, but libtool created by configure
# doesn't work. My hardcoded trick is to replace libtool created by configure
# with one provided by libtool package in /usr/bin/ path.
cp %{_bindir}/libtool .

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_pkglibdir},%{_datadir}/suphp}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

install src/suphp $RPM_BUILD_ROOT%{_sbindir}
install src/apache2/.libs/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/70_mod_%{mod_name}.conf

install -d $RPM_BUILD_ROOT/etc/logrotate.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/apache-mod_suphp

install doc/suphp.conf-example $RPM_BUILD_ROOT%{_datadir}/suphp

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc README AUTHORS ChangeLog doc
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*.so
%attr(4755,root,root) %{_sbindir}/suphp
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/*
%dir %{_datadir}/suphp
%{_datadir}/suphp/*

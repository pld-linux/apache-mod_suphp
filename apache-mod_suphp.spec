#
# Available build options:
%bcond_with	checkpath	# enable check if php execution is within
				# DOCUMENT_ROOT of the vhost
#
%define		mod_name	suphp
%define 	apxs		/usr/sbin/apxs
%define 	_apache1        %(rpm -q apache-devel 2> /dev/null | grep -Eq '\\-2\\.[0-9]+\\.' && echo 0 || echo 1)
Summary:	Apache module: suPHP - execute PHP scripts with the permissions of their owners
Summary(pl):	Modu� do apache: suPHP - uruchamianie skrypt�w PHP z uprawnieniami ich w�a�cicieli
Name:		apache-mod_%{mod_name}
Version:	0.5.1
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.suphp.org/download/%{mod_name}-%{version}.tar.gz	
# Source0-md5:	6898ccd801ec93cb7c6a69a9ac8f3703
Source1:	apache-mod_suphp.logrotate
Source2:	apache-mod_suphp.conf
URL:		http://www.suphp.org/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel
BuildRequires:	autoconf
BuildRequires:	automake
Requires(post,preun):	%{apxs}
Requires:	apache
Requires:	php-cgi
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)

%description
suPHP is a tool for executing PHP scripts with the permissions of their
owners. It consists of an Apache module (mod_suphp) and a setuid root
binary (suphp) that is called by the Apache module to change the uid of
the process executing the PHP interpreter.

%description -l pl
suPHP jest narz�dziem pozwalaj�cym na wykonywanie skrypt�w PHP z
uprawnieniami ich w�a�cicieli. Sk�ada si� z modu�u (mod_suphp) oraz
programu (suphp) z ustawionym bitem suid, kt�ry uruchamiany jest przez
modu� w celu zmiany uid procesu uruchamiaj�cego interpreter PHP.

%prep
%setup -q -n %{mod_name}-%{version}

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
chmod 755 configure
%configure \
	%{?with_checkpath: --enable-checkpath} \
	%{!?with_checkpath: --disable-checkpath} \
	--with-apache-user=http \
	--with-min-uid=500 \
	--with-min-gid=1000 \
	--with-apxs=%{apxs} \
	--disable-checkuid \
	--disable-checkgid 

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_pkglibdir}}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

install src/suphp $RPM_BUILD_ROOT%{_sbindir}
%if %{_apache1}
install src/apache/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
%else
install src/apache2/.libs/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/70_mod-suphp.conf
%endif

install -d $RPM_BUILD_ROOT/etc/logrotate.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/apache-mod_suphp

%clean
rm -rf $RPM_BUILD_ROOT

%if %{_apache1}
%post
%{apxs} -e -a -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi
%endif

%files
%defattr(644,root,root,755)
%doc README AUTHORS ChangeLog doc
%attr(4755,root,root) %{_sbindir}/suphp
%attr(755,root,root) %{_pkglibdir}/*
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/*

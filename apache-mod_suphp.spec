%define		mod_name	suphp
%define 	apxs		/usr/sbin/apxs
Summary:	Apache module: suPHP - execute PHP scripts with the permissions of their owners
Summary(pl):	Modu³ do apache: suPHP - uruchamianie skryptów PHP z uprawnieniami ich w³a¶cicieli
Name:		apache-mod_%{mod_name}
Version:	0.3
Release:	0.1
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.suphp.org/download/%{mod_name}-%{version}.tar.gz	
# Source0-md5:	f80d54de6aff5db4ab76670f1c5b3c6d
URL:		http://www.suphp.org/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel <= 1.4
Requires(post,preun):	%{apxs}
Requires:	apache
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)

%description
suPHP is a tool for executing PHP scripts with the permissions of their
owners. It consists of an Apache module (mod_suphp) and a setuid root
binary (suphp) that is called by the Apache module to change the uid of
the process executing the PHP interpreter.

%description -l pl
suPHP jest narzêdziem pozwalaj±cym na wykonywanie skryptów PHP z
uprawnieniami ich w³a¶cicieli. Sk³ada siê z modu³u (mod_suphp) oraz
programu (suphp) z ustawionym bitem suid, który uruchamiany jest przez
modu³ w celu zmiany uid procesu uruchamiaj±cego interpreter PHP.

%prep
%setup -q -n %{mod_name}-%{version}

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
%configure
%{__make}

#%{apxs} -c mod_%{mod_name}.c -o mod_%{mod_name}.so -lz

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_pkglibdir}}

install src/suphp $RPM_BUILD_ROOT%{_sbindir}
install src/apache/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}

%clean
rm -rf $RPM_BUILD_ROOT

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

%files
%defattr(644,root,root,755)
%doc README AUTHORS ChangeLog doc
%attr(4755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_pkglibdir}/*

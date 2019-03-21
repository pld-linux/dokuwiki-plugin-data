%define		subver	2019-03-20
%define		ver		%(echo %{subver} | tr -d -)
%define		plugin		data
%define		php_min_version 5.6.0
%include	/usr/lib/rpm/macros.php
Summary:	DokuWiki Structured Data Plugin
Name:		dokuwiki-plugin-%{plugin}
Version:	%{ver}
Release:	1
License:	GPL v2
Group:		Applications/WWW
Source0:	https://github.com/splitbrain/dokuwiki-plugin-%{plugin}/archive/%{subver}/%{plugin}-%{subver}.tar.gz
# Source0-md5:	26a8dc7c282c88e9dc3c2b3df0d8315e
URL:		https://www.dokuwiki.org/plugin:data
Patch2:		separator-style.patch
Patch3:		separate-rpmdb.patch
Patch4:		cache-enable.patch
BuildRequires:	rpm-php-pearprov
BuildRequires:	rpmbuild(macros) >= 1.520
Requires:	php(core) >= %{php_min_version}
Requires(triggerun):	sqlite
Requires(triggerun):	sqlite3
Requires:	dokuwiki >= 20090214b-5
Requires:	dokuwiki-plugin-sqlite >= 20130508
Requires:	php(pcre)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		dokuconf	/etc/webapps/dokuwiki
%define		dokudir		/usr/share/dokuwiki
%define		metadir		/var/lib/dokuwiki/meta
%define		plugindir	%{dokudir}/lib/plugins/%{plugin}
%define		find_lang 	%{_usrlibrpm}/dokuwiki-find-lang.sh %{buildroot}

# no pear deps
%define		_noautopear	pear

# sqlite is dokuwiki-plugin-sqlite dep, not ours
%define		_noautophp	php-sqlite

# put it together for rpmbuild
%define		_noautoreq	%{?_noautophp} %{?_noautopear}

%description
This plugin allows you to add structured data to any DokuWiki page.
Think about this data as additional named attributes. Those attributes
can then be queried and aggregated. The plugin is similar to what was
done here for the repository plugin but its internals are very
different to the repository plugin.

%prep
%setup -qc
mv *-%{plugin}-*/{.??*,*} .
%patch2 -p1
%patch3 -p1
%patch4 -p1

# nothing to do with tests
rm -rf _test
rm .travis.yml

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%build
version=$(awk '/date/{print $2}' plugin.info.txt)
if [ $(echo "$version" | tr -d -) != %{version} ]; then
	: %%{version} mismatch
	exit 1
fi

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{plugindir},%{metadir}}
cp -a . $RPM_BUILD_ROOT%{plugindir}
%{__rm} $RPM_BUILD_ROOT%{plugindir}/README
# sqlite2: php-sqlite
touch $RPM_BUILD_ROOT%{metadir}/data.sqlite
# sqlite3: php-pdo-sqlite
touch $RPM_BUILD_ROOT%{metadir}/data.sqlite3

# find locales
%find_lang %{name}.lang

%clean
rm -rf $RPM_BUILD_ROOT

%post
# force css cache refresh
if [ -f %{dokuconf}/local.php ]; then
	touch %{dokuconf}/local.php
fi

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README
%dir %{plugindir}
%{plugindir}/*.css
%{plugindir}/*.js
%{plugindir}/*.php
%{plugindir}/*.svg
%{plugindir}/*.txt
%{plugindir}/admin
%{plugindir}/conf
%{plugindir}/db
%{plugindir}/helper
%{plugindir}/syntax
%attr(660,http,http) %ghost %{metadir}/data.sqlite
%attr(660,http,http) %ghost %{metadir}/data.sqlite3

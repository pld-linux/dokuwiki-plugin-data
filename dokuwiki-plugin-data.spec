%define		subver	2016-03-11
%define		ver		%(echo %{subver} | tr -d -)
%define		plugin		data
%define		php_min_version 5.3.0
%include	/usr/lib/rpm/macros.php
Summary:	DokuWiki Structured Data Plugin
Name:		dokuwiki-plugin-%{plugin}
Version:	%{ver}
Release:	0.1
License:	GPL v2
Group:		Applications/WWW
# using master snapshot, upstream doesn't tag their code
# https://github.com/splitbrain/dokuwiki-plugin-data/issues/206
Source0:	https://github.com/splitbrain/dokuwiki-plugin-%{plugin}/archive/master/%{plugin}-%{subver}.tar.gz
# Source0-md5:	eea5c5398f01db4f2b4f22c71d601aea
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
Requires:	dokuwiki-plugin-sqlite >= 20120619
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
mv *-%{plugin}-*/* .
%patch2 -p1
%patch3 -p1
%patch4 -p0

version=$(awk '/date/{print $2}' plugin.info.txt)
if [ $(echo "$version" | tr -d -) != %{version} ]; then
	: %%{version} mismatch
#	exit 1
fi

# nothing to do with tests
rm -rf _test

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

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

%triggerun -- %{name} < 20100322-0.5
# move to new location
mv /var/lib/dokuwiki/cache/dataplugin.sqlite %{metadir}/data.sqlite

# perform new indexes add manually
sqlite %{metadir}/data.sqlite <<'EOF'
CREATE TABLE opts (opt,val);
CREATE UNIQUE INDEX idx_opt ON opts(opt);
INSERT INTO opts VALUES ('dbversion', 1);
EOF
chown root:http %{metadir}/data.sqlite
chmod 660 %{metadir}/data.sqlite

%triggerun -- %{name} < 20120716-3
if [ -f %{metadir}/data.sqlite3 ]; then
	# already migrated
	exit 0
fi
# perform sqlite2 -> sqlite3 migration of both tools present
if [ ! -x /usr/bin/sqlite ] || [ ! -x /usr/bin/sqlite3 ]; then
	echo >&2 "data plugin: To migrate db from sqlite2 to sqlite3 you need to install 'sqlite' and 'sqlite3' packages"
	exit 0
fi

sqlite %{metadir}/data.sqlite .dump > %{metadir}/data.dump
sqlite3 %{metadir}/data.dump.new < %{metadir}/data.dump
mv %{metadir}/data.sqlite3{.new,}
chown root:http %{metadir}/data.sqlite3
chmod 660 %{metadir}/data.sqlite3

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README
%dir %{plugindir}
%{plugindir}/admin
%{plugindir}/syntax
%{plugindir}/conf
%{plugindir}/db
%{plugindir}/*.js
%{plugindir}/*.php
%{plugindir}/*.txt
%{plugindir}/*.css
%attr(660,http,http) %ghost %{metadir}/data.sqlite
%attr(660,http,http) %ghost %{metadir}/data.sqlite3

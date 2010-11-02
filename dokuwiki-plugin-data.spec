%define		plugin		data
%define		php_min_version 5.0.0
%include	/usr/lib/rpm/macros.php
Summary:	DokuWiki Structured Data Plugin
Name:		dokuwiki-plugin-%{plugin}
Version:	20100608
Release:	0.2
License:	GPL v2
Group:		Applications/WWW
Source0:	http://github.com/splitbrain/dokuwiki-plugin-%{plugin}/zipball/master#/%{plugin}-%{version}.zip
# Source0-md5:	f79901b38df2205eb13720b996336e9c
URL:		http://wiki.splitbrain.org/plugin:data
Patch0:		interwiki.patch
Patch1:		helper-map.patch
Patch2:		separator-style.patch
BuildRequires:	rpmbuild(macros) >= 1.520
BuildRequires:	unzip
Requires:	php-common >= 4:%{php_min_version}
Requires(triggerun):	sqlite
Requires:	dokuwiki >= 20090214b-5
Requires:	dokuwiki-plugin-sqlite
Requires:	php-pcre
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
%patch0 -p1
%patch1 -p1
%patch2 -p1

version=$(awk '/date/{print $2}' plugin.info.txt)
if [ $(echo "$version" | tr -d -) != %{version} ]; then
	: %%{version} mismatch
	exit 1
fi

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{plugindir},%{metadir}}
cp -a . $RPM_BUILD_ROOT%{plugindir}
touch $RPM_BUILD_ROOT%{metadir}/data.sqlite

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

%files -f %{name}.lang
%defattr(644,root,root,755)
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

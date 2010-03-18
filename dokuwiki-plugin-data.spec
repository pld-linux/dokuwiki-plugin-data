%define		plugin		data
Summary:	DokuWiki Structured Data Plugin
Name:		dokuwiki-plugin-%{plugin}
Version:	20100125
Release:	1
License:	GPL v2
Group:		Applications/WWW
Source0:	http://download.github.com/splitbrain-dokuwiki-plugin-data-1e1e56a.zip
# Source0-md5:	2f1fbc2c8c88e846d5fd52c8500c0294
URL:		http://wiki.splitbrain.org/plugin:data
Patch0:		interwiki.patch
Patch1:		helper-map.patch
Patch2:		separator-style.patch
BuildRequires:	rpmbuild(macros) >= 1.520
Requires:	dokuwiki >= 20090214b-5
Requires:	php(sqlite)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		dokuconf	/etc/webapps/dokuwiki
%define		dokudir		/usr/share/dokuwiki
%define		cachedir	/var/lib/dokuwiki/cache
%define		plugindir	%{dokudir}/lib/plugins/%{plugin}
%define		find_lang 	%{_usrlibrpm}/dokuwiki-find-lang.sh %{buildroot}

%description
This plugin allows you to add structured data to any DokuWiki page.
Think about this data as additional named attributes. Those attributes
can then be queried and aggregated. The plugin is similar to what was
done here for the repository plugin but its internals are very
different to the repository plugin.

%prep
%setup -qc -n %{plugin}
mv splitbrain-dokuwiki-plugin-data-*/* .
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
install -d $RPM_BUILD_ROOT{%{plugindir},%{cachedir}}
cp -a . $RPM_BUILD_ROOT%{plugindir}

touch $RPM_BUILD_ROOT%{cachedir}/dataplugin.sqlite

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
%dir %{plugindir}
%{plugindir}/syntax
%{plugindir}/*.php
%{plugindir}/*.txt
%{plugindir}/*.css
%{plugindir}/*.sql
%attr(660,http,http) %ghost %{cachedir}/dataplugin.sqlite

%define		plugin		data
Summary:	DokuWiki Structured Data Plugin
Name:		dokuwiki-plugin-%{plugin}
Version:	20090213
Release:	2
License:	GPL v2
Group:		Applications/WWW
Source0:	http://dev.splitbrain.org/download/snapshots/data-plugin-latest.tgz
# Source0-md5:	6a3ee212496a60a343b62246e8002957
URL:		http://wiki.splitbrain.org/plugin:data
Patch0:		interwiki.patch
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
%setup -q -n %{plugin}
%patch0 -p1

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
%{plugindir}/*.css
%{plugindir}/*.sql
%ghost %attr(660,http,http) %{cachedir}/dataplugin.sqlite

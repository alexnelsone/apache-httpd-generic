%define _arch noarch
%define _httpd_conf_dir /etc/httpd/conf.d/
%define _http_data_dir /data/www
%define _requires httpd
%define _summary INSERT YOUR SUMMARY HERE
%define _description INSERT DESCRIPTION HERE

######################################################################


Name: SITENAME
Summary: %{_summary}
Version: 1.0.0
Vendor: VENDOR
License: LICENSE
Release: %(date +%Y%m%d)_BUILDNUMBER
Packager: PACKAGER
Group: Applications/Internet
URL: URL
Source: %{name}-%{version}.tar.gz
Buildroot: %{_tmppath}/%{name}-root
Requires: %{_requires}
BuildArchitectures: %{_arch}


%description
%{_description}.


%prep
rm -rf ${RPM_BUILD_ROOT}
mkdir ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_httpd_conf_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_http_data_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_http_data_dir}/%{name}
mkdir -p ${RPM_BUILD_ROOT}%{_http_data_dir}/%{name}/htdocs
mkdir -p ${RPM_BUILD_ROOT}%{_http_data_dir}/%{name}/wsgi
mkdir -p ${RPM_BUILD_ROOT}%{_http_data_dir}/%{name}/conf.d

mkdir -p ${RPM_BUILD_ROOT}/tmp


%setup -q -n %{name}-%{version}

%build

%install
if [ -e $RPM_BUILD_ROOT ];
then
       
        mv %{name}.conf ${RPM_BUILD_ROOT}%{_httpd_conf_dir}/%{name}.conf
        mv isalive.html ${RPM_BUILD_ROOT}%{_http_data_dir}/%{name}/htdocs/isalive.html
fi

%post
printf "\n\n"
printf "Checking this server's region.\n"
server_env=`cat /etc/servertype`
server_loc=`hostname | cut -c1-3`
printf "server found to be operating in ${server_env} region in ${server_loc}.\n\n"

if [[ ${server_env} == "DV" ]]; then
        site_prefix="dev"
elif [[ ${server_env} == "CT" ]]; then
    site_prefix="test"
else
    #convert the prefix to lowercase
        site_prefix=${server_env,,}
fi


printf "setting server alias to be ${site_prefix}.%{name}\n"

sed -i "s/ServerName %{name}/ServerName ${site_prefix}.%{name}/g" %{_httpd_conf_dir}/%{name}.conf
printf "\n\n"
printf "Checking %{_httpd_conf_dir}/%{name}.conf:\n"
grep ServerName %{_httpd_conf_dir}/%{name}.conf

grepSuccess=$?

printf "\n\n"
if [[ grepSuccess -ne 0 ]]; then
        printf "Failure setting server name.  Please manually verify %{_httpd_conf_dir}/%{name}.conf.\n\n"
else
        printf "Vhost ServerName set successfully.\n\n"
fi

nslookup ${site_prefix}.%{name} > /dev/null
nslookupSuccess=$?

printf "\n\n"
if [[ nslookupSuccess -ne 0 ]]; then
        printf "###############################################################\n"
        printf "###############################################################\n\n"
        printf "Failure resolving DNS for ${site_prefix}.%{name}.\n"
        printf "Make sure that you have put in a DNS request for this site.\n\n"
        printf "###############################################################\n"
        printf "###############################################################\n\n"
       
else
        printf "DNS query for ${site_prefix}.%{name} was successful.\n\n"
fi


printf "Attempting to reload apache configuration.\n\n"
/sbin/service httpd reload > /dev/null

reloadSuccess=$?

printf "\n\n"
if [[ reloadSuccess -ne 0 ]];then
        printf "###############################################################\n"
        printf "###############################################################\n\n"
        printf "httpd reload failed. Please review log files.\n\n"
        printf "###############################################################\n"
        printf "###############################################################\n\n"
       
else
        printf "httpd reload successful.\n\n"
fi


%postun

# Need to get server env.
printf "\n\n"
printf "Checking this server's region.\n"
server_env=`cat /etc/servertype`
server_loc=`hostname | cut -c1-3`
printf "server found to be operating in ${server_env} region in ${server_loc}.\n\n"

# final clean up.  Have to remove these this way because they are modified during install.
printf "\n\nPerforming final cleanup.\n"


%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT


%files
# set perms and ownerships of packaged files
# the - indicates that the current permissions on the files should be used
# since these attributes can't start with % they need to be paths
# TODO: try using shell vars at the top.
%defattr(-,apache,apache)
/etc/httpd/conf.d/%{name}.conf
%dir /data/www/SITENAME/
%dir /data/www/SITENAME/htdocs
%dir /data/www/SITENAME/conf.d
%dir /data/www/SITENAME/wsgi
/data/www/SITENAME/htdocs/isalive.html






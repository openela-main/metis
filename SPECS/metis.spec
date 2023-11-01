%if 0%{?fedora} <= 22
%global _hardened_build 1
%endif

%if 0%{?rhel} < 7
%{!?__global_ldflags: %global __global_ldflags -Wl,-z,relro}
%endif

%if %{?__isa_bits:%{__isa_bits}}%{!?__isa_bits:32} == 64
%global arch64 1
%else
%global arch64 0
%endif

Name:    metis
Version: 5.1.0
Release: 17%{?dist}
Summary: Serial Graph Partitioning and Fill-reducing Matrix Ordering
License: ASL 2.0 and BSD and LGPLv2+
Group:   Development/Libraries
URL:     http://glaros.dtc.umn.edu/gkhome/views/%{name}
Source0: http://glaros.dtc.umn.edu/gkhome/fetch/sw/%{name}/%{name}-%{version}.tar.gz

## This patch sets up libmetis soname of libmetis
Patch0:  %{name}-libmetis.patch

## This patch sets up shared GKlib library 
Patch1:  %{name}-shared-GKlib.patch

## Specify the width (32 or 64 bits) of the elementary data type 
## used in METIS. This is controled by the IDXTYPEWIDTH
## constant.
## For now, on a 32 bit architecture you can only specify a width of 32, 
## whereas for a 64 bit architecture you can specify a width of either 
## 32 or 64 bits.
Patch2:  %{name}-width-datatype.patch

## This patch sets up GKREGEX, GKRAND, libsuffix options to the Makefiles 
Patch3:  %{name}-GKREGEX-GKRAND-LIBSUFFIX-fix.patch

## Rename library of 64 integer version
Patch4: %{name}_lib64.patch

BuildRequires: cmake
BuildRequires: pcre-devel
BuildRequires: help2man
BuildRequires: chrpath

%description
METIS is a set of serial programs for partitioning graphs, 
partitioning finite element meshes, and producing fill reducing 
orderings for sparse matrices. 
The algorithms implemented in METIS are based on the multilevel 
recursive-bisection, multilevel k-way, and multi-constraint 
partitioning schemes developed in our lab.
METIS is distributed with OpenMP support.

%package devel
Summary: The OpenMP Metis headers and development-related files
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
%description devel
Header and library files of Metis, OpenMP version.

%if 0%{?arch64}
%package -n metis64
Summary: Serial Graph Partitioning and Fill-reducing Matrix Ordering (64bit INTEGER)
Group: System Environment/Libraries

%description -n metis64
METIS is a set of serial programs for partitioning graphs, 
partitioning finite element meshes, and producing fill reducing 
orderings for sparse matrices. 
The algorithms implemented in METIS are based on the multilevel 
recursive-bisection, multilevel k-way, and multi-constraint 
partitioning schemes developed in our lab.
METIS is distributed with OpenMP support.
This build has 64bit INTEGER support.

%package -n metis64-devel
Summary: LAPACK development libraries (64bit INTEGER)
Group: Development/Libraries
Requires: metis64%{?_isa} = %{version}-%{release}

%description -n metis64-devel
Header and library files of Metis,
OpenMP version (64bit INTEGER).
%endif

%prep
%setup -qc 

pushd %{name}-%{version}
%patch0 -p0
%patch1 -p0
%patch3 -p0

## Remove default compiler flag
sed -e 's|-O3||g' -i GKlib/GKlibSystem.cmake
popd

%if 0%{?arch64}
cp -a %{name}-%{version} metis64
%endif

%build
pushd %{name}-%{version}/build
export CC=gcc
%cmake \
 -DGKLIB_PATH=../GKlib  \
 -DSHARED:BOOL=TRUE \
 -DOPENMP:BOOL=ON \
 -DPCRE:BOOL=ON \
 -DCMAKE_C_FLAGS:STRING="%{optflags} -Wl,-z,relro -fPIC -pie -Wl,-z,now -pthread" \
 -DCMAKE_SHARED_LINKER_FLAGS_RELEASE:STRING="%{__global_ldflags} -fPIC -pie -Wl,-z,now" \
 -DCMAKE_EXE_LINKER_FLAGS_RELEASE:STRING="%{__global_ldflags} -fPIC -pie -Wl,-z,now" \
 -DCMAKE_VERBOSE_MAKEFILE:BOOL=TRUE \
 -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} ..
make %{?_smp_mflags}
popd

%if 0%{?arch64}
cd metis64
patch -p0 < %{PATCH2}
patch -p0 < %{PATCH4}
mkdir -p build64
pushd build64
export CC=gcc
%cmake \
 -DGKLIB_PATH=../GKlib  \
 -DSHARED:BOOL=TRUE \
 -DOPENMP:BOOL=ON \
 -DPCRE:BOOL=ON \
 -DCMAKE_C_FLAGS:STRING="%{optflags} -Wl,-z,relro -fPIC -pie -Wl,-z,now -pthread" \
 -DCMAKE_SHARED_LINKER_FLAGS_RELEASE:STRING="%{__global_ldflags} -fPIC -pie -Wl,-z,now" \
 -DCMAKE_EXE_LINKER_FLAGS_RELEASE:STRING="%{__global_ldflags} -fPIC -pie -Wl,-z,now" \
 -DCMAKE_VERBOSE_MAKEFILE:BOOL=TRUE \
 -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} ..
make %{?_smp_mflags}
popd
cd ../
%endif

%install
pushd %{name}-%{version}/build
%make_install

## Generate manpages from binaries
%if 0%{?el6}
LD_PRELOAD=%{buildroot}%{_libdir}/lib%{name}.so.0 \
help2man --version-option="%{version}" -n "Partitions a graph into a specified number of parts." \
 -N --output="gpmetis.1" -h -help %{buildroot}%{_bindir}/gpmetis

## Can't get manpage from ndmetis. Use 'ndmetis -h' command 
LD_PRELOAD=%{buildroot}%{_libdir}/lib%{name}.so.0 \
help2man --version-option="%{version}" -n "Partitions a mesh into a specified number of parts." \
 -N --output="mpmetis.1" -h -help %{buildroot}%{_bindir}/mpmetis

LD_PRELOAD=%{buildroot}%{_libdir}/lib%{name}.so.0 \
help2man --version-option="%{version}" -n "Converts a mesh into a graph that is compatible with METIS." \
 -N --output="m2gmetis.1" -h -help %{buildroot}%{_bindir}/m2gmetis

%else
LD_PRELOAD=%{buildroot}%{_libdir}/lib%{name}.so.0 \
help2man --version-string="%{version}" -n "Partitions a graph into a specified number of parts." \
 -N --output="gpmetis.1" --no-discard-stderr --help-option="-help" %{buildroot}%{_bindir}/gpmetis

LD_PRELOAD=%{buildroot}%{_libdir}/lib%{name}.so.0 \
help2man --version-string="%{version}" \
 -n "Computes a fill-reducing ordering of the vertices of the graph using multilevel nested dissection." \
 -N --output="ndmetis.1" --no-discard-stderr --help-option="-help" %{buildroot}%{_bindir}/ndmetis

LD_PRELOAD=%{buildroot}%{_libdir}/lib%{name}.so.0 \
help2man --version-string="%{version}" -n "Partitions a mesh into a specified number of parts." \
 -N --output="mpmetis.1" --no-discard-stderr --help-option="-help" %{buildroot}%{_bindir}/mpmetis

LD_PRELOAD=%{buildroot}%{_libdir}/lib%{name}.so.0 \
help2man --version-string="%{version}" -n "Converts a mesh into a graph that is compatible with METIS." \
 -N --output="m2gmetis.1" --no-discard-stderr -h "-help" %{buildroot}%{_bindir}/m2gmetis
%endif

mkdir -p %{buildroot}%{_mandir}/man1
mv *.1 %{buildroot}%{_mandir}/man1
popd

# Save metis.h with IDXTYPEWIDTH = 32
mv %{buildroot}%{_includedir}/metis.h %{buildroot}%{_includedir}/metis32.h

%if 0%{?arch64}
pushd metis64/build64
%make_install
# Save metis.h with IDXTYPEWIDTH = 64
mv %{buildroot}%{_includedir}/metis.h %{buildroot}%{_includedir}/metis64.h
popd
%endif

# Save metis.h with IDXTYPEWIDTH = 32
mv %{buildroot}%{_includedir}/metis32.h %{buildroot}%{_includedir}/metis.h

## Remove rpaths
chrpath -d %{buildroot}%{_bindir}/*

%check
cp -p %{buildroot}%{_bindir}/* %{name}-%{version}/graphs
pushd %{name}-%{version}/graphs
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./ndmetis mdual.graph
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./mpmetis metis.mesh 2
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./gpmetis test.mgraph 4
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./gpmetis copter2.graph 4
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./graphchk 4elt.graph
%if 0%{?arch64}
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./ndmetis64 mdual.graph
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./mpmetis64 metis.mesh 2
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./gpmetis64 test.mgraph 4
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./gpmetis64 copter2.graph 4
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH ./graphchk64 4elt.graph
%endif
popd

%ldconfig_scriptlets

%if 0%{?arch64}
%ldconfig_scriptlets -n metis64
%endif

%files
%{!?_licensedir:%global license %doc}
%doc %{name}-%{version}/Changelog %{name}-%{version}/manual/manual.pdf
%license %{name}-%{version}/LICENSE.txt
%{_bindir}/cmpfillin
%{_bindir}/gpmetis
%{_bindir}/graphchk
%{_bindir}/m2gmetis
%{_bindir}/mpmetis
%{_bindir}/ndmetis
%{_mandir}/man1/*.1.gz
%{_libdir}/lib%{name}.so.*

%files devel
%{_includedir}/%{name}.h
%{_libdir}/lib%{name}.so

%if 0%{?arch64}
%files -n metis64
%{!?_licensedir:%global license %doc}
%doc metis64/Changelog metis64/manual/manual.pdf
%license metis64/LICENSE.txt
%{_bindir}/cmpfillin64
%{_bindir}/gpmetis64
%{_bindir}/graphchk64
%{_bindir}/m2gmetis64
%{_bindir}/mpmetis64
%{_bindir}/ndmetis64
%{_libdir}/lib%{name}64.so.*

%files -n metis64-devel
%{_includedir}/%{name}64.h
%{_libdir}/lib%{name}64.so
%endif

%changelog
* Sat Feb 17 2018 Antonio Trande <sagitter@fedoraproject.org> - 5.1.0-17
- Use %%ldconfig_scriptlets

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 5.1.0-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.1.0-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.1.0-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.1.0-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Feb 15 2016 Antonio Trande <sagitter@fedoraproject.org> - 5.1.0-12
- Build 64 integer version

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.1.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild 

* Wed Jan 20 2016 Antonio Trande <sagitter@fedoraproject.org> - 5.1.0-10
- Removed ExcludeArch

* Wed Jan 20 2016 Antonio Trande <sagitter@fedoraproject.org> - 5.1.0-9
- Defined OpenMP support
- Some cleanups of the SPEC file

* Wed Dec 23 2015 Antonio Trande <sagitter@fedoraproject.org> - 5.1.0-8
- Used always 'cmake' command

* Thu Oct 29 2015 Antonio Trande <sagitter@fedoraproject.org> - 5.1.0-7
- Rebuild for cmake 3.4.0
- Hardened builds on <F23

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jan 15 2015 Antonio Trande <sagitter@fedoraproject.org>  - 5.1.0-5
- Built on EPEL7
- Used new macro %%license

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Apr 14 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.1.0-1
- Update to 5.1.0

* Sun Mar 31 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-10
- Removed BR 'perl-Carp' (Bug 926996)
- Added LD_PRELOAD before help2man tasks to fix manpage shared_lib_error

* Sun Mar 24 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-9
- Added BR 'perl-Carp' for Fedora
- Excluded manpage creation for 'cmpfillin' and 'graphchk' commands

* Wed Mar 20 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-8
- Added BR cmake28 for EPEL6 building
- Set up of manpages creation in EPEL6

* Wed Mar 20 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-7
- Removed explicit manpages compression
- License tag changed to 'ASL 2.0 and BSD and LGPLv2+'

* Wed Mar 20 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-6
- Modified %%check section to perform tests properly

* Tue Mar 19 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-5
- Added %%check section
- Removed GK*.h libraries installation

* Sun Mar 17 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-4
- Added patch to sets up GKREGEX, GKRAND, libsuffix options to the Makefiles
- Configured patch2 condition
- soname version of libmetis changed to 0
- Added cmake options and flags to check openmp
- GKlib_includes destination changed to include/metis
- Added commands to generate binaries man-page
- Added BR openmpi-devel, pcre-devel, help2man

* Fri Mar 15 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-3
- Static sub-package removed
- TEMPORARY fix for files in "/usr/lib" removed
- Added patches for set up shared GKlib and soname libmetis 
- Removed BR chrpath

* Thu Mar 14 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-2
- Initial release changed from 0 to 1
- Removed chrpath command
- Added metis-width-datatype.patch only for 64bit systems
- Build commands completely changed to use %%cmake
- TEMPORARY fix for files in "/usr/lib"

* Sat Mar 02 2013 Antonio Trande <sagitter@fedoraproject.org> - 5.0.3-1
- Initial package
- Removed chrpaths
- Added BR chrpath
- Removed exec permissions to silence spurious-executable-perm warning

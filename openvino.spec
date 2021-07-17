#
# Conditional build:
%bcond_without	apidocs		# API documentation
%bcond_without	static_libs	# static libraries
%bcond_without	opencv		# OpenCV support
%bcond_with	gna		# GNA engine support (proprietary, x86_64 only, downloading from https://download.01.org/opencv/2020/openvinotoolkit/2020.3/inference_engine/GNA_01.00.00.1401.zip)
#
Summary:	OpenVINO - deep learning deployment toolkit
Summary(pl.UTF-8):	OpenVINO - narzędzia do wdrażania głębokiego uczenia
Name:		openvino
Version:	2020.3.2
Release:	0.1
License:	Apache v2.0
Group:		Libraries
#Source0Download: https://github.com/openvinotoolkit/openvino/releases
Source0:	https://github.com/openvinotoolkit/openvino/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	f756d94110e2ddb5bf8c50d63cc910fd
%define		ade_gitref	cbe2db61a659c2cc304c3837406f95c39dfa938e
Source1:	https://github.com/opencv/ade/archive/%{ade_gitref}/ade-%{ade_gitref}.tar.gz
# Source1-md5:	7b78a98fdc4906dcdfb809e11848189e
%define		ngraph_gitref	1797d7fb712d2ffa6048ce5f5b3b560b84ab5ae4
Source2:	https://github.com/NervanaSystems/ngraph/archive/%{ngraph_gitref}/ngraph-%{ngraph_gitref}.tar.gz
# Source2-md5:	07c44d55373c8ea04de35cd66a2b3c4c
Source3:	https://download.01.org/opencv/2020/openvinotoolkit/2020.3/inference_engine/firmware_pcie-ma248x_1656.zip
# Source3-md5:	93be199f56fbb0afa4fd10fe144d7734
Source4:	https://download.01.org/opencv/2020/openvinotoolkit/2020.3/inference_engine/firmware_usb-ma2450_1656.zip
# Source4-md5:	9e0ec96b2d8458468a74b1e2fbeab417
Source5:	https://download.01.org/opencv/2020/openvinotoolkit/2020.3/inference_engine/firmware_usb-ma2x8x_1656.zip
# Source5-md5:	aa7da91690d47f53470d1d084fbdf4d5
Patch0:		%{name}-no-download.patch
URL:		https://github.com/openvinotoolkit/openvino
BuildRequires:	cmake >= 3.7.2
BuildRequires:	libstdc++-devel >= 6:4.7
%{?with_opencv:BuildRequires:	opencv-devel >= 4.3}
BuildRequires:	protobuf-devel >= 2.6.1
BuildRequires:	tbb-devel >= 2020.3
# if using noarch subpackages:
#BuildRequires:	rpm-build >= 4.6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This toolkit allows developers to deploy pre-trained deep learning
models through a high-level C++ Inference Engine API integrated with
application logic. 

%description -l pl.UTF-8
Ten zestaw narzędzi pozwala programistom wdrażać wstępnie wytrenowane
modele uczenia głębokiego poprzez wysokopoziomowe API C++ Inference
Engine, zintegrowane z logiką aplikacyjną.

%package devel
Summary:	Header files for OpenVINO library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki OpenVINO
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for OpenVINO library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki OpenVINO.

%package static
Summary:	Static OpenVINO library
Summary(pl.UTF-8):	Statyczna biblioteka OpenVINO
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static OpenVINO library.

%description static -l pl.UTF-8
Statyczna biblioteka OpenVINO.

%package apidocs
Summary:	API documentation for OpenVINO library
Summary(pl.UTF-8):	Dokumentacja API biblioteki OpenVINO
Group:		Documentation
#BuildArch:	noarch

%description apidocs
API documentation for OpenVINO library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki OpenVINO.

%prep
%setup -q
%patch0 -p1

%{__tar} xf %{SOURCE1} --strip-components=1 -C inference-engine/thirdparty/ade
%{__tar} xf %{SOURCE2} --strip-components=1 -C ngraph
# allow custom CMAKE_BUILD_TYPE
%{__sed} -i -e '/^if (CMAKE_BUILD_TYPE/,/^endif/ d' ngraph/CMakeLists.txt
%{__sed} -i -e '/^include(linux_name)/,/^endif/ c set(LINUX_OS_NAME PLD)' inference-engine/cmake/dependencies.cmake

install -d inference-engine/temp/download
ln -snf %{SOURCE3} %{SOURCE4} %{SOURCE5} inference-engine/temp/download

%build
install -d build
cd build
%cmake --debug-output --debug-find .. \
	%{!?with_gna:-DENABLE_GNA=OFF} \
	%{!?with_opencv:-DENABLE_OPENCV=OFF} \
	-DENABLE_UNSAFE_LOCATIONS=ON \
%ifnarch %{x8664} x32
	-DENABLE_AVX2=OFF \
	-DENABLE_AVX512F=OFF \
	-DENABLE_SSE42=OFF \
%endif
	-DNGRAPH_USE_SYSTEM_PROTOBUF=ON \
	-DTBB_DIR=/usr \
	-DTBBROOT=/usr \
	-DTREAT_WARNING_AS_ERROR=OFF

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_libdir}/%{name}.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/%{name}.so.N

%files devel
%defattr(644,root,root,755)
%doc devel-doc/* ChangeLog NEWS TODO
%attr(755,root,root) %{_libdir}/%{name}.so
%{_includedir}/%{name}
%{_aclocaldir}/%{name}.m4
%{_pkgconfigdir}/%{name}.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/%{name}.a
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc apidocs/*
%endif

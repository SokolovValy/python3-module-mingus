%define pypi_name mingus


Name: python3-module-%pypi_name
Version: 0.6.1
Release: alt1

Summary: Сross-platform music theory and notation package for Python with MIDI file and playback support.
License: GPLv3
Group: Other
Url: https://github.com/bspaans/python-mingus
Packager: Valentin Sokolov <sova@altlinux.org>

BuildArch: noarch

Source: %name-%version.tar

BuildRequires(pre): rpm-build-python3 rpm-build-gir
BuildRequires: rpm-build-compat >= 1.2
BuildRequires: python3(setuptools)
BuildRequires: python3(wheel)

%description
Mingus is an advanced, cross-platform music theory and notation package for
Python with MIDI file and playback support. It can be used to play around
with music theory, to build editors, educational tools and other
applications that need to process and/or play music. It can also
be used to create sheet music with LilyPond.

%prep
%setup

%build
%pyproject_build

%install
%pyproject_install

%files
%doc README.md  CHANGELOG.md CONTRIBUTING.md LICENSE
%python3_sitelibdir/%pypi_name/
%python3_sitelibdir/%{pyproject_distinfo %pypi_name}


%changelog
* Fri Jun 9 2023 Valentin Sokolov <sova@altlinux.org> 0.6.1-alt1
- Initial build for Sisyphus


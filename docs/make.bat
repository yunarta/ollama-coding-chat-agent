@ECHO OFF
set SPHINXBUILD=sphinx-build
set SOURCEDIR=.
set BUILDDIR=_build

if "%1"=="clean" goto clean
if "%1"=="html" goto html

:help
ECHO Targets: html clean
goto end

:html
%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%/html
goto end

:clean
rmdir /s /q %BUILDDIR%

:end

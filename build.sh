#!/bin/sh

# Checkout submodules
git submodule init
git submodule update --init --recursive

version=$(grep -oP '(?<=version=).*' act/default/app.conf)
filename=dist/act-${version}.spl
mkdir -p dist
rm -f $filename

# Exclude files that will make splunk-appinspect fail
tar zcf $filename \
    --exclude-vcs-ignores \
    --exclude=./build.sh \
    --exclude=act/local \
    --exclude=act/metadata/local.meta \
    --exclude=act/bin/lib/requests/.github \
    --exclude=act/bin/lib/chardet/.gitattributes \
    --exclude=act/bin/lib/chardet/tests \
    --exclude=act/bin/lib/urllib3/tox.ini \
    --exclude=act/bin/lib/urllib3/Makefile \
    --exclude=act/bin/lib/urllib3/docs/Makefile \
    --exclude=bin/lib/requests/docs/Makefile \
    --exclude=__pycache__ \
    --exclude=act/bin/lib/chardet/docs/Makefile \
    --exclude=.git \
    --exclude=\*.pyc \
    --exclude=.gitignore \
    --exclude=.gitmodules \
    --exclude=.travis.yml \
    --exclude=.coveragerc \
    act

splunk-appinspect inspect $filename

echo "package: ${filename}"

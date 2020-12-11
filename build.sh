#!/bin/sh

# Checkout submodules
git submodule init
git submodule update --recursive --remote

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
    --exclude=__pycache__ \
    --exclude=.git \
    --exclude=\*.pyc \
    --exclude=act/bin/lib/act-api-python/test/ \
    --exclude=.gitignore \
    --exclude=.gitmodules \
    --exclude=.travis.yml \
    --exclude=.coveragerc \
    act

splunk-appinspect inspect $filename

echo "package: ${filename}"

#!/bin/bash

set -e

# Download Blender. Latest version likely works.
blender_path=Blender2.76/blender-2.76b-linux-glibc211-x86_64.tar.bz2
blender_basename=$(basename $blender_path)
if [[ ! -f $blender_basename ]]; then
    curl -O http://download.blender.org/release/$blender_path
    tar xf $blender_basename
    ln -sfn ${blender_basename%.tar.bz2} blender
    (cd blender && patch -p0 -s <../stl-export-blender.patch)
fi

# Install Python modules
pip install --target=converter/py-lib/boto3 boto3==1.2.2
pip install xlwt xlrd # for translation file conversions

# Create symlinks
ln -s ../OSM2World ../blender converter

#!/bin/sh

CWD=$(pwd)

docker run -p 4000:80 \
    -v $CWD/converted_files:/app/converted_files \
    -v $CWD/original_files:/app/original_files \
    convert_to_md

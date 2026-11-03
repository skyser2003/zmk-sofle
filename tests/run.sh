#!/usr/bin/env bash
set -euo pipefail
test_root=$(cd -- "$(dirname -- "$0")/.." && pwd)
test_build=$(mktemp -d)
trap 'rm -rf "$test_build"' EXIT
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined \
    -I"$test_root/tests/stubs" -I"$test_root/include" \
    "$test_root/tests/encoder_virtual_keys.c" -o "$test_build/encoder_virtual_keys"
"$test_build/encoder_virtual_keys"

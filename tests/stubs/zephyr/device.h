/* SPDX-License-Identifier: MIT */
#pragma once
#include <stdbool.h>
#include <stdint.h>

#define BUILD_ASSERT(condition, message) _Static_assert(condition, message)
#define DT_INST_FOREACH_STATUS_OKAY(fn)

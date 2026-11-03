/* SPDX-License-Identifier: MIT */
#pragma once
#include <stdbool.h>
#include <stdint.h>

struct zmk_behavior_binding {
    uint32_t param1;
};

struct zmk_behavior_binding_event {
    uint32_t position;
    int64_t timestamp;
    uint8_t source;
};

enum { BEHAVIOR_LOCALITY_CENTRAL = 0 };

struct behavior_driver_api {
    int (*binding_pressed)(struct zmk_behavior_binding *, struct zmk_behavior_binding_event);
    int (*binding_released)(struct zmk_behavior_binding *, struct zmk_behavior_binding_event);
    int locality;
};

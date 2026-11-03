/* SPDX-License-Identifier: MIT */
#pragma once
#include <stdbool.h>
#include <stdint.h>

#define ZMK_POSITION_STATE_CHANGE_SOURCE_LOCAL UINT8_MAX

struct zmk_position_state_changed {
    uint8_t source;
    uint32_t position;
    bool state;
    int64_t timestamp;
};

int raise_zmk_position_state_changed(struct zmk_position_state_changed event);

/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include "../src/behavior_sofle_encoder_key.c"

static struct zmk_position_state_changed received[2];
static unsigned int received_count;
static int dispatch_error;

int raise_zmk_position_state_changed(struct zmk_position_state_changed event) {
    if (dispatch_error) {
        return dispatch_error;
    }
    assert(received_count < 2);
    received[received_count++] = event;
    return 0;
}

int main(void) {
    struct zmk_behavior_binding_event event = {
        .position = 100, /* The sensor's own position must not become the key position. */
        .source = 1,
    };

    assert(encoder_key_api.locality == BEHAVIOR_LOCALITY_CENTRAL);
    for (unsigned int step = 0; step < 2000; step++) {
        uint32_t position = step % 2 ? SOFLE_ENCODER_CW_POSITION : SOFLE_ENCODER_CCW_POSITION;
        struct zmk_behavior_binding binding = {.param1 = position};
        received_count = 0;
        event.timestamp = step * 10;
        assert(encoder_key_api.binding_pressed(&binding, event) == 0);
        event.timestamp += 5;
        assert(encoder_key_api.binding_released(&binding, event) == 0);
        assert(received_count == 2);
        assert(received[0].position == position && received[1].position == position);
        assert(received[0].state && !received[1].state);
        assert(received[0].source == ZMK_POSITION_STATE_CHANGE_SOURCE_LOCAL);
        assert(received[1].source == ZMK_POSITION_STATE_CHANGE_SOURCE_LOCAL);
        assert(received[1].timestamp - received[0].timestamp == 5);
    }

    uint32_t invalid[] = {0, 63, 66, UINT32_MAX};
    for (unsigned int i = 0; i < sizeof(invalid) / sizeof(invalid[0]); i++) {
        struct zmk_behavior_binding binding = {.param1 = invalid[i]};
        received_count = 0;
        assert(encoder_key_api.binding_pressed(&binding, event) == -EINVAL);
        assert(encoder_key_api.binding_released(&binding, event) == -EINVAL);
        assert(received_count == 0);
    }

    struct zmk_behavior_binding binding = {.param1 = SOFLE_ENCODER_CW_POSITION};
    dispatch_error = -EIO;
    assert(encoder_key_api.binding_pressed(&binding, event) == -EIO);
    assert(encoder_key_api.binding_released(&binding, event) == -EIO);
    assert(received_count == 0);
    puts("Encoder virtual keys: balanced direction events, bounds and dispatch errors passed.");
}

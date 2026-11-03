/* SPDX-License-Identifier: MIT */
#define DT_DRV_COMPAT zmk_behavior_sofle_encoder_key

#include <errno.h>
#include <zephyr/device.h>
#include <drivers/behavior.h>
#include <dt-bindings/zmk/eyelash_sofle.h>
#include <zmk/events/position_state_changed.h>
#include <zmk/matrix.h>

BUILD_ASSERT(SOFLE_ENCODER_CW_POSITION < ZMK_KEYMAP_LEN,
             "The Sofle layout must include both encoder rotation keys");

static int encoder_key_event(struct zmk_behavior_binding *binding,
                             struct zmk_behavior_binding_event event, bool pressed) {
    if (binding->param1 != SOFLE_ENCODER_CCW_POSITION &&
        binding->param1 != SOFLE_ENCODER_CW_POSITION) {
        return -EINVAL;
    }

    return raise_zmk_position_state_changed((struct zmk_position_state_changed){
        .source = ZMK_POSITION_STATE_CHANGE_SOURCE_LOCAL,
        .position = binding->param1,
        .state = pressed,
        .timestamp = event.timestamp,
    });
}

static int encoder_key_pressed(struct zmk_behavior_binding *binding,
                               struct zmk_behavior_binding_event event) {
    return encoder_key_event(binding, event, true);
}

static int encoder_key_released(struct zmk_behavior_binding *binding,
                                struct zmk_behavior_binding_event event) {
    return encoder_key_event(binding, event, false);
}

static const struct behavior_driver_api encoder_key_api = {
    .binding_pressed = encoder_key_pressed,
    .binding_released = encoder_key_released,
    .locality = BEHAVIOR_LOCALITY_CENTRAL,
};

#define ENCODER_KEY_INST(n)                                                                         \
    BEHAVIOR_DT_INST_DEFINE(n, NULL, NULL, NULL, NULL, POST_KERNEL,                                  \
                            CONFIG_KERNEL_INIT_PRIORITY_DEFAULT, &encoder_key_api);

DT_INST_FOREACH_STATUS_OKAY(ENCODER_KEY_INST)

# SPDX-License-Identifier: MIT
target_sources_ifdef(CONFIG_ZMK_BEHAVIOR_SOFLE_ENCODER_KEY app PRIVATE
  src/behavior_sofle_encoder_key.c)
zephyr_include_directories(include)

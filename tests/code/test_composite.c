#include "composite.h"

#include <assert.h>

uint32_t init_ = 0;
uint32_t exit_ = 0;

int main(int argc, char** argv)
{
    composite_sc_t sc;
    composite_init(&sc);
    assert(sc.state == COMPOSITE_ST_LEVEL_ZERO);
    assert(sc.level_zero_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE);
    assert(sc.level_zero_level_one_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE_LEVEL_TWO);
    assert(init_ == (0x1 | 0x2 | 0x4));
    assert(exit_ == 0);
    composite_handle_event(&sc, COMPOSITE_EVT_EVENT_THREE);
    assert(sc.state == COMPOSITE_ST_LEVEL_ZERO);
    assert(sc.level_zero_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE);
    assert(sc.level_zero_level_one_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE_LEVEL_TWO_ONE);
    assert(exit_ == 0x4);
    composite_handle_event(&sc, COMPOSITE_EVT_RESET);
    assert(sc.state == COMPOSITE_ST_LEVEL_ZERO);
    assert(sc.level_zero_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE);
    assert(sc.level_zero_level_one_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE_LEVEL_TWO);
    assert(init_ == (0x1 | 0x2 | 0x4));
    assert(exit_ == 0);
    composite_handle_event(&sc, COMPOSITE_EVT_EVENT_TWO);
    assert(sc.state == COMPOSITE_ST_LEVEL_ZERO);
    assert(sc.level_zero_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE_TWO);
    assert(init_ == (0x1 | 0x2 | 0x4));
    assert(exit_ == (0x2 | 0x4));
    composite_handle_event(&sc, COMPOSITE_EVT_RESET);
    composite_handle_event(&sc, COMPOSITE_EVT_EVENT_THREE);
    exit_ = 0;
    composite_handle_event(&sc, COMPOSITE_EVT_EVENT_TWO);
    assert(sc.state == COMPOSITE_ST_LEVEL_ZERO);
    assert(sc.level_zero_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE_THREE);
    assert(exit_ == (0x2));
    composite_handle_event(&sc, COMPOSITE_EVT_RESET);
    composite_handle_event(&sc, COMPOSITE_EVT_EVENT_ONE);
    assert(init_ == (0x1 | 0x2 | 0x4));
    assert(exit_ == (0x2 | 0x4));
    assert(sc.state == COMPOSITE_ST_LEVEL_ZERO);
    assert(sc.level_zero_state == COMPOSITE_ST_LEVEL_ZERO_LEVEL_ONE_TWO);
    return 0;
}
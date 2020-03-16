#include "internal_transition.h"

#include <assert.h>

int number;

int main(int argc, char** argv)
{
    internal_transition_sc_t sc;
    internal_transition_init(&sc);
    assert(number == 0);
    internal_transition_handle_event(&sc, INTERNAL_TRANSITION_EVT_RES);
    assert(number == -1);
    internal_transition_handle_event(&sc, INTERNAL_TRANSITION_EVT_RES);
    assert(number == 1);
    internal_transition_handle_event(&sc, INTERNAL_TRANSITION_EVT_INC);
    assert(number == 2);
    internal_transition_handle_event(&sc, INTERNAL_TRANSITION_EVT_DEC);
    assert(number == 1);
    return 0;
}
#include "transient_state.h"

#include <assert.h>

int number;

int main(int argc, char** argv)
{
    transient_state_sc_t sc;
    number = 0;
    transient_state_init(&sc);
    assert(sc.state == TRANSIENT_STATE_ST_ON);
    number = 2;
    transient_state_handle_event(&sc, TRANSIENT_STATE_EVT_RESET);
    assert(sc.state == TRANSIENT_STATE_ST_OFF);
    number = 1;
    transient_state_handle_event(&sc, TRANSIENT_STATE_EVT_RESET);
    assert(sc.state == TRANSIENT_STATE_ST_ERROR);
    return 0;
}
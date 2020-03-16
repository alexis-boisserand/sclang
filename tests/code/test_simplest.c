#include "simplest.h"

#include <assert.h>

int main(int argc, char** argv)
{
    simplest_sc_t sc;
    simplest_init(&sc);
    assert(sc.state == SIMPLEST_ST_ON);
    simplest_handle_event(&sc, SIMPLEST_EVT_PRESS);
    assert(sc.state == SIMPLEST_ST_ON);
    simplest_handle_event(&sc, SIMPLEST_EVT_TIMEOUT);
    assert(sc.state == SIMPLEST_ST_OFF);
    simplest_handle_event(&sc, SIMPLEST_EVT_TIMEOUT);
    assert(sc.state == SIMPLEST_ST_OFF);
    simplest_handle_event(&sc, SIMPLEST_EVT_PRESS);
    assert(sc.state == SIMPLEST_ST_ON);
    return 0;
}
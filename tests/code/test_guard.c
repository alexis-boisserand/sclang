#include "guard.h"

#include <assert.h>

int number = 0;

int main(int argc, char** argv)
{
    guard_sc_t sc;
    guard_init(&sc);
    assert(sc.state == GUARD_ST_ON);
    guard_handle_event(&sc, GUARD_EVT_PRESS);
    assert(sc.state == GUARD_ST_ON);
    number = 1;
    guard_handle_event(&sc, GUARD_EVT_TIMEOUT);
    assert(sc.state == GUARD_ST_ON);
    number = 2;
    guard_handle_event(&sc, GUARD_EVT_TIMEOUT);
    assert(sc.state == GUARD_ST_OFF);
    guard_handle_event(&sc, GUARD_EVT_TIMEOUT);
    assert(sc.state == GUARD_ST_OFF);
    guard_handle_event(&sc, GUARD_EVT_PRESS);
    assert(sc.state == GUARD_ST_OFF);
    number = 4;
    guard_handle_event(&sc, GUARD_EVT_PRESS);
    assert(sc.state == GUARD_ST_ON);
    number = 18;
    guard_handle_event(&sc, GUARD_EVT_PRESS);
    assert(sc.state == GUARD_ST_ON);
    guard_handle_event(&sc, GUARD_EVT_TIMEOUT);
    assert(sc.state == GUARD_ST_ERROR);
    return 0;
}
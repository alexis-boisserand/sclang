#include "guard.h"

#include <assert.h>

int number = 0;

int main(int argc, char** argv)
{
    guard_sc_t sc;
    guard_init(&sc);
    assert(sc.state == GUARD_ON);
    guard_handle_event(&sc, GUARD_PRESS);
    assert(sc.state == GUARD_ON);
    number = 1;
    guard_handle_event(&sc, GUARD_TIMEOUT);
    assert(sc.state == GUARD_ON);
    number = 2;
    guard_handle_event(&sc, GUARD_TIMEOUT);
    assert(sc.state == GUARD_OFF);
    guard_handle_event(&sc, GUARD_TIMEOUT);
    assert(sc.state == GUARD_OFF);
    guard_handle_event(&sc, GUARD_PRESS);
    assert(sc.state == GUARD_OFF);
    number = 4;
    guard_handle_event(&sc, GUARD_PRESS);
    assert(sc.state == GUARD_ON);
    number = 18;
    guard_handle_event(&sc, GUARD_PRESS);
    assert(sc.state == GUARD_ON);
    guard_handle_event(&sc, GUARD_TIMEOUT);
    assert(sc.state == GUARD_ERROR);
    return 0;
}
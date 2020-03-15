#include "simplest.h"

#include <string.h>
#include <assert.h>
#include <stdio.h>

int main(int argc, char** argv)
{
    simplest_sc_t sc;
    simplest_init(&sc);
    assert(sc.state == SIMPLEST_ON);
    simplest_handle_event(&sc, SIMPLEST_PRESS);
    assert(sc.state == SIMPLEST_ON);
    simplest_handle_event(&sc, SIMPLEST_TIMEOUT);
    assert(sc.state == SIMPLEST_OFF);
    simplest_handle_event(&sc, SIMPLEST_TIMEOUT);
    assert(sc.state == SIMPLEST_OFF);
    simplest_handle_event(&sc, SIMPLEST_PRESS);
    assert(sc.state == SIMPLEST_ON);
    return 0;
}
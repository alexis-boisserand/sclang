#include "simplest.h"

#include <string.h>
#include <assert.h>
#include <stdio.h>

const char* simplest_get_current_state(void);

void check_state(const char* state)
{
    assert(strcmp(simplest_get_current_state(), state) == 0);
}

int main(int argc, char** argv)
{
    simplest_init();
    check_state("Off");
    simplest_handle_event(TIMEOUT);
    check_state("Off");
    simplest_handle_event(BUTTON_PRESS);
    check_state("On");
    simplest_handle_event(BUTTON_PRESS);
    check_state("On");
    simplest_handle_event(TIMEOUT);
    check_state("Off");
    return 0;
}
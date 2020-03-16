#include "actions.h"

#include <assert.h>

int numbers[3];

int main(int argc, char** argv)
{
    actions_sc_t sc;
    actions_init(&sc);
    assert(numbers[0] == 1 && numbers[1] == 2 && numbers[2] == 3);
    actions_handle_event(&sc, ACTIONS_EVT_ERROR);
    assert(numbers[0] == 1 && numbers[1] == 1 && numbers[2] == 4);
    actions_handle_event(&sc, ACTIONS_EVT_RESET);
    assert(numbers[0] == 1 && numbers[1] == 2 && numbers[2] == 3);
    actions_handle_event(&sc, ACTIONS_EVT_TIMEOUT);
    assert(numbers[0] == 1 && numbers[1] == 3 && numbers[2] == 3);
    return 0;
}
/**
 * @file
 * simplest statechart implementation.
 * @note This file was automatically generated using scgen (https://github.com/alexis-boisserand/scgen).
 * Please don't edit it manually.
 */
#include "simplest.h"

typedef enum
{
    OFF,
    ON
} simplest_state_t;

static simplest_state_t current_state;

static void simplest_off_handle_event(simplest_event_t event);
static void simplest_on_handle_event(simplest_event_t event);

static void simplest_off_handle_event(simplest_event_t event)
{
    switch (event)
    {
    case BUTTON_PRESS:
        current_state = ON;
        break;
    }
}

static void simplest_on_handle_event(simplest_event_t event)
{
    switch (event)
    {
    case TIMEOUT:
        current_state = OFF;
        break;
    }
}

void simplest_init(void)
{
    current_state = OFF;
}

void simplest_handle_event(simplest_event_t event)
{
    switch (current_state)
    {
    case OFF:
        simplest_off_handle_event(event);
        break;
    case ON:
        simplest_on_handle_event(event);
        break;
    }
}

#ifdef UNIT_TEST
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct
{
    simplest_state_t state;
    const char* name;
} simplest_state_desc_t;

static simplest_state_desc_t states_descriptions[] = 
{
    { OFF, "Off" },
    { ON, "On" }
};

const char* simplest_get_current_state(void)
{
    for (size_t i = 0; i < sizeof(states_descriptions) / sizeof(simplest_state_desc_t); i++)
    {
        if (states_descriptions[i].state == current_state)
        {
            return states_descriptions[i].name;
        }
    }

    assert(false);
    return "";
}

#endif // UNIT_TEST


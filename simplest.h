/**
 * @file
 * Declarations for the simplest statechart.
 * @note This file was automatically generated using scgen (https://github.com/alexis-boisserand/scgen).
 * Please don't edit it manually.
 */
#ifndef SIMPLEST_H
#define SIMPLEST_H

typedef enum
{
    TIMEOUT,
    BUTTON_PRESS
} simplest_event_t;

void simplest_init(void);
void simplest_handle_event(simplest_event_t event);

#endif // SIMPLEST_H

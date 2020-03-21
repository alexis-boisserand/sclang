#include "composite.h"

#include <assert.h>

uint32_t init_ = 0;
uint32_t exit_ = 0;
uint32_t action = 0;

int main(int argc, char** argv)
{
    composite_sc_t sc;
    composite_init(&sc);
    assert(init_ == 0x3);
    assert(exit_ == 0);
    return 0;
}
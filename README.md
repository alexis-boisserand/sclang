![build](https://github.com/alexis-boisserand/sclang/workflows/build/badge.svg)
# sclang

## Introduction
sclang is a compact declarative language for state machine description. It is bundled with two tools:
* code: A C code generator to automatically generate the boilerplate code for the state machine logic. It generates simple, easy to read C99 code that only depends on <stdbool.h>.

* graph: A statechart diagram generator to quickly validate and document the state machine design.

## Simple example
```
/turnstile
Locked
  @COIN -> Unlocked
Unlocked
  @PUSH -> Locked
```
![simple example](doc/turnstile.png)

// installation

// usage

// concepts

- events

- guards

- hsm and paths

- actions

- targetless transitions

- transient state

// cmake integration
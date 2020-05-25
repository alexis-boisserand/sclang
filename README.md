![build](https://github.com/alexis-boisserand/sclang/workflows/build/badge.svg)
# sclang

## Introduction
sclang is a compact declarative language for state machine description. It is bundled with two tools:
* code: a C code generator
* graph: a statechart diagram generator

The code generator automatically generates all the boilerplate code related to the state machine logic,
allowing the developer to only focus on the actions of the system.
The main target being reactive embedded systems, it generates simple, easy to read C99 code that only depends on <stdbool.h>.


// made for embedded systems
// simple C code with no dependencies
// state machine correctness

## Simple example
```
/simplest
On
  @TIMEOUT -> Off
Off
  @PRESS -> On
```
![simple example](doc/simplest.png)

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
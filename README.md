# morphine

Simple Prolog trace formatter.

This is a simple wrapper around [swipl](https://www.swi-prolog.org/) 
tracer. To be more precise morphine creates its own shell and runs
```console
swipl -s path/to/file -g "leash(-all),trace,start." -t halt
```
When output seems like swipl's tracing morphine formats it.

## Requirements

- python 3.5 or higher
- swipl

## Installation

```console
pip install morphine
```

## Usage

```console
morphine path/to/prolog/file
```

Make sure the file has the predicate `start/0` (takes no arguments).
Morphine automatically runs this predicate.

### User input

Morphine's shell can receive and pass to swipl user input.
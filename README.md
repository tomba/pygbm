[![Lint Status](https://github.com/tomba/pygbm/actions/workflows/ci.yml/badge.svg)](https://github.com/tomba/pygbm/actions/workflows/ci.yml)

# Pure-Python Linux GBM (Generic Buffer Management) bindings

## gbm.capi

gbm.capi namespace contains the bindings to the libgbm C API.

The bindings are generated with (slighly customized) ctypesgen, with the gen.py script.

## gbm

gbm namespace contains wrappers to the C API to simplify its use. The target is that the user of the gbm namespace does not need to use any types from the gbm.capi namespace.

## License

This project is covered by the [LGPL-3.0](LICENSE.md) license.

## Install

`pip install git+https://github.com/tomba/pygbm.git`

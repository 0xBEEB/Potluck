#include "Python.h"

#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <assert.h>
#include <stdlib.h>

#include "alpm.h"
#include "alpm_list.h"


static PyObject *py_cb_event = NULL;
static PyObject *py_cb_conv = NULL;
static PyObject *py_cb_progress = NULL;
static PyObject *py_cb_dl_progress = NULL;
static PyObject *py_cb_dl_total_progress = NULL;



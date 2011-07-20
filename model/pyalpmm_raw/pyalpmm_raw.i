// alpm interface

%module pyalpmm_raw

%inline %{

#include "alpm_list.h"
#include "alpm.h"

static PyObject *py_cb_event = NULL;
static PyObject *py_cb_conv = NULL;
static PyObject *py_cb_progress = NULL;
static PyObject *py_cb_dl_progress = NULL;
static PyObject *py_cb_dl_total_progress = NULL;

void cb_python_event_wrap(pmtransevt_t event, void *data1, void *data2){
	PyObject *arglist = NULL;
	PyObject *d1 = Py_None;
	PyObject *d2 = Py_None;

	switch(event) {
		case PM_TRANS_EVT_ADD_START:
		case PM_TRANS_EVT_ADD_DONE:
		case PM_TRANS_EVT_REMOVE_START:
		case PM_TRANS_EVT_REMOVE_DONE:
		case PM_TRANS_EVT_UPGRADE_START:
			d1 = SWIG_NewPointerObj(SWIG_as_voidptr(data1), SWIGTYPE_p___pmpkg_t, 0 );
			break;
		case PM_TRANS_EVT_UPGRADE_DONE:
			d1 = SWIG_NewPointerObj(SWIG_as_voidptr(data1), SWIGTYPE_p___pmpkg_t, 0 );
			d2 = SWIG_NewPointerObj(SWIG_as_voidptr(data2), SWIGTYPE_p___pmpkg_t, 0 );
			break;
		case PM_TRANS_EVT_DELTA_PATCH_START:
			arglist = Py_BuildValue("(i,s,s)", event, data1, data2);
			break;
		case PM_TRANS_EVT_SCRIPTLET_INFO:
		case PM_TRANS_EVT_RETRIEVE_START:
			arglist = Py_BuildValue("(i,s,O)", event, data1, d2);
			break;
	}
	if (!arglist)
		arglist = Py_BuildValue("(i,O,O)", event, d1, d2);

	PyEval_CallObject(py_cb_event, arglist);
	Py_DECREF(arglist);
}

void cb_python_conv_wrap(pmtransconv_t event, void *data1, void *data2, void *data3, int *response){
	PyObject *arglist = NULL;
	PyObject *d1 = Py_None;
	PyObject *d2 = Py_None;
	PyObject *d3 = Py_None;

	switch(event) {
		case PM_TRANS_CONV_INSTALL_IGNOREPKG:
			if(data2) {
				d1 = SWIG_NewPointerObj(SWIG_as_voidptr(data1), SWIGTYPE_p___pmpkg_t, 0 );
				d2 = SWIG_NewPointerObj(SWIG_as_voidptr(data2), SWIGTYPE_p___pmpkg_t, 0 );
			} else {
				d1 = SWIG_NewPointerObj(SWIG_as_voidptr(data1), SWIGTYPE_p___pmpkg_t, 0 );
			}
			break;
		case PM_TRANS_CONV_LOCAL_NEWER:
		case PM_TRANS_CONV_REMOVE_PKGS:
			d1 = SWIG_NewPointerObj(SWIG_as_voidptr(data1), SWIGTYPE_p___pmpkg_t, 0 );
			break;
		case PM_TRANS_CONV_REPLACE_PKG:
			d1 = SWIG_NewPointerObj(SWIG_as_voidptr(data1), SWIGTYPE_p___pmpkg_t, 0 );
			d2 = SWIG_NewPointerObj(SWIG_as_voidptr(data2), SWIGTYPE_p___pmpkg_t, 0 );
			arglist = Py_BuildValue("(i,O,O,s)", event, d1, d2, data3);
			break;
		case PM_TRANS_CONV_CONFLICT_PKG:
			arglist = Py_BuildValue("(i,s,s,O)", event, data1, data2, d3);
			break;

		case PM_TRANS_CONV_CORRUPTED_PKG:
			arglist = Py_BuildValue("(i,s,O,O)", event, data1, d2, d3);
			break;
	}
	if (!arglist)
		arglist = Py_BuildValue("(i,O,O,O)", event, d1, d2, d3);

	*response = PyInt_AsLong(PyEval_CallObject(py_cb_conv, arglist));
	Py_DECREF(arglist);
}

void cb_python_progress_wrap(pmtransprog_t event, const char *pkgname, int percent, int howmany, int remain){
	PyObject *arglist = NULL;
	arglist = Py_BuildValue("(i,s,i,i,i)", event, pkgname, percent, howmany, remain);
	PyEval_CallObject(py_cb_progress, arglist);
	Py_DECREF(arglist);
}

void cb_python_dl_total_progress_wrap(off_t total){
	PyObject *arglist = NULL;
	arglist = Py_BuildValue("(i)", total);
	PyEval_CallObject(py_cb_dl_total_progress, arglist);
	Py_DECREF(arglist);
}

void cb_python_dl_progress_wrap(const char *filename, off_t file_xfered, off_t file_total){
	PyObject *arglist = NULL;
	arglist = Py_BuildValue("(s,i,i)", filename, file_xfered, file_total);
	PyEval_CallObject(py_cb_dl_progress, arglist);
	Py_DECREF(arglist);
}

%}

/*************************************************************/
/**						TypeMaps here!						**/
/*************************************************************/

%typemap(out) off_t, time_t {
    $result = PyLong_FromLong((long) $1);
}

%typemap(in) alpm_trans_cb_event cb_event (pmtransevt_t event, void *data1, void *data2) {
	if (!PyCallable_Check($input)) {
		PyErr_SetString(PyExc_TypeError, "Need a callable object!");
		$1 = NULL;
    }
    Py_XINCREF($input);
    Py_XDECREF(py_cb_event);
    py_cb_event = $input;
    $1 = cb_python_event_wrap;
}

%typemap(in) alpm_trans_cb_conv conv (pmtransconv_t event, void *data1, void *data2, void *data3, int *response) {
    if (!PyCallable_Check($input)) {
		PyErr_SetString(PyExc_TypeError, "Need a callable object!");
		$1 = NULL;
    }
    Py_XINCREF($input);
    Py_XDECREF(py_cb_conv);
    py_cb_conv = $input;
    $1 = cb_python_conv_wrap;
}

%typemap(in) alpm_trans_cb_progress cb_progress (pmtransprog_t event, const char *pkgname, int percent, int howmany, int remain) {
    if (!PyCallable_Check($input)) {
		PyErr_SetString(PyExc_TypeError, "Need a callable object!");
		$1 = NULL;
    }
    Py_XINCREF($input);
    Py_XDECREF(py_cb_progress);
    py_cb_progress = $input;
    $1 = cb_python_progress_wrap;
}

%typemap(in) alpm_cb_download cb (const char *filename, off_t xfered, off_t total) {
    if (!PyCallable_Check($input)) {
		PyErr_SetString(PyExc_TypeError, "Need a callable object!");
		$1 = NULL;
    }
    Py_XINCREF($input);
    Py_XDECREF(py_cb_dl_progress);
    py_cb_dl_progress = $input;
    $1 = cb_python_dl_progress_wrap;
}

%typemap(in) alpm_cb_totaldl cb (off_t total) {
    if (!PyCallable_Check($input)) {
		PyErr_SetString(PyExc_TypeError, "Need a callable object!");
		$1 = NULL;
    }
    Py_XINCREF($input);
    Py_XDECREF(py_cb_dl_total_progress);
    py_cb_dl_total_progress = $input;
    $1 = cb_python_dl_total_progress_wrap;
}

%include "alpm_list.h"
%include "alpm.h"

%include helper.i
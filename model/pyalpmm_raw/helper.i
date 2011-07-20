%inline %{



pmpkg_t *helper_list_getpkg(alpm_list_t *item){
    return (pmpkg_t*) alpm_list_getdata(item);
}

char *helper_list_getstr(alpm_list_t *item){
    return (char*) alpm_list_getdata(item);
}

pmgrp_t *helper_list_getgrp(alpm_list_t *item){
    return (pmgrp_t*) alpm_list_getdata(item);
}

pmdepmissing_t *helper_list_getmiss(alpm_list_t *item){
    return (pmdepmissing_t*) alpm_list_getdata(item);
}

pmdepend_t *helper_list_getdep(alpm_list_t *item){
    return (pmdepend_t*) alpm_list_getdata(item);
}

pmfileconflict_t *helper_list_getfileconflict(alpm_list_t *item){
    return (pmfileconflict_t*) alpm_list_getdata(item);
}

static alpm_list_t *list_buffer = NULL;

alpm_list_t **get_list_buffer_ptr(){
    return &list_buffer;
}

alpm_list_t *get_list_from_ptr(alpm_list_t **d){
    return *d;
}

alpm_list_t *helper_create_alpm_list(PyObject *list) {
    int i;
    alpm_list_t *out = NULL;
    char *string = NULL;

    for(i=0; i<PyList_Size(list); ++i){
        string = malloc(PyString_Size(PyList_GetItem(list, i)));
        Py_INCREF(string);
        strcpy(string, PyString_AsString(PyList_GetItem(list, i)));
        out = alpm_list_add(out, string);
    }
    return out;
}

char *helper_get_char(PyObject *str){
    return PyString_AsString(str);
}

int get_errno(){
    return (int) pm_errno;
}


%}

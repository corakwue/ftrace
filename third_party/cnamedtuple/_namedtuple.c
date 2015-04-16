#include "Python.h"
#include "structmember.h"

/* The values that the module will hold. These are needed by various functions
   supporting the namedtuple type. */
typedef struct{
    PyObject *iskeyword;  /* `keywords.iskeyword` */
    PyObject *asdict;     /* The constructor called from `_asdict`. */
}module_state;

/* The type of the descriptors that access the named fields of the `namedtuple`
   types. */
typedef struct{
    PyObject id_ob;
    Py_ssize_t id_idx;  /* The index that this will access. */
}namedtuple_indexer;

/* Index a tuple at `self`'s index like a specialized `itemgetter`. */
static PyObject *
namedtuple_indexer_descr_get(PyObject *self,
                             PyObject *instance,
                             PyObject *owner)
{
    PyObject *ret;

    if (!instance) {
        /* If this is called on the owner, then just return this object. */
        ret = self;
    }
    else {
        /* Assert that this is a tuple subclass. */
        if (!PyTuple_Check(instance)) {
            PyErr_Format(PyExc_TypeError,
                         "%s objects can only be used on tuple types",
                         ((PyTypeObject*) self->ob_type)->tp_name);
            return NULL;
        }

        if (!(ret = PyTuple_GetItem(instance,
                                    ((namedtuple_indexer*) self)->id_idx))) {
            return NULL;
        }
    }

    Py_INCREF(ret);
    return ret;
}

PyDoc_STRVAR(namedtuple_indexer_doc,
"A specialized 'itemgetter' for tuples where the index is known to be valid.");

/* A specialized `itemgetter` for tuples where the index is known to be
   valid. This cannot be constructed or subclassed from within python
   because if the preconditions are not followed, you would get undefined
   behaviour. */
PyTypeObject namedtuple_indexer_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "_collections.NamedTupleIndexerType",       /* tp_name */
    sizeof(namedtuple_indexer),                 /* tp_basicsize */
    0,                                          /* tp_itemsize */
    0,                                          /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_reserved */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    namedtuple_indexer_doc,                     /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    namedtuple_indexer_descr_get,               /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    0,                                          /* tp_new */
};

/* A wrapper around an object to make read-only access to it. */
typedef struct{
    PyObject wr_ob;
    PyObject *wr_wrapped;
}namedtuple_descr_wrapper;

static void
namedtuple_descr_wrapper_dealloc(PyObject *self)
{
    Py_CLEAR(((namedtuple_descr_wrapper*) self)->wr_wrapped);
    PyObject_GC_Del(self);
}

/* Retrieve the wrapped object. Because this will return the object even
   when `instance` is NULL, this is kind of like a class property. */
static PyObject *
namedtuple_descr_wrapper_get(PyObject *self,
                             PyObject *instance,
                             PyObject *owner)
{
    PyObject *ret = ((namedtuple_descr_wrapper*) self)->wr_wrapped;
    Py_INCREF(ret);
    return ret;
}

static int
namedtuple_descr_wrapper_traverse(PyObject *self, visitproc visit, void *arg)
{
    Py_VISIT(((namedtuple_descr_wrapper*) self)->wr_wrapped);
    return 0;
}

static int
namedtuple_descr_wrapper_clear(PyObject *self)
{
    Py_CLEAR(((namedtuple_descr_wrapper*) self)->wr_wrapped);
    return 0;
}

PyDoc_STRVAR(namedtuple_descr_wrapper_doc,
"A wrapper for objects for using the descriptor protocol.");

PyTypeObject namedtuple_descr_wrapper_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "_collections.NamedTupleDescrWrapper",             /* tp_name */
    sizeof(namedtuple_descr_wrapper),                  /* tp_basicsize */
    0,                                                 /* tp_itemsize */
    (destructor) namedtuple_descr_wrapper_dealloc,     /* tp_dealloc */
    0,                                                 /* tp_print */
    0,                                                 /* tp_getattr */
    0,                                                 /* tp_setattr */
    0,                                                 /* tp_reserved */
    0,                                                 /* tp_repr */
    0,                                                 /* tp_as_number */
    0,                                                 /* tp_as_sequence */
    0,                                                 /* tp_as_mapping */
    0,                                                 /* tp_hash */
    0,                                                 /* tp_call */
    0,                                                 /* tp_str */
    PyObject_GenericGetAttr,                           /* tp_getattro */
    0,                                                 /* tp_setattro */
    0,                                                 /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,           /* tp_flags */
    namedtuple_descr_wrapper_doc,                      /* tp_doc */
    (traverseproc) namedtuple_descr_wrapper_traverse,  /* tp_traverse */
    (inquiry) namedtuple_descr_wrapper_clear,          /* tp_clear */
    0,                                                 /* tp_richcompare */
    0,                                                 /* tp_weaklistoffset */
    0,                                                 /* tp_iter */
    0,                                                 /* tp_iternext */
    0,                                                 /* tp_methods */
    0,                                                 /* tp_members */
    0,                                                 /* tp_getset */
    0,                                                 /* tp_base */
    0,                                                 /* tp_dict */
    namedtuple_descr_wrapper_get,                      /* tp_descr_get */
    0,                                                 /* tp_descr_set */
    0,                                                 /* tp_dictoffset */
    0,                                                 /* tp_init */
    0,                                                 /* tp_alloc */
    0,                                                 /* tp_new */
};

/* Gets the `_fields` off a namedtuple. Raises a `TypeError` error if this is
   not a tuple.
   return: A new reference or NULL */
static PyObject *
get_fields(PyObject *self) {
    PyObject *fields;

    if (!(fields = PyObject_GetAttrString((PyObject*) self, "_fields"))) {
        return NULL;
    }

    if (!(PyTuple_CheckExact(fields))) {
        PyErr_SetString(PyExc_TypeError,
                        "_fields must be a tuple of fieldnames.");
        Py_DECREF(fields);
        return NULL;
    }

    return fields;
}

/* `__new__` for namedtuple types. This will reflect it's argument list
   off `cls`.
   return: A new instance of a namedtuple or NULL in case of error. */
static PyObject *
namedtuple_new(PyTypeObject *cls, PyObject *args, PyObject *kwargs)
{
    PyObject  *self;
    PyObject  *fields;
    Py_ssize_t fieldc;
    PyObject  *keyword;
    Py_ssize_t n;
    Py_ssize_t pos;
    Py_ssize_t nargs;
    Py_ssize_t nkwargs;
    PyObject  *current_arg;
    int        match;
    PyObject  *key;
    PyObject  *value;

    if (!(fields = get_fields((PyObject*) cls))) {
        return NULL;
    }
    fieldc = PyTuple_GET_SIZE(fields);

    nargs = PyTuple_GET_SIZE(args);
    nkwargs = (kwargs) ? PyDict_Size(kwargs) : 0;
    if (nargs + nkwargs > BUFSIZ) {
        PyErr_Format(PyExc_TypeError,
                     "Cannot pass more than %d arguments to %U",
                     BUFSIZ,
                     ((PyHeapTypeObject*) cls)->ht_name);
        return NULL;
    }

    if (!(self = PyTuple_Type.tp_alloc(cls, fieldc))) {
        return NULL;
    }

    // Custom argument parsing because of dynamic construction.
    if (nargs + nkwargs > fieldc) {
        PyErr_Format(PyExc_TypeError,
                     "%U takes at most %zd argument%s (%zd given)",
                     ((PyHeapTypeObject*) cls)->ht_name,
                     fieldc,
                     (fieldc == 1) ? "" : "s",
                     nargs + nkwargs);
        PyTuple_Type.tp_dealloc(self);
        return NULL;
    }

    for (n = 0;n < fieldc;n++) {
        keyword = PyTuple_GET_ITEM(fields, n);
        current_arg = NULL;
        if (nkwargs) {
            current_arg = PyDict_GetItem(kwargs,keyword);
        }
        if (current_arg) {
            --nkwargs;
            if (n < nargs) {
                /* Arg present in tuple and in dict. */
                PyErr_Format(PyExc_TypeError,
                             "Argument given by name ('%U') and position (%zd)",
                             keyword,
                             n + 1);
                PyTuple_Type.tp_dealloc(self);
                return NULL;
            }
        }
        else if (nkwargs && PyErr_Occurred()) {
            PyTuple_Type.tp_dealloc(self);
            return NULL;
        }
        else if (n < nargs) {
            current_arg = PyTuple_GET_ITEM(args,n);
        }

        if (current_arg) {
            /* This reference is stolen when we store it in self. */
            Py_INCREF(current_arg);
            PyTuple_SET_ITEM((PyTupleObject*) self, n, current_arg);
            continue;
        }

        if (n < fieldc) {
            PyErr_Format(PyExc_TypeError,
                         "Required argument '%U' (pos %zd) not found",
                         keyword,
                         n + 1);
            PyTuple_Type.tp_dealloc(self);
            return NULL;
        }
    }

    /* Check for extra kwargs. */
    if (nkwargs > 0) {
        pos = 0;
        while (PyDict_Next(kwargs, &pos, &key, &value)) {
            if (!PyUnicode_Check(key)) {
                PyErr_SetString(PyExc_TypeError,
                                "keywords must be strings");
                PyTuple_Type.tp_dealloc(self);
                return NULL;
            }
            for (n = 0;n < fieldc;++n) {
                if (!PyUnicode_Compare(key, PyTuple_GET_ITEM(fields, n))) {
                    match = 1;
                    break;
                }
            }
            if (!match) {
                PyErr_Format(PyExc_TypeError,
                             "'%U' is an invalid keyword argument for this "
                             "function",
                             key);
                PyTuple_Type.tp_dealloc(self);
                return NULL;
            }
        }
    }

    return self;
}

/* Namedtuple class method for creating new instances from an iterable.
   return `PyObject*` representing the new instance, or NULL to signal an
   error. */
static PyObject *
namedtuple__make(PyObject *cls, PyObject *args, PyObject *kwargs)
{
    const char * const argnames[] = {"iterable", NULL};
    PyObject *iterable;
    PyObject *ret;

    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "O:_make",
                                     (char**) argnames,
                                     &iterable)) {
        return NULL;
    }

    if (!(iterable = PySequence_Tuple(iterable))) {
      PyErr_SetString(PyExc_ValueError, "iterable must be a sequence");
      return NULL;
    }

    ret = ((PyTypeObject*) cls)->tp_new((PyTypeObject*) cls, iterable, NULL);
    Py_DECREF(iterable);
    return ret;
}

/* return:  new instance of `type(self)` with the kwargs
   swapped out. On failure, returns NULL. */
static PyObject *
namedtuple__replace(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *items;
    PyObject *item;
    PyObject *ret;
    PyObject *tstr;
    PyObject *tkeys;
    PyObject *ttuple;
    PyObject *errstr;
    Py_ssize_t n;
    PyObject *fields;
    Py_ssize_t fieldc;

    if (!(fields = get_fields(self))) {
        return NULL;
    }
    fieldc = PyTuple_GET_SIZE(fields);

    if (PyTuple_GET_SIZE(args)) {
        /* No positional arguments allowed. */
        PyErr_Format(PyExc_TypeError,
                     "_replace takes no positional arguments (%zd given)",
                     PyTuple_GET_SIZE(args));
        return NULL;
    }

    if (!kwargs) {
        /* Fast path if nothing needs to be replaced, just copy. */
        return namedtuple__make((PyObject*) self->ob_type,
                                Py_BuildValue("(N)", self),
                                NULL);
    }

    if (!(items = PyTuple_New(fieldc))) {
        return NULL;
    }

    for (n = 0;n < fieldc;++n) {
        if (!(item = PyDict_GetItem(kwargs, PyTuple_GET_ITEM(fields, n)))) {
            item = PyTuple_GET_ITEM(self, n);
        }
        else {
            PyDict_DelItem(kwargs,PyTuple_GET_ITEM(fields, n));
        }

        Py_INCREF(item);
        PyTuple_SET_ITEM(items, n, item);
    }

    if (PyDict_Size(kwargs)) {
        tstr = PyUnicode_FromString("Got unexpected field names: %r");
        tkeys = PyDict_Keys(kwargs);
        ttuple = PyTuple_Pack(1, tkeys);
        Py_DECREF(tstr);
        Py_DECREF(tkeys);
        errstr = PyUnicode_Format(tstr, ttuple);
        Py_DECREF(ttuple);
        PyErr_SetObject(PyExc_ValueError, errstr);
        return NULL;
    }

    ret = namedtuple__make((PyObject*) self->ob_type,
                           Py_BuildValue("(N)", items),
                           NULL);
    Py_DECREF(items);
    return ret;
}

/* The `__repr__` for `namedtuple` objects.
   return: A str in the format `{typename}({f_1}={v_1}, ..., {f_n}={v_n})`
   or NULL in case of an exception. */
static PyObject *
namedtuple_repr(PyObject *self, PyObject *_)
{
    PyObject *reprfmt;
    Py_ssize_t len;
    Py_ssize_t n;
    PyObject *field;
    PyObject *args;
    PyObject *ret;

    if (!(reprfmt = PyObject_GetAttrString(self, "__reprfmt__"))) {
        return NULL;
    }

    if (!PyUnicode_CheckExact(reprfmt)) {
        PyErr_SetString(PyExc_TypeError,
                        "__reprfmt__ must be an instance of 'str'");
        Py_DECREF(reprfmt);
        return NULL;
    }

    len = PyTuple_GET_SIZE(self);
    if (!(args = PyTuple_New(len + 1))) {
        return NULL;
    }

    PyTuple_SET_ITEM(args, 0, ((PyHeapTypeObject*) self->ob_type)->ht_name);
    Py_INCREF(((PyHeapTypeObject*) self->ob_type)->ht_name);

    for (n = 1;n < len + 1;++n) {
        field = PyTuple_GET_ITEM(self, n - 1);
        Py_INCREF(field);
        PyTuple_SET_ITEM(args, n, field);
    }

    ret = PyUnicode_Format(reprfmt, args);
    Py_DECREF(args);
    return ret;
}

/* Converts self into a dict.
   return: A new dict or NULL in case of error. */
PyObject *
namedtuple__asdict(PyObject *self, PyObject *_)
{
    Py_ssize_t n;
    PyObject *fields;
    Py_ssize_t fieldc;
    PyObject *args;
    PyObject *ret;
    PyObject *asdict;

    if (!(fields = get_fields(self))) {
        return NULL;
    }
    fieldc = PyTuple_GET_SIZE(fields);

    if (!(args = PyTuple_New(fieldc))) {
        return NULL;
    }
    for (n = 0;n < fieldc;++n) {
        if (!(ret = PyTuple_Pack(2,
                                 PyTuple_GET_ITEM(fields, n),
                                 PyTuple_GET_ITEM(self, n)))) {
            Py_DECREF(args);
            return NULL;
        }
        PyTuple_SET_ITEM(args, n, ret);
    }

    if (!(asdict = PyObject_GetAttrString(self, "__asdict__"))) {
        Py_DECREF(args);
        return NULL;
    }

    ret = PyObject_CallFunctionObjArgs(asdict, args, NULL);
    Py_DECREF(args);
    return ret;
}

/* Pickle and copy protocol.
   return: self as a plain tuple or NULL in case of error. */
static PyObject *
namedtuple_getnewargs(PyObject *self, PyObject *_)
{
    return PySequence_Tuple(self);
}

/* Pass function for the pickle and copy protocol.
   return: Py_None. */
static PyObject *
namedtuple_getstate(PyObject *self, PyObject *_)
{
    Py_RETURN_NONE;
}

/* Pickle protocol for extension types.
   return: A tuple `(type(self),tuple(self))` or NULL in case of an error. */
static PyObject *
namedtuple_reduce_ex(PyObject *self,PyObject *_)
{
    PyObject *astuple = PySequence_Tuple(self);

    if (!astuple) {
        return NULL;
    }

    return PyTuple_Pack(2, self->ob_type, astuple);
}

static int
namedtuple_traverse(PyTupleObject *self, visitproc visit, void *arg)
{
    Py_ssize_t n;

    for (n = PyTuple_GET_SIZE(self);--n >= 0;) {
        Py_VISIT(PyTuple_GET_ITEM(self, n));
    }
    return 0;
}

/* The `__dict__` of namedtuple types is the `__asdict__` type holding all
   of the fields.
   return: A new dict or NULL in case of error. */
static PyObject *
namedtuple_get_dict(PyObject *self, void *_)
{
    PyObject *asdict = PyObject_GetAttrString(self, "__asdict__");
    Py_ssize_t n;
    PyObject *fields;
    Py_ssize_t fieldc;
    PyObject *arg;
    PyObject *tmp;

    if (!asdict) {
        return NULL;
    }

    if (!(fields = get_fields(self))) {
        return NULL;
    }

    fieldc = PyTuple_GET_SIZE(fields);
    if (!(arg = PyTuple_New(fieldc))) {
        Py_DECREF(fields);
        return NULL;
    }

    /* Construct an assoc list of ((field . value)) to pass to
       the `__asdict__` constructor. */
    for (n = 0;n < fieldc;++n) {
        if (!(tmp = PyTuple_Pack(2,
                                 PyTuple_GET_ITEM(fields, n),
                                 PyTuple_GET_ITEM(self, n)))) {
            Py_DECREF(arg);
            Py_DECREF(fields);
            return NULL;
        }

        PyTuple_SET_ITEM(arg, n, tmp);
    }

    tmp = PyObject_CallFunctionObjArgs(asdict, arg, NULL);
    Py_DECREF(arg);
    Py_DECREF(fields);
    return tmp;
}

PyDoc_STRVAR(_make_doc,
"_make(iterable) -> namedtuple\n\n"
"Create an instance of this class from an iterable.");

PyDoc_STRVAR(_replace_doc,
"_replace(field=new_value, ...) -> new namedtuple\n\n"
"Returns a new namedtuple with the specified fields replaced.");

PyDoc_STRVAR(_asdict_doc,
"_asdict() -> dict\n\n"
"Converts this namedtuple into a dictionary that maps fields to values");

PyDoc_STRVAR(__getnewargs___doc,
"__getnewargs__() -> tuple\n\n"
"Return self as a plain tuple. Used by copy and pickle.");

PyDoc_STRVAR(__getstate___doc,
"__getstate__() -> None\n\n"
"Exclude the OrderedDict from pickling.");

PyDoc_STRVAR(__reduce_ex___doc,
"__reduce_ex__() -> (type(self), tuple(self))\n\n"
"Returns the pair of the type of the instance with the instance cast to\n"
"a tuple.");

PyMethodDef namedtuple_methods[] = {
    {"_make",
     (PyCFunction) namedtuple__make,
     METH_CLASS | METH_VARARGS | METH_KEYWORDS,
     _make_doc},
    {"_replace",
     (PyCFunction) namedtuple__replace,
     METH_VARARGS | METH_KEYWORDS,
     _replace_doc},
    {"_asdict",
     (PyCFunction) namedtuple__asdict,
     METH_NOARGS,
     _asdict_doc},
    {"__getnewargs__",
     (PyCFunction) namedtuple_getnewargs,
     METH_NOARGS,
     __getnewargs___doc},
    {"__getstate__",
     namedtuple_getstate,
     METH_NOARGS,
     __getstate___doc},
    {"__reduce_ex__",
     namedtuple_reduce_ex,
     METH_O,
     __reduce_ex___doc},
    {NULL},
};

/* Construct the `fields` tuple from the input `field_names`. */
static PyObject *
build_fields(PyObject *field_names)
{
    PyObject  *tmp_fields;
    PyObject  *fast_fields;
    PyObject  *fields;
    PyObject  *with_replace;
    PyObject  *as_str;
    PyObject  *comma;
    PyObject  *space;
    Py_ssize_t n;
    Py_ssize_t len;

    /* If the `field_names` is a `str`, then we will replace all ',' with ' '
       and then split it on whitespace to get the sequence of fields. */
    if (PyUnicode_Check(field_names)) {
         comma = PyUnicode_InternFromString(",");
         space = PyUnicode_InternFromString(" ");

         /* Replace all instances of ',' with ' '. */
        with_replace = PyUnicode_Replace(field_names, comma, space, -1);
        Py_DECREF(comma);
        Py_DECREF(space);

        if (!with_replace) {
            return NULL;
        }

        // Split the field names into a tuple around all whitespace.
        tmp_fields = PyUnicode_Split(with_replace, NULL, -1);
        Py_DECREF(with_replace);

        if (!tmp_fields) {
            return NULL;
        }
    }
    else {
        /* The `field_names` is a sequence already, just convert it into a
           tuple. */
        tmp_fields = PySequence_Tuple(field_names);
    }

    fast_fields = PySequence_Fast(tmp_fields, "field_names must be a sequence");
    Py_DECREF(tmp_fields);
    if (!fast_fields) {
        return NULL;
    }
    len = PySequence_Fast_GET_SIZE(fast_fields);
    fields = PyTuple_New(len);

    for (n = 0;n < len;++n) {
        if (!(as_str =
              PyObject_Str(PySequence_Fast_GET_ITEM(fast_fields, n)))) {
            Py_DECREF(tmp_fields);
            Py_DECREF(fields);
            return NULL;
        }
        PyTuple_SET_ITEM(fields, n, as_str);
    }

    Py_DECREF(tmp_fields);
    return fields;
}

/* A type to indicate the results of checking a field or type name */
typedef enum{
    CHECKFIELD_VALID      = 0,
    CHECKFIELD_EMPTY      = 1,
    CHECKFIELD_DIGIT      = 2,
    CHECKFIELD_UNDERSCORE = 3,
    CHECKFIELD_NONALNUM   = 4,
    CHECKFIELD_KEYWORD    = 5,
    CHECKFIELD_NOTREADY   = 6,
}nt_checkfield;

/* Checks the field against the various rules for invalid names.
   return: An `nt_checkfield` indicating the result. */
static nt_checkfield
checkfield(PyObject *iskeyword, PyObject *field)
{
    void      *data;
    int        kind;
    Py_UCS4    ch;
    Py_ssize_t idx;
    PyObject  *iskwd_obj;
    int        iskwd;

    if (PyUnicode_READY(field)) {
        return CHECKFIELD_NOTREADY;
    }

    if (!PyUnicode_GET_LENGTH(field)) {
        /* Empty name. */
        return CHECKFIELD_EMPTY;
    }

    kind = PyUnicode_KIND(field);
    data = PyUnicode_DATA(field);

    ch = PyUnicode_READ(kind,data,0);

    if (Py_UNICODE_ISDIGIT(ch)) {
        /* Cannot start with digit. */
        return CHECKFIELD_DIGIT;
    }
    else if (ch == (Py_UCS4) '_') {
        /* Cannot start with '_'. */
        return CHECKFIELD_UNDERSCORE;
    }

    idx = PyUnicode_GET_LENGTH(field);
    while (--idx) {
        ch = PyUnicode_READ(kind, data, idx);
        if (!(Py_UNICODE_ISALNUM(ch) || ch == (Py_UCS4) '_')) {
            /* Must be all alphanumeric characters or underscores. */
            return CHECKFIELD_NONALNUM;
        }
    }


    iskwd = ((iskwd_obj = PyObject_CallFunctionObjArgs(iskeyword,
                                                       field,
                                                       NULL)) &&
             PyObject_IsTrue(iskwd_obj));
    Py_XDECREF(iskwd_obj);

    if (iskwd) {
        return CHECKFIELD_KEYWORD;
    }

    return CHECKFIELD_VALID;
}

/* Rename the `field_names` if they fail the various checks. This mutates
   `fields` in place.
   return: Zero on succes, nonzero on failure */
static int
rename_fields(PyObject *iskeyword, PyObject *fields)
{
    PyObject *seen;
    PyObject *field;
    Py_ssize_t fieldc = PyTuple_GET_SIZE(fields);
    Py_ssize_t n;
    int rename;

    if (!(seen = PySet_New(NULL))) {
        return -1;
    }

    /* Iterate over the fields, applying any renames if needed. */
    for (n = 0;n < fieldc;++n) {
        rename = 0;
        field = PyTuple_GET_ITEM(fields, n);

        if (checkfield(iskeyword, field)
            != CHECKFIELD_VALID) {
            // Invalid name for some reason.
            rename = 1;
        }
        else {
            /* Check if the name is in the set of seen names. */
            switch(PySet_Contains(seen, field)) {
            case 1:
                rename = 1;
                break;
            case -1:
                Py_DECREF(seen);
                return -1;
            }
        }

        if (rename) {
            Py_DECREF(field);

            if (!(field = PyUnicode_FromFormat("_%zu", n))) {
                PyTuple_SET_ITEM(fields, n, NULL);
                Py_DECREF(seen);
                return -1;
            }
            PyTuple_SET_ITEM(fields, n, field);
        }

        /* Add the name to the set of seen names. */
        if (PySet_Add(seen, field)) {
            return -1;
        }
    }

    Py_DECREF(seen);
    return 0;
}

/* Process the `typename` and `field_names` for a `namedtuple`.
   After this function is called (and no errors occur),
   `field_names` will point to a new reference to a tuple of field names
   that have been properly renamed and checked.
   return: Zero on succes, nonzero on failure. */
static int
validate_field_names(PyObject *typename,
                     PyObject **field_names,
                     int rename,
                     PyObject *iskeyword)
{
    const char * const nonalnum_fmt =
        "Type names and field names can only contain alphanumeric characters "
        "and underscores: %U";
    const char * const keyword_fmt =
        "Type names and field names cannot be a keyword: %U";
    const char * const digit_fmt = "Type names and field names cannot start "
        "with a number: %U";
    const char * const underscore_fmt =
        "Field names cannot start with an underscore: %U";
    const char * const empty_type_fmt = "Type names cannot be empty";
    const char * const empty_field_fmt =
        "Field names cannot be empty (index %zd)";
    const char * const seen_fmt = "Encountered duplicate field name: %U";
    const char * const notready_fmt = "name was not ready";
    PyObject *fields;
    PyObject *field;
    Py_ssize_t fieldc;
    Py_ssize_t n;
    PyObject *seen;

    if (!(fields = build_fields(*field_names))) {
        return -1;
    }

    if (rename_fields(iskeyword, fields)) {
        return -1;
    }

    switch(checkfield(iskeyword, typename)) {
    case CHECKFIELD_UNDERSCORE:  /* typenames may begin with '_'. */
    case CHECKFIELD_VALID:
        break;
    case CHECKFIELD_NONALNUM:
        PyErr_Format(PyExc_ValueError,nonalnum_fmt,typename);
        return -1;
    case CHECKFIELD_KEYWORD:
        PyErr_Format(PyExc_ValueError,keyword_fmt,typename);
        return -1;
    case CHECKFIELD_DIGIT:
        PyErr_Format(PyExc_ValueError,digit_fmt,typename);
        return -1;
    case CHECKFIELD_EMPTY:
        PyErr_SetString(PyExc_ValueError,empty_type_fmt);
        return -1;
    case CHECKFIELD_NOTREADY:
        PyErr_SetString(PyExc_ValueError,notready_fmt);
        return -1;
    }

    if (!(seen = PySet_New(NULL))) {
        return 1;
    }

    fieldc = PyTuple_GET_SIZE(fields);
    for (n = 0;n < fieldc;++n) {
        field = PyTuple_GET_ITEM(fields, n);

        switch(checkfield(iskeyword, field)) {
        case CHECKFIELD_VALID:
            break;
        case CHECKFIELD_UNDERSCORE:
            if (!rename) {
                PyErr_Format(PyExc_ValueError, underscore_fmt, field);
                return -1;
            }
            break;
        case CHECKFIELD_NONALNUM:
            PyErr_Format(PyExc_ValueError, nonalnum_fmt, field);
            Py_DECREF(seen);
            return -1;
        case CHECKFIELD_KEYWORD:
            PyErr_Format(PyExc_ValueError, keyword_fmt, field);
            Py_DECREF(seen);
            return -1;
        case CHECKFIELD_DIGIT:
            PyErr_Format(PyExc_ValueError, digit_fmt, field);
            Py_DECREF(seen);
            return -1;
        case CHECKFIELD_EMPTY:
            PyErr_Format(PyExc_ValueError, empty_field_fmt, n);
            return -1;
        case CHECKFIELD_NOTREADY:
            PyErr_SetString(PyExc_ValueError, notready_fmt);
            return -1;
        }

        switch(PySet_Contains(seen, field)) {
        case 1:
            PyErr_Format(PyExc_ValueError, seen_fmt, field);
            Py_DECREF(seen);
            return -1;
        case -1:
            Py_DECREF(seen);
            return -1;
        }

        if (PySet_Add(seen, field)) {
            Py_DECREF(seen);
            return -1;
        }
    }

    Py_DECREF(seen);
    *field_names = fields;
    return 0;
}

/* Adds a `namedtuple_indexer` for each field in `fields`.
   return: Zero on succes, nonzero on failure. */
static int
add_indexers(PyObject *dict_, PyObject *fields)
{
    Py_ssize_t fieldc = PyTuple_GET_SIZE(fields);
    Py_ssize_t n;
    namedtuple_indexer *indexer;

    for (n = 0;n < fieldc;++n) {
        if (!(indexer = PyObject_New(namedtuple_indexer,
                                     &namedtuple_indexer_type))) {
            return -1;
        }

        indexer->id_idx = n;
        if (PyDict_SetItem(dict_,
                           PyTuple_GET_ITEM(fields, n),
                           (PyObject*) indexer)) {
            return -1;
        }
        Py_DECREF(indexer);
    }

    return 0;
}

/* Cache the repr format string so we don't need to do this every time we call
   `namedtuple_repr`.
   return: Zero on succes, nonzero on failure. */
// Cache the repr format string.
// return: zero on success, nonzero on failure.
static int
cache_repr_fmt(PyObject *dict_, PyObject *fields)
{
    Py_ssize_t fieldc = PyTuple_GET_SIZE(fields);
    PyObject *field_fmts;
    PyObject *sep;
    PyObject *joined;
    Py_ssize_t n;
    PyObject *field_fmt;
    PyObject *reprfmt = NULL;
    int ret;

    /* Allocate a tuple strings representing each field's format, */
    if (!(field_fmts = PyTuple_New(fieldc))) {
        return -1;
    }


    for (n = 0;n < fieldc;++n) {
        if (!(field_fmt = PyUnicode_FromFormat("%U=%%r",
                                               PyTuple_GET_ITEM(fields, n)))) {
            Py_DECREF(field_fmts);
            return -1;
        }
        PyTuple_SET_ITEM(field_fmts, n, field_fmt);
    }

    if (!(sep = PyUnicode_FromString(", "))) {
        Py_DECREF(field_fmts);
        return -1;
    }
    joined = PyUnicode_Join(sep, field_fmts);
    Py_DECREF(sep);
    Py_DECREF(field_fmts);
    if (!joined) {
        return -1;
    }
    reprfmt = PyUnicode_FromFormat("%%s(%U)", joined);
    Py_DECREF(joined);
    if (!reprfmt) {
        return -1;
    }

    ret = PyDict_SetItemString(dict_, "__reprfmt__", reprfmt);
    Py_DECREF(reprfmt);
    return ret;
}

PyGetSetDef namedtuple_getsets[] = {
    {"__dict__",
     namedtuple_get_dict,
     NULL,
     NULL},
    {NULL},
};

PyType_Slot namedtuple_slots[] = {
    {Py_tp_new,
     namedtuple_new},
    {Py_tp_methods,
     namedtuple_methods},
    {Py_tp_repr,
     namedtuple_repr},
    {Py_tp_traverse,
     namedtuple_traverse},
    {Py_tp_getset,
     namedtuple_getsets},
    {0, NULL},
};

PyType_Spec namedtuple_spec = {
    "",  /* placeholder */
    0,
    0,
    Py_TPFLAGS_HAVE_GC
    | Py_TPFLAGS_TUPLE_SUBCLASS
    | Py_TPFLAGS_HEAPTYPE
    | Py_TPFLAGS_BASETYPE
    | Py_TPFLAGS_DEFAULT,
    namedtuple_slots,
};

_Py_IDENTIFIER(__module__);

/* namedtuple factory function.
 * return: A new reference to a new namedtuple type or NULL on failure. */
static PyObject *
namedtuple_factory(PyObject *self,PyObject *args,PyObject *kwargs)
{
    const char *const argnames[] = {
        "typename",
        "field_names",
        "rename",
        NULL,
    };
    module_state *st = PyModule_GetState(self);
    PyObject *typename = NULL;
    PyObject *field_names = NULL;
    int rename = NULL;
    PyTypeObject *newtype;
    PyObject *globals;
    PyObject *module_name;
    namedtuple_descr_wrapper *descr;
    PyObject *bases;
    PyObject *dict_;
    int err;

    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "OO|p:namedtuple",
                                     (char**) argnames,
                                     &typename,
                                     &field_names,
                                     &rename)) {
        return NULL;
    }

    if (!(typename = PyObject_Str(typename))) {
        /* Typename cannot be converted to `str`. */
        return NULL;
    }

    /* Validate and rename the `typename` and `field_names`. After this
     * function, field_names` will point to a tuple of strings that is the
     * split and renamed fields (if there are no errors). */
    if (validate_field_names(typename, &field_names, rename, st->iskeyword)) {
        /* Invalid `field_names` or `typename`. */
        Py_DECREF(typename);
        return NULL;
    }

    bases = PyTuple_Pack(1, &PyTuple_Type);
    namedtuple_spec.name = PyUnicode_AsUTF8(typename);
    newtype = (PyTypeObject*) PyType_FromSpecWithBases(&namedtuple_spec, bases);
    Py_DECREF(typename);
    if (!newtype) {
        return NULL;
    }

    dict_ = newtype->tp_dict;

    /* Add indexers for each name. */
    if (add_indexers(dict_, field_names)) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
        return NULL;
    }

    /* Add the field descriptor. */
    if (!(descr = PyObject_GC_New(namedtuple_descr_wrapper,
                                  &namedtuple_descr_wrapper_type))) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
        return NULL;
    }
    descr->wr_wrapped = field_names;
    if (PyDict_SetItemString(dict_, "_fields", (PyObject*) descr)) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
        return NULL;
    }
    Py_DECREF(descr);

    /* Add an empty '__slots__' */
    if (!(descr = PyObject_GC_New(namedtuple_descr_wrapper,
                                         &namedtuple_descr_wrapper_type))) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
        return NULL;
    }
    if (!(descr->wr_wrapped = PyTuple_New(0))) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
        return NULL;
    }
    if (PyDict_SetItemString(dict_, "__slots__", (PyObject*) descr)) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
        return NULL;
    }
    Py_DECREF(descr);

    /* Add the `__reprfmt__` and `tp_doc`.*/
    if (cache_repr_fmt(dict_, field_names)) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
        return NULL;
    }

    /* set the asdict constructor */
    if (PyDict_SetItemString(dict_, "__asdict__", st->asdict)) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
        return NULL;
    }

    /* Lookup the module where this type was defined and store it as
       `__module__` in the dict */
    if ((globals = PyEval_GetGlobals()) &&
        (module_name = PyDict_GetItemString(globals, "__name__"))) {
        Py_INCREF(module_name);
    }
    else {
        /* Default to an empty string. */
        module_name = PyUnicode_InternFromString("");
    }
    /* Replace the `__module__` with the actual module. */
    err = _PyDict_SetItemId(dict_, &PyId___module__, module_name);
    Py_DECREF(module_name);
    if (err) {
        PyType_Type.tp_dealloc((PyObject*) newtype);
    }

    return (PyObject*) newtype;
}

static PyObject *
_register_asdict(PyObject *self, PyObject *asdict)
{
    module_state *st = PyModule_GetState(self);

    Py_DECREF(st->asdict);
    Py_INCREF(asdict);
    st->asdict = asdict;

    Py_RETURN_NONE;
}

PyDoc_STRVAR(namedtuple_doc,
"Returns a new subclass of tuple with named fields.\n"
"\n"
"    >>> Point = namedtuple('Point', ['x', 'y'])\n"
"    'Point(x, y)'\n"
"    >>> p = Point(11, y=22)  # instantiate with positional args or keywords\n"
"    >>> p[0] + p[1]          # indexable like a plain tuple\n"
"    33\n"
"    >>> x, y = p             # unpack like a regular tuple\n"
"    >>> x, y\n"
"    (11, 22)\n"
"    >>> p.x + p.y            # fields also accessable by name\n"
"    33\n"
"    >>> d = p._asdict()      # convert to a dictionary\n"
"    >>> d['x']\n"
"    11\n"
"    >>> Point(**d)           # convert from a dictionary\n"
"    Point(x=11, y=22)\n"
"    >>> p._replace(x=100)    # _replace() is like str.replace() but targets named fields\n"
"    Point(x=100, y=22)\n");

PyDoc_STRVAR(_register_asdict_doc,
"_register_asdict(type) -> None\n\n"
"Register the type constructor to use in the '_asdict' method for nametuple.\n"
"This is part of the internal api to solve circular dependencies.");


// The module level methods for the `namedtuple` module.
PyMethodDef _namedtuple_methods[] = {
    {.ml_name="namedtuple",
     .ml_meth=(PyCFunction) namedtuple_factory,
     .ml_flags=METH_VARARGS | METH_KEYWORDS,
     .ml_doc=namedtuple_doc},
    {.ml_name="_register_asdict",
     .ml_meth=_register_asdict,
     .ml_flags=METH_O,
     .ml_doc=_register_asdict_doc},
    {NULL},
};

static int
module_traverse(PyObject *self,visitproc visit,void *arg)
{
    module_state *st = PyModule_GetState(self);

    if (!st) {
        return 1;
    }
    Py_VISIT(st->asdict);
    return 0;
}

static int
module_clear(PyObject *self) {
    module_state *st = PyModule_GetState(self);

    if (!st) {
        return 1;
    }
    Py_CLEAR(st->asdict);
    return 0;
}

PyDoc_STRVAR(module_doc,
"High performance data structures.\n\
- namedtuple:   A factory for creating subclasses of tuple that can be \
indexed by name\n\
");

static struct PyMethodDef module_functions[] = {
    {.ml_name="namedtuple",
     .ml_meth=(PyCFunction) namedtuple_factory,
     .ml_flags=METH_VARARGS | METH_KEYWORDS,
     .ml_doc=namedtuple_doc},
    {.ml_name="_register_asdict",
     .ml_meth=_register_asdict,
     .ml_flags=METH_O,
     .ml_doc=_register_asdict_doc},
    {NULL},
};

static struct PyModuleDef _namedtuplemodule = {
    PyModuleDef_HEAD_INIT,
    "_namedtuple",
    module_doc,
    sizeof(module_state),
    module_functions,
    NULL,
    module_traverse,
    module_clear,
    NULL
};

PyMODINIT_FUNC
PyInit__namedtuple(void)
{
    PyObject *m;
    PyObject *keyword_mod;
    module_state *st;

    m = PyModule_Create(&_namedtuplemodule);
    if (m == NULL) {
        return NULL;
    }
    if (!(st = PyModule_GetState(m))) {
        PyErr_SetString(PyExc_SystemError,"Module state is NULL");
        return NULL;
    }

    if (PyType_Ready(&namedtuple_indexer_type) < 0)
        return NULL;

    if (PyType_Ready(&namedtuple_descr_wrapper_type) < 0)
        return NULL;

    st->asdict = (PyObject*) &PyDict_Type;
    Py_INCREF(st->asdict);

    if (!(keyword_mod = PyImport_ImportModule("keyword"))) {
        Py_DECREF(m);
        return NULL;
    }
    st->iskeyword = PyObject_GetAttrString(keyword_mod, "iskeyword");
    Py_DECREF(keyword_mod);
    if (!st->iskeyword) {
        Py_DECREF(m);
        return NULL;
    }

    return m;
}

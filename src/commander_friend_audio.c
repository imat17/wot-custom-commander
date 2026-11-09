/* Small Python 2.7 x64 binding. No ctypes, subprocess, or game memory hooks. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmsystem.h>
#include <Python.h>

static PyObject *play_sound(PyObject *self, PyObject *args)
{
    PyObject *path, *unused;
    unsigned int flags;
    const wchar_t *filename = NULL;
    if (!PyArg_ParseTuple(args, "OOI", &path, &unused, &flags))
        return NULL;
    if (path != Py_None) {
        if (!PyUnicode_Check(path)) {
            PyErr_SetString(PyExc_TypeError, "Expected a Unicode WAV path or None");
            return NULL;
        }
        filename = PyUnicode_AsUnicode(path);
        if (!filename) return NULL;
        /* Only asynchronous file playback is exposed; never memory/resource audio. */
        flags = SND_FILENAME | SND_ASYNC | SND_NODEFAULT;
    } else {
        flags = 0;
    }
    return PyBool_FromLong(PlaySoundW(filename, NULL, flags) != FALSE);
}

static PyMethodDef methods[] = {
    {"play_sound", play_sound, METH_VARARGS, "Play one WAV asynchronously, or stop with None."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initcommander_friend_audio(void)
{
    Py_InitModule3("commander_friend_audio", methods, "Commander Friend Windows audio");
}

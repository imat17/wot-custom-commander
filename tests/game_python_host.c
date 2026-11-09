/* Isolated test host: load the copied game Python DLL, never the game process. */
#include <Python.h>
#include <stdio.h>
int main(int argc, char **argv)
{
    int result;
    if (argc != 3) return 2;
    Py_SetPythonHome(argv[1]);
    Py_Initialize();
    PySys_SetArgv(1, argv + 2);
    result = PyRun_SimpleString("import runpy, sys; runpy.run_path(sys.argv[0], run_name='__main__')");
    Py_Finalize();
    return result == 0 ? 0 : 1;
}

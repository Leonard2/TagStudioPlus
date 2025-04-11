#include <filesystem>

#include <stdlib.h>

#include "Python.h"

const char *script = "import tagstudio.main\n"
                     "tagstudio.main.main()";


PyMODINIT_FUNC PyInit_TSPlus()
{
    static PyModuleDef TagStudioPlus =
    {
        PyModuleDef_HEAD_INIT,
        "tagstudioplus",
        nullptr,
        -1,
        nullptr,
        nullptr,
        nullptr,
        nullptr,
        nullptr
    };

    return PyModule_Create(&TagStudioPlus);
}

int main(int argc, char *argv[])
{
    auto dir = std::filesystem::weakly_canonical(std::filesystem::path(argv[0])).parent_path();
    putenv(std::format("PYTHONHOME={}", dir.string()).c_str());
    dir = dir / "_internal";
    putenv(std::format("PYTHONPATH={}", dir.string()).c_str());

    if (PyImport_AppendInittab("tagstudioplus", PyInit_TSPlus) < 0)
    {
        if (PyErr_Occurred())
            PyErr_Print();
        return 1;
    }

    Py_Initialize();
    if (PyErr_Occurred())
    {
        PyErr_Print();
        return 1;
    }

    auto module = PyImport_ImportModule("tagstudioplus");
    if (!module)
    {
        if (PyErr_Occurred())
            PyErr_Print();
        return 1;
    }

    auto swtch = PyBool_FromLong(1);
    if (PyModule_AddObject(module, "cppswitch", swtch) < 0)
    {
        if (PyErr_Occurred())
            PyErr_Print();
        return -1;
    }

    return PyRun_SimpleString(script);
}

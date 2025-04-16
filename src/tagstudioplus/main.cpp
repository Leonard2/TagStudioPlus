#include <filesystem>

#include <stdlib.h>

#include "tagstudioplus_python.h"
extern "C" PyObject *PyInit_tagstudioplus();

const char *script = "import tagstudio.main\n"
                     "tagstudio.main.main()";


int main(int argc, char *argv[])
{
    auto dir = std::filesystem::weakly_canonical(std::filesystem::path(argv[0])).parent_path();
    putenv(std::format("PYTHONHOME={}", dir.string()).c_str());
    dir = dir / "_internal";
    putenv(std::format("PYTHONPATH={}", dir.string()).c_str());

    if (PyImport_AppendInittab("tagstudioplus", PyInit_tagstudioplus) < 0)
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

    cppswitch swtch;
    swtch.enabled = true;
    auto *pyObj = Shiboken::Conversions::pointerToPython(Shiboken::SbkType<cppswitch>(), &swtch);
    if (PyModule_AddObject(module, "cppswitch", pyObj) < 0)
    {
        if (PyErr_Occurred())
            PyErr_Print();
        return -1;
    }

    return PyRun_SimpleString(script);
}

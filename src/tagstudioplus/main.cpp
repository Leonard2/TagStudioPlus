#include <filesystem>

#include <QtGlobal>
#include <QByteArrayView>

#include "tagstudioplus_python.h"
extern "C" PyObject *PyInit_tagstudioplus();

const char *script = "import tagstudio.main\n"
                     "tagstudio.main.main()";


int main(int argc, char *argv[])
{
    auto dir = std::filesystem::weakly_canonical(std::filesystem::path(argv[0])).parent_path();
    qputenv("PYTHONHOME", dir.string().c_str());
    dir = dir / "_internal";
    qputenv("PYTHONPATH", dir.string().c_str());

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

    TSPApplication app(argc, argv);
    auto *pyObj = Shiboken::Conversions::pointerToPython(Shiboken::SbkType<TSPApplication>(), &app);
    if (PyModule_AddObject(module, "app", pyObj) < 0)
    {
        if (PyErr_Occurred())
            PyErr_Print();
        return -1;
    }

    auto *codeObj = Py_CompileString(script, "<internal>", Py_file_input);
    if (codeObj == nullptr)
    {
        return -1;
    }

    auto *main = PyImport_AddModule("__main__");
    if (main == nullptr)
    {
        return -1;
    }
    auto *dict = PyModule_GetDict(main);
    if (dict == nullptr)
    {
        if (PyErr_Occurred())
            PyErr_Print();
        return -1;
    }

    PyEval_EvalCode(codeObj, dict, dict);
    return 0;
}

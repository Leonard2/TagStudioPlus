#include <filesystem>

#include <QtGlobal>
#include <QByteArrayView>

#include "autodecref.h"

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

    {
        Shiboken::AutoDecRef module(PyImport_ImportModule("tagstudioplus"));
        if (module.object() == nullptr)
        {
            if (PyErr_Occurred())
                PyErr_Print();
            return 1;
        }

        TSPApplication app(argc, argv);
        Shiboken::AutoDecRef pyObj(Shiboken::Conversions::pointerToPython(Shiboken::SbkType<TSPApplication>(), &app));
        if (PyModule_AddObject(module, "app", pyObj) < 0)
        {
            if (PyErr_Occurred())
                PyErr_Print();
            return -1;
        }

        {
            Shiboken::AutoDecRef codeObj(Py_CompileString(script, "<internal>", Py_file_input));
            if (codeObj.object() == nullptr)
            {
                return -1;
            }
            
            Shiboken::AutoDecRef main(PyImport_AddModule("__main__"));
            if (main.object() == nullptr)
            {
                return -1;
            }
            Py_IncRef(main);

            Shiboken::AutoDecRef dict(PyModule_GetDict(main));
            if (dict.object() == nullptr)
            {
                if (PyErr_Occurred())
                PyErr_Print();
                return -1;
            }
            Py_IncRef(dict);

            Shiboken::AutoDecRef run(PyEval_EvalCode(codeObj, dict, dict));
        }
    }

    return Py_FinalizeEx();
}

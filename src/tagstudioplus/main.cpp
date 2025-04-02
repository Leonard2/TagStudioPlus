#include <filesystem>

#include <stdlib.h>

#include "Python.h"

const char *script = "import tagstudio.main\n"
                     "tagstudio.main.main()";


int main(int argc, char *argv[])
{
    auto dir = std::filesystem::weakly_canonical(std::filesystem::path(argv[0])).parent_path();
    putenv(std::format("PYTHONHOME={}", dir.string()).c_str());
    dir = dir / "_internal";
    putenv(std::format("PYTHONPATH={}", dir.string()).c_str());

    Py_Initialize();
    if (PyErr_Occurred())
    {
        PyErr_Print();
        return 1;
    }
    return PyRun_SimpleString(script);
}

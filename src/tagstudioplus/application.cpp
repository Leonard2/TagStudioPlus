#include "application.h"


TSPApplication::TSPApplication(int &argc, char **argv)
    : QApplication(argc, argv)
{
    m_hascpp = true;
}

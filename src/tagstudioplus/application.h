#pragma once

#include <QApplication>


class TSPApplication : public QApplication
{
    Q_OBJECT

    Q_PROPERTY(bool hascpp MEMBER m_hascpp)

public:
    TSPApplication(int &argc, char **argv);

private:
    bool m_hascpp;
};

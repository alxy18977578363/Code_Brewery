#ifndef WIDGET_H
#define WIDGET_H

#include <QWidget>
#include "Network.h"
#include <QGraphicsScene>

QT_BEGIN_NAMESPACE
namespace Ui {
class Widget;
}
QT_END_NAMESPACE

class Widget : public QWidget
{
    Q_OBJECT

public:
    Widget(QWidget *parent = nullptr);
    ~Widget();

private slots:
    void onExampleButtonClicked();
    void onAddEventButtonClicked();
    void onAddActivityButtonClicked();
    void onAnalyzeButtonClicked();
    void onClearButtonClicked();

private:
    void drawNetwork();
    void drawEvent(Event* event);
    void drawActivity(Activity* activity);
    void updateStatusDisplay();
    void clearCanvas();

    Ui::Widget *ui;
    Network network;
    QGraphicsScene* scene;
    int nextEventId = 1;
};

#endif // WIDGET_H

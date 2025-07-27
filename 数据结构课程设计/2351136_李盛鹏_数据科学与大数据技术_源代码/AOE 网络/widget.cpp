#include "widget.h"
#include "ui_widget.h"
#include <QGraphicsEllipseItem>
#include <QGraphicsLineItem>
#include <QGraphicsTextItem>
#include <QMessageBox>
#include <QDebug>

Widget::Widget(QWidget *parent)
    : QWidget(parent)
    , ui(new Ui::Widget)
    , scene(new QGraphicsScene(this))
{
    ui->setupUi(this);

    // 初始化图形视图
    ui->graphicsView->setScene(scene);
    ui->graphicsView->setRenderHint(QPainter::Antialiasing);

    // 连接信号和槽
    connect(ui->exampleButton, &QPushButton::clicked, this, &Widget::onExampleButtonClicked);
    connect(ui->addEventButton, &QPushButton::clicked, this, &Widget::onAddEventButtonClicked);
    connect(ui->addActivityButton, &QPushButton::clicked, this, &Widget::onAddActivityButtonClicked);
    connect(ui->analyzeButton, &QPushButton::clicked, this, &Widget::onAnalyzeButtonClicked);
    connect(ui->clearButton, &QPushButton::clicked, this, &Widget::onClearButtonClicked);

    // 设置初始状态
    ui->eventIdSpinBox->setMinimum(1);
    ui->durationSpinBox->setMinimum(1);
    ui->startEventSpinBox->setMinimum(1);
    ui->endEventSpinBox->setMinimum(1);
}

Widget::~Widget()
{
    delete ui;
}

void Widget::onExampleButtonClicked()
{
    // 清空当前网络
    network.clearNetwork();
    clearCanvas();

    Event* event1 = new Event(1);
    Event* event2 = new Event(2);
    Event* event3 = new Event(3);
    Event* event4 = new Event(4);
    Event* event5 = new Event(5);
    Event* event6 = new Event(6);
    Event* event7 = new Event(7);
    Event* event8 = new Event(8);
    Event* event9 = new Event(9);
    Event* event10 = new Event(10);

    network.addEvent(event1);
    network.addEvent(event2);
    network.addEvent(event3);
    network.addEvent(event4);
    network.addEvent(event5);
    network.addEvent(event6);
    network.addEvent(event7);
    network.addEvent(event8);
    network.addEvent(event9);
    network.addEvent(event10);

    Activity* a1 = new Activity(1, 2, 5);
    Activity* a2 = new Activity(1, 3, 6);
    Activity* a3 = new Activity(2, 4, 3);
    Activity* a4 = new Activity(3, 4, 6);
    Activity* a5 = new Activity(3, 5, 3);
    Activity* a6 = new Activity(4, 6, 4);
    Activity* a7 = new Activity(4, 7, 4);
    Activity* a8 = new Activity(4, 5, 3);
    Activity* a9 = new Activity(6, 10, 4);
    Activity* a10 = new Activity(5, 7, 1);
    Activity* a11 = new Activity(5, 8, 4);
    Activity* a12 = new Activity(7, 9, 5);
    Activity* a13 = new Activity(8, 9, 2);
    Activity* a14 = new Activity(9, 10, 2);


    network.addActivity(a1);
    network.addActivity(a2);
    network.addActivity(a3);
    network.addActivity(a4);
    network.addActivity(a5);
    network.addActivity(a6);
    network.addActivity(a7);
    network.addActivity(a8);
    network.addActivity(a9);
    network.addActivity(a10);
    network.addActivity(a11);
    network.addActivity(a12);
    network.addActivity(a13);
    network.addActivity(a14);


    if (network.getAllEvents().isEmpty()) {
        QMessageBox::warning(this, "错误", "网络中没有事件");
        return;
    }

    if (network.analyzeCriticalPath()) {
        // 重新绘制网络以突出显示关键路径
        clearCanvas();
        drawNetwork();
        updateStatusDisplay();
    } else {
        Network::NetworkStatus status = network.checkFeasibility();
        QMessageBox::warning(this, "错误",
                             QString("网络无效: %1").arg(network.getStatusString(status)));
    }


    nextEventId = 11; // 设置下一个事件ID
}

void Widget::onAddEventButtonClicked()
{
    int id = ui->eventIdSpinBox->value();

    // 检查事件是否已存在
    for (Event* event : network.getAllEvents()) {
        if (event->id == id) {
            QMessageBox::warning(this, "错误", QString("事件%1已存在").arg(id));
            return;
        }
    }

    // 添加新事件
    Event* newEvent = new Event(id);
    network.addEvent(newEvent);

    // 更新下一个事件ID
    nextEventId = id + 1;
    ui->eventIdSpinBox->setValue(nextEventId);
    ui->startEventSpinBox->setMaximum(nextEventId - 1);
    ui->endEventSpinBox->setMaximum(nextEventId - 1);

    // 重新绘制网络
    clearCanvas();
    drawNetwork();
}

void Widget::onAddActivityButtonClicked()
{
    int start = ui->startEventSpinBox->value();
    int end = ui->endEventSpinBox->value();
    int duration = ui->durationSpinBox->value();

    // 检查是否为自反
    if(start == end){
        QMessageBox::warning(this, "错误", QString("事件%1不能从自己到自己").arg(start));
        return;
    }

    // 检查起止事件是否存在
    bool startExists = false, endExists = false;
    for (Event* event : network.getAllEvents()) {
        if (event->id == start) startExists = true;
        if (event->id == end) endExists = true;
    }

    if (!startExists || !endExists) {
        QMessageBox::warning(this, "错误", "起止事件不存在");
        return;
    }

    // 检查是否已存在相同起止点的活动
    bool activityExists = false;
    for (Activity* existingActivity : network.getAllActivities()) {
        if (existingActivity->start == start && existingActivity->end == end) {
            activityExists = true;
            break;
        }
    }

    if (activityExists) {
        QMessageBox::warning(this, "错误",
                             QString("从事件%1到事件%2的活动已存在").arg(start).arg(end));
        return;
    }

    // 添加新活动
    Activity* newActivity = new Activity(start, end, duration);
    network.addActivity(newActivity);

    // 重新绘制网络
    clearCanvas();
    drawNetwork();
}

void Widget::onAnalyzeButtonClicked()
{
    if (network.getAllEvents().isEmpty()) {
        QMessageBox::warning(this, "错误", "网络中没有事件");
        return;
    }

    if (network.analyzeCriticalPath()) {
        // 重新绘制网络以突出显示关键路径
        clearCanvas();
        drawNetwork();
        updateStatusDisplay();
    } else {
        Network::NetworkStatus status = network.checkFeasibility();
        QMessageBox::warning(this, "错误",
                             QString("网络无效: %1").arg(network.getStatusString(status)));
    }
}

void Widget::onClearButtonClicked()
{
    network.clearNetwork();
    clearCanvas();
    ui->statusTextEdit->clear();
    nextEventId = 1;
    ui->eventIdSpinBox->setValue(1);
}

void Widget::drawNetwork()
{
    const int radius = 30;
    const int spacing = 100;

    // 先绘制所有活动
    for (Activity* activity : network.getAllActivities()) {
        drawActivity(activity);
    }

    // 然后绘制所有事件（这样事件会显示在活动上方）
    for (Event* event : network.getAllEvents()) {
        drawEvent(event);
    }
}

void Widget::drawEvent(Event* event)
{
    const int radius = 30;

    // 计算位置（简单布局）
    int x = 100 + (event->id % 3) * 200;
    int y = 100 + (event->id / 3) * 150;

    // 创建圆形表示事件
    QGraphicsEllipseItem* circle = new QGraphicsEllipseItem(-radius, -radius, radius*2, radius*2);
    circle->setPos(x, y);

    // 根据是否为关键路径设置颜色
    if (event->isCritical) {
        circle->setBrush(Qt::red);
    } else {
        circle->setBrush(Qt::lightGray);
    }

    scene->addItem(circle);

    // 添加事件ID文本
    QGraphicsTextItem* text = new QGraphicsTextItem(QString::number(event->id));
    text->setPos(x - 5, y - 8); // 粗略居中
    scene->addItem(text);

    // 添加事件时间信息
    QGraphicsTextItem* timeText = new QGraphicsTextItem(
        QString("ve=%1\nvl=%2").arg(event->ve).arg(event->vl));
    timeText->setPos(x + radius + 5, y - radius);
    scene->addItem(timeText);

    // 保存位置信息
    event->pos = QPointF(x, y);
}

void Widget::drawActivity(Activity* activity)
{
    // 查找起止事件
    Event* startEvent = nullptr;
    Event* endEvent = nullptr;

    for (Event* event : network.getAllEvents()) {
        if (event->id == activity->start) startEvent = event;
        if (event->id == activity->end) endEvent = event;
    }

    if (!startEvent || !endEvent) return;

    // 计算箭头位置
    QPointF startPos = startEvent->pos;
    QPointF endPos = endEvent->pos;

    // 计算方向向量
    QPointF direction = endPos - startPos;
    double length = sqrt(direction.x() * direction.x() + direction.y() * direction.y());
    direction /= length; // 归一化

    // 调整起点和终点到圆边缘
    const int radius = 30;
    QPointF adjustedStart = startPos + direction * radius;
    QPointF adjustedEnd = endPos - direction * radius;

    // 创建线条表示活动
    QGraphicsLineItem* line = new QGraphicsLineItem(
        adjustedStart.x(), adjustedStart.y(), adjustedEnd.x(), adjustedEnd.y());

    // 根据是否为关键路径设置颜色和线宽
    if (activity->isCritical) {
        line->setPen(QPen(Qt::red, 3));
    } else {
        line->setPen(QPen(Qt::black, 1));
    }

    scene->addItem(line);

    // 添加活动信息文本
    QPointF midPoint = (adjustedStart + adjustedEnd) / 2;
    QGraphicsTextItem* text = new QGraphicsTextItem(
        QString("%1 (e:%2,l:%3)").arg(activity->duration).arg(activity->e).arg(activity->l));
    text->setPos(midPoint);
    scene->addItem(text);

    // 添加箭头
    // 这里省略了箭头绘制的具体实现，可以使用QGraphicsPolygonItem添加箭头
}

void Widget::updateStatusDisplay()
{
    QString statusText;

    // 显示总工期
    statusText += QString("总工期: %1\n\n").arg(network.getTotalDuration());

    // 显示关键事件
    statusText += "关键事件:\n";
    for (Event* event : network.getCriticalEvents()) {
        statusText += QString("事件%1 (ve=%2, vl=%3)\n")
                          .arg(event->id).arg(event->ve).arg(event->vl);
    }

    // 显示关键活动
    statusText += "\n关键活动:\n";
    for (Activity* activity : network.getCriticalActivities()) {
        statusText += QString("%1→%2 (持续时间: %3, e=%4, l=%5)\n")
                          .arg(activity->start).arg(activity->end)
                          .arg(activity->duration).arg(activity->e).arg(activity->l);
    }

    ui->statusTextEdit->setPlainText(statusText);
}

void Widget::clearCanvas()
{
    scene->clear();
}

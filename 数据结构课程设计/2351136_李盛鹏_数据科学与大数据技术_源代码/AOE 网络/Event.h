// Event.h - 定义事件(顶点)类
#ifndef EVENT_H
#define EVENT_H

#include <QVector>
#include <QPointF>

class Activity; // 前向声明

class Event {
public:
    // 构造函数
    Event(int id);

    // 基本属性
    int id;            // 事件ID
    bool isCritical;   // 是否在关键路径上
    int ve;             // 最早发生时间
    int vl;             // 最迟发生时间
    QPointF pos;       // 绘图位置

    // 图结构
    QVector<Activity*> outgoing; // 出边活动
    int inDegree;      // 入度（拓扑排序用）

    // 方法
    void addOutgoingActivity(Activity* activity);
    QString toString() const;
};

#endif // EVENT_H

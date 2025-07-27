// Activity.h - 定义活动(边)类
#ifndef ACTIVITY_H
#define ACTIVITY_H

#include <QPointF>
#include <QString>

class Event; // 前向声明（避免循环依赖）


// Activity 是活动，也就是图中的"边"
class Activity {
public:
    // 构造函数
    Activity(int startEventId, int endEventId, int duration);

    // 基本属性
    int start;       // 起始事件ID
    int end;         // 结束事件ID
    int duration;    // 活动持续时间
    int e;           // 最早开始时间
    int l;           // 最迟开始时间
    bool isCritical; // 是否为关键活动

    // 绘图相关（可选）
    QPointF startPos; // 起点坐标
    QPointF endPos;   // 终点坐标

    // 方法
    QString toString() const;
};

#endif // ACTIVITY_H

// Activity.cpp - 实现活动类
#include "Activity.h"
#include <QDebug>

Activity::Activity(int startEventId, int endEventId, int duration)
    : start(startEventId),
    end(endEventId),
    duration(duration),
    e(0),           // 由于边的最早和最晚时间不用比较，所以赋值为0即可
    l(0),
    isCritical(false),
    startPos(0, 0),
    endPos(0, 0) {}

QString Activity::toString() const {
    return QString("Activity %1->%2 (Dur: %3, e: %4, l: %5, %6)")
    .arg(start).arg(end).arg(duration)
        .arg(e).arg(l)
        .arg(isCritical ? "CRITICAL" : "non-critical");
}

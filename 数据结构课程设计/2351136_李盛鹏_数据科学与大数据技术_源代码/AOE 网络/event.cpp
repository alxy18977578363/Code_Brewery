// Event.cpp - 实现事件类
#include "Event.h"
#include "Activity.h" // 需要Activity的完整定义

Event::Event(int id)
    : id(id),
    isCritical(false),
    ve(0),
    vl(INT_MAX),
    pos(0, 0),
    inDegree(0) {}

void Event::addOutgoingActivity(Activity* activity) {
    if (activity) {
        outgoing.append(activity);
    }
}

QString Event::toString() const {
    return QString("Event %1 (e: %2, l: %3, %4)")
    .arg(id).arg(ve).arg(vl)
        .arg(isCritical ? "CRITICAL" : "non-critical");
}

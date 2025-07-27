#include "Network.h"
#include <limits.h>
#include <algorithm>
#include <QDebug>

Network::Network() : totalDuration(0) {}

Network::~Network() {
    clearNetwork();
}

void Network::clearNetwork() {
    qDeleteAll(activities);
    qDeleteAll(events);
    activities.clear();
    events.clear();
    totalDuration = 0;
}

void Network::addEvent(Event* event) {
    if (event && std::find_if(events.begin(), events.end(),
                              [event](Event* e) { return e->id == event->id; }) == events.end()) {
        // 计算位置
        int id = event->id;
        int x = 100 + (id % 3) * 200;
        int y = 100 + (id / 3) * 150;
        event->pos = QPointF(x,y);

        events.append(event);
    }
}

void Network::addActivity(Activity* activity) {
    if (!activity) return;

    // 检查是否已存在相同起止点的活动
    auto it = std::find_if(activities.begin(), activities.end(),
                           [activity](Activity* a) {
                               return a->start == activity->start && a->end == activity->end;
                           });

    if (it != activities.end()) {
        qDebug() << "Activity from" << activity->start << "to" << activity->end << "already exists";
        delete activity;
        return;
    }

    activities.append(activity);

    // 更新事件的出边
    for (Event* event : events) {
        if (event->id == activity->start) {
            event->addOutgoingActivity(activity);
            break;
        }
    }

    // 更新目标事件的入度
    for (Event* event : events) {
        if (event->id == activity->end) {
            event->inDegree++;
            break;
        }
    }
}

Network::NetworkStatus Network::checkFeasibility() const {
    // 检查空网络
    if (events.isEmpty() || activities.isEmpty()) {
        return EmptyNetwork;
    }

    // 检查是否有负持续时间
    for (const Activity* activity : activities) {
        if (activity->duration < 0) {
            return NegativeDuration;
        }
    }

    // 检查是否有唯一的起点和终点
    Event* startEvent = nullptr;
    Event* endEvent = nullptr;
    if (!hasUniqueStartAndEnd(startEvent, endEvent)) {
        return NoUniqueStartOrEnd;
    }

    // 检查网络连通性
    if (!isNetworkConnected()) {
        return Disconnected;
    }

    // 检查是否有环
    QVector<Event*> sortedEvents;
    if (!topologicalSort(sortedEvents)) {
        return HasCycle;
    }

    return Valid;
}

bool Network::hasUniqueStartAndEnd(Event*& startEvent, Event*& endEvent) const {
    int startCount = 0;
    int endCount = 0;

    for (Event* event : events) {
        if (event->inDegree == 0) {
            startCount++;
            startEvent = event;
        }

        if (event->outgoing.isEmpty()) {
            endCount++;
            endEvent = event;
        }
    }

    return (startCount == 1) && (endCount == 1);
}

bool Network::isNetworkConnected() const {
    if (events.isEmpty()) return false;

    // 使用BFS检查从起点到所有节点的连通性
    QVector<bool> visited(events.size(), false);
    QQueue<const Event*> queue;

    // 找到起点
    const Event* startEvent = nullptr;
    for (const Event* event : events) {
        if (event->inDegree == 0) {
            startEvent = event;
            break;
        }
    }

    if (!startEvent) return false;

    queue.enqueue(startEvent);
    visited[events.indexOf(const_cast<Event*>(startEvent))] = true;

    while (!queue.isEmpty()) {
        const Event* current = queue.dequeue();

        // 探索事件的每一个出边，从出边中知道邻接节点
        for (const Activity* activity : current->outgoing) {
            for (const Event* neighbor : events) {
                if (neighbor->id == activity->end && !visited[events.indexOf(const_cast<Event*>(neighbor))]) {
                    visited[events.indexOf(const_cast<Event*>(neighbor))] = true;
                    queue.enqueue(neighbor);
                }
            }
        }
    }

    // 检查是否所有节点都被访问过
    return std::all_of(visited.begin(), visited.end(), [](bool v) { return v; });
}

bool Network::topologicalSort(QVector<Event*>& sortedEvents) const {
    QQueue<Event*> queue;
    QVector<Event*> tempEvents = events;
    QVector<int> inDegreeCopy(tempEvents.size());

    // 初始化入度副本
    for (int i = 0; i < tempEvents.size(); ++i) {
        inDegreeCopy[i] = tempEvents[i]->inDegree;
        if (inDegreeCopy[i] == 0) {
            queue.enqueue(tempEvents[i]);
        }
    }

    int count = 0;
    while (!queue.isEmpty()) {
        Event* current = queue.dequeue();
        sortedEvents.append(current);
        count++;

        // 减少相邻节点的入度
        for (Activity* activity : current->outgoing) {
            for (int i = 0; i < tempEvents.size(); ++i) {
                if (tempEvents[i]->id == activity->end) {
                    inDegreeCopy[i]--;
                    if (inDegreeCopy[i] == 0) {
                        queue.enqueue(tempEvents[i]);
                    }
                    break;
                }
            }
        }
    }

    // 检查是否有环
    return (count == tempEvents.size());
}

bool Network::analyzeCriticalPath() {
    // 先检查工程可行性
    NetworkStatus status = checkFeasibility();
    if (status != Valid) {
        qDebug() << "工程不可行:" << getStatusString(status);
        return false;
    }

    // 1. 拓扑排序
    QVector<Event*> sortedEvents;
    if (!topologicalSort(sortedEvents)) {
        qDebug() << "Network has cycles, cannot compute critical path";
        return false;
    }

    // 2. 计算事件的最早发生时间
    calculateEarliestTimes(sortedEvents);

    // 3. 计算事件的最迟发生时间
    calculateLatestTimes(sortedEvents);

    // 4. 计算活动的最早和最迟开始时间
    calculateActivityTimes();

    // 5. 标记关键路径
    markCriticalPath();

    // 设置总工期
    if (!sortedEvents.isEmpty()) {
        totalDuration = sortedEvents.last()->ve;
    }

    return true;
}

void Network::calculateEarliestTimes(const QVector<Event*>& sortedEvents) {
    // 初始化所有事件的最早发生时间为0
    for (Event* event : sortedEvents) {
        event->ve = 0;
    }

    // 按拓扑顺序计算ve
    for (Event* event : sortedEvents) {
        for (Activity* activity : event->outgoing) {
            for (Event* target : events) {
                if (target->id == activity->end) {
                    if (target->ve < event->ve + activity->duration) {
                        target->ve = event->ve + activity->duration;
                    }
                    break;
                }
            }
        }
    }
}

void Network::calculateLatestTimes(const QVector<Event*>& sortedEvents) {
    if (sortedEvents.isEmpty()) return;

    // 初始化所有事件的最迟发生时间为最后一个事件的ve
    int lastVe = sortedEvents.last()->ve;
    for (Event* event : sortedEvents) {
        event->vl = lastVe;
    }

    // 按逆拓扑顺序计算vl
    for (int i = sortedEvents.size() - 1; i >= 0; --i) {
        Event* event = sortedEvents[i];
        for (Activity* activity : event->outgoing) {
            for (Event* target : events) {
                if (target->id == activity->end) {
                    if (event->vl > target->vl - activity->duration) {
                        event->vl = target->vl - activity->duration;
                    }
                    break;
                }
            }
        }
    }
}

void Network::calculateActivityTimes() {
    for (Activity* activity : activities) {
        // 找到起始事件
        Event* startEvent = nullptr;
        for (Event* event : events) {
            if (event->id == activity->start) {
                startEvent = event;
                break;
            }
        }

        // 找到结束事件
        Event* endEvent = nullptr;
        for (Event* event : events) {
            if (event->id == activity->end) {
                endEvent = event;
                break;
            }
        }

        if (startEvent && endEvent) {
            // 活动的最早开始时间 = 起始事件的最早发生时间
            activity->e = startEvent->ve;

            // 活动的最迟开始时间 = 结束事件的最迟发生时间 - 活动持续时间
            activity->l = endEvent->vl - activity->duration;
        }
    }
}

void Network::markCriticalPath() {
    // 标记关键事件
    for (Event* event : events) {
        event->isCritical = (event->ve == event->vl);
    }

    // 标记关键活动
    for (Activity* activity : activities) {
        activity->isCritical = (activity->e == activity->l) && (activity->e != 0);
    }
}

QString Network::getStatusString(NetworkStatus status) const {
    switch (status) {
    case Valid:
        return "工程可行";
    case HasCycle:
        return "网络中存在环";
    case NoUniqueStartOrEnd:
        return "没有唯一的起点或终点";
    case NegativeDuration:
        return "存在负持续时间活动";
    case EmptyNetwork:
        return "空网络";
    case Disconnected:
        return "网络不连通";
    default:
        return "未知状态";
    }
}

int Network::getTotalDuration() const {
    return totalDuration;
}

QVector<Activity*> Network::getAllActivities() const {
    return activities;
}

QVector<Event*> Network::getAllEvents() const {
    return events;
}

QVector<Activity*> Network::getCriticalActivities() const {
    QVector<Activity*> criticalActivities;
    for (Activity* activity : activities) {
        if (activity->isCritical) {
            criticalActivities.append(activity);
        }
    }
    return criticalActivities;
}

QVector<Event*> Network::getCriticalEvents() const {
    QVector<Event*> criticalEvents;
    for (Event* event : events) {
        if (event->isCritical) {
            criticalEvents.append(event);
        }
    }
    return criticalEvents;
}

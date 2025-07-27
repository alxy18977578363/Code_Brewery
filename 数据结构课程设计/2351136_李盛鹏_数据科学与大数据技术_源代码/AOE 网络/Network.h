#ifndef NETWORK_H
#define NETWORK_H

#include "Event.h"
#include "Activity.h"
#include <QVector>
#include <QQueue>
#include <QString>

class Network {
public:
    enum NetworkStatus {
        Valid,              // 工程可行
        HasCycle,           // 网络中存在环
        NoUniqueStartOrEnd, // 没有唯一的起点或终点
        NegativeDuration,   // 存在负持续时间
        EmptyNetwork,       // 空网络
        Disconnected       // 网络不连通
    };

    Network();
    ~Network();

    // 添加事件和活动
    void addEvent(Event* event);
    void addActivity(Activity* activity);
    void clearNetwork();

    // 检查工程可行性
    NetworkStatus checkFeasibility() const;

    // 关键路径分析
    bool analyzeCriticalPath();

    // 获取结果
    int getTotalDuration() const;
    QVector<Activity*> getAllActivities() const;
    QVector<Event*> getAllEvents() const;
    QVector<Activity*> getCriticalActivities() const;
    QVector<Event*> getCriticalEvents() const;
    QString getStatusString(NetworkStatus status) const;

private:
    // 拓扑排序
    bool topologicalSort(QVector<Event*>& sortedEvents) const;

    // 计算事件的最早发生时间
    void calculateEarliestTimes(const QVector<Event*>& sortedEvents);

    // 计算事件的最迟发生时间
    void calculateLatestTimes(const QVector<Event*>& sortedEvents);

    // 计算活动的最早和最迟开始时间
    void calculateActivityTimes();

    // 标记关键路径
    void markCriticalPath();

    // 检查是否有唯一的起点和终点
    bool hasUniqueStartAndEnd(Event*& startEvent, Event*& endEvent) const;

    // 检查网络连通性
    bool isNetworkConnected() const;

    QVector<Event*> events;
    QVector<Activity*> activities;
    int totalDuration;
};

#endif // NETWORK_H

package com.ocean.database.service;

/**
 * Service基类
 * 定义通用CRUD操作
 */
public abstract class BaseService {
    
    /**
     * 获取所有记录
     */
    public abstract String getAll() throws Exception;
    
    /**
     * 根据ID获取单条记录
     */
    public abstract String getById(String id) throws Exception;
    
    /**
     * 创建新记录
     */
    public abstract String create(String jsonBody) throws Exception;
    
    /**
     * 更新记录
     */
    public abstract String update(String id, String jsonBody) throws Exception;
    
    /**
     * 删除记录
     */
    public abstract String delete(String id) throws Exception;
}

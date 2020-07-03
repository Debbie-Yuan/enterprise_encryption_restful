# enterprise_encryption_restful
企业安全信息管理 后端API接口

## 环境配置：
> gunicorn               20.0.4   
> Flask                  1.1.2   
> Flask-Caching          1.9.0   
> Flask-DebugToolbar     0.11.0   
> Flask-Login            0.5.0   
> Flask-Mail             0.9.1   
> Flask-Migrate          2.5.3   
> Flask-RESTful          0.3.8   
> Flask-Script           2.0.6   
> Flask-Session          0.3.2   
    
    
> python 3.8.1   
> nginx    



## 运行方法：

```bash
gunicorn --reload -c gunicorn_deploy.py manager:app    
```

## 测试接口：

<https://debbiee.cn/flask/>

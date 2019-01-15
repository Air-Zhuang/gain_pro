'''
parser:
    parser_urls:从HTML中提取url放到pre_parse_urls中
    parser_item:根据自定义的item规则从HTML中提取字段
    execute_url(@coroutine):调用request.fetch()发送网络请求获取页面源码
                        调用parser_item,执行item.save()保存字段
    task(@coroutine):调度execute_url

spider(with uvloop):
    is_running:当前爬虫状态
    parse:逐个执行parser.parser_urls()
    run:gain框架启动函数,创建loop,将parser.task()任务塞进去
    init_parse:首次请求(可能用来登陆操作)

log:
    日志模块

request(with uvloop):
    用aiohttp发送get请求获取HTML,只返回response.text()

selector:
    定义了Css,Xpath,正则提取规则

item:
    save:自定义字段存储规则
'''
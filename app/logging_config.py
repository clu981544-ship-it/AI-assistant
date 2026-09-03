import logging
logging.basicConfig(
    level=logging.INFO,#显示INFO及以上的级别日志
    format="%(asctime)s-%(levelname)s-%(name)s-%(message)s"#统一日志格式
)
logger=logging.getLogger("ai-assistant")#创建项目专用日志记录器
DROP TABLE IF EXISTS ods_note_data;
CREATE TABLE IF NOT EXISTS ods_note_data (
    note_id STRING COMMENT 'Unique identifier for the note',
    keyword STRING COMMENT 'Keyword associated with the note (e.g., Indonesia tourism)',
    author_id STRING COMMENT 'Unique identifier of the author',
    note_url STRING COMMENT 'URL of the note',
    title STRING COMMENT 'Title of the note',
    content STRING COMMENT 'Content of the note (appears empty in sample data)',
    publish_date STRING COMMENT 'Publication date of the note (format: YYYY/MM/DD)',
    like_count INT COMMENT 'Number of likes received by the note',
    comment_count INT COMMENT 'Number of comments on the note',
    share_count INT COMMENT 'Number of shares of the note',
    image_count INT COMMENT 'Number of images in the note',
    crawl_time STRING COMMENT 'Timestamp when the data was crawled (format: YYYY/MM/DD HH:MM)'
)
COMMENT 'ODS table for storing raw note data from social platform'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

-- Load data into ODS table
LOAD DATA INPATH '/training/hdfs_data/notes.csv' 
OVERWRITE INTO TABLE ods_note_data;

-- 忽略第一行
ALTER TABLE ods_note_data 
SET TBLPROPERTIES ('skip.header.line.count'='1');

--------------------------------------------------------------------------------------------------------

-- 创建评论数据ODS表
DROP TABLE IF EXISTS ods_comment_data;
CREATE TABLE IF NOT EXISTS ods_comment_data (
    comment_id STRING COMMENT '评论唯一ID',
    note_id STRING COMMENT '关联的笔记ID',
    user_id STRING COMMENT '评论用户ID',
    user_name STRING COMMENT '评论用户名',
    user_url STRING COMMENT '用户主页URL',
    comment_content STRING COMMENT '评论内容',
    comment_date STRING COMMENT '评论日期',
    comment_likes INT COMMENT '评论点赞数',
    comment_replies INT COMMENT '评论回复数',
    crawl_time STRING COMMENT '爬取时间'
)
COMMENT '评论原始数据表'
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ','  -- 根据实际分隔符调整
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");

-- 加载CSV数据到表中(假设文件名为comments.csv)
LOAD DATA INPATH '/training/hdfs_data/comments.csv' INTO TABLE ods_comment_data;


SELECT * FROM ods_comment_data LIMIT 5;

--------------------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ods_author_data (
    author_id STRING COMMENT 'Unique identifier of the author',
    author_url STRING COMMENT 'URL to the author''s profile page',
    author_name STRING COMMENT 'Name or nickname of the author',
    fan_count INT COMMENT 'Number of fans/followers the author has',
    following_count INT COMMENT 'Number of accounts the author follows',
    like_count INT COMMENT 'Total number of likes received by the author',
    tags STRING COMMENT 'Tags associated with the author (comma-separated if multiple)',
    description STRING COMMENT 'Author''s self-description or bio',
    ip_location STRING COMMENT 'Geographic location derived from IP address',
    crawl_time STRING COMMENT 'Timestamp when the data was crawled (format: YYYY-MM-DD HH:MM:SS)'
)
COMMENT 'Raw author profile data from source platform'
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ','  -- 根据实际分隔符调整
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");

-- 加载CSV数据到表中(假设文件名为comments.csv)
LOAD DATA INPATH '/training/hdfs_data/authors_detail.csv' INTO TABLE ods_author_data;


SELECT * FROM ods_author_data LIMIT 5;
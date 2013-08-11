create table 163baoxian(
    id varchar(20) not null default '',
    url varchar(200) default null,
    name varchar(100) default null,
    interest varchar(50) default null,
    summary varchar(100) default null,
    start_amount varchar(20) default null,
    limit_interest varchar(20) default null,
    period varchar(50) default null,
    company varchar(50) default null,
    pic_urls varchar(800) default null,
    update_time datetime default null,
    primary key (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

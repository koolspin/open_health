create table user
(
    id       integer not null
        constraint user_pk
            primary key autoincrement,
    username varchar not null,
    password varchar not null,
    creation_date     datetime not null,
    last_login_date   datetime
);

create unique index user_username_uindex
    on user (username);

create table activity
(
    id                integer  not null
        constraint activity_pk
            primary key autoincrement,
    user_id           integer  not null
        references user,
    activity_date     datetime not null,
    device_mfgr       varchar,
    device_model      varchar,
    activity_type     varchar  not null,
    activity_sub_type varchar,
    file_hash         varchar
);

create index activity_activity_date_index
    on activity (activity_date);

create index activity_file_hash_index
    on activity (file_hash);

create table lap_sum
(
    id                 integer not null
        constraint lap_sum_pk
            primary key autoincrement,
    activity_id        integer not null
        references activity,
    lap_num            integer not null,
    summary_key        varchar not null,
    summary_value      varchar,
    summary_value_int  integer,
    summary_value_real real,
    summary_value_date datetime
);

create unique index lap_sum_activity_id_summary_key_uindex
    on lap_sum (activity_id, lap_num, summary_key);

create table session_sum
(
    id                 integer not null
        constraint session_sum_pk
            primary key autoincrement,
    activity_id        integer not null
        references activity,
    session_num        integer not null,
    summary_key        varchar not null,
    summary_value      varchar,
    summary_value_int  integer,
    summary_value_real real,
    summary_value_date datetime
);

create unique index session_sum_activity_id_summary_key_uindex
    on session_sum (activity_id, session_num, summary_key);

create table activity_record
(
    id          integer  not null
        constraint activity_record_pk
            primary key autoincrement,
    activity_id integer  not null
        references activity,
    timestamp   datetime not null,
    lat         varchar,
    long        varchar,
    heart_rate  integer,
    distance    real,
    altitude    real,
    speed       real,
    temperature real
);

create index activity_record_timestamp_index
    on activity_record (timestamp);


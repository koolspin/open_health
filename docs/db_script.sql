DROP TABLE IF EXISTS activity_summary;
DROP TABLE IF EXISTS activity_sum;
DROP TABLE IF EXISTS activity_record;
DROP TABLE IF EXISTS activity;
DROP TABLE IF EXISTS user;

create table user
(
    id       integer not null
        constraint user_pk
            primary key autoincrement,
    username varchar not null,
    password varchar not null
);

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
    activity_sub_type varchar
);

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

create table activity_sum
(
    id            integer not null
        constraint activity_sum_pk
            primary key autoincrement,
    activity_id   integer not null
        references activity,
    summary_key   varchar not null,
    summary_value varchar
);

create unique index activity_sum_activity_id_summary_key_uindex
    on activity_sum (activity_id, summary_key);

create table activity_summary
(
    id                              integer  not null
        constraint activity_summary_pk
            primary key autoincrement,
    activity_id                     integer  not null
        references activity,
    start_time                      datetime not null,
    elapsed_time                    real,
    total_time                      real,
    total_distance                  real,
    total_calories                  real,
    average_speed                   real,
    max_speed                       real,
    average_power                   real,
    max_power                       real,
    total_ascent                    real,
    total_descent                   real,
    lap_count                       integer,
    average_heart_rate              integer,
    max_heart_rate                  integer,
    average_temperature             real,
    max_temperature                 real,
    average_cadence                 real,
    max_cadence                     real,
    total_training_effect           real,
    total_anaerobic_training_effect real
);

create unique index user_username_uindex
    on user (username);



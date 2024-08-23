CREATE TABLE 病历记录 (
    入院科室 VARCHAR(255) NOT NULL,
    入院日期 DATE NOT NULL,
    入院途径 VARCHAR(255) NOT NULL,
    病案号 VARCHAR(255) NOT NULL,
    性别 ENUM('男', '女') NOT NULL,
    年龄 INT NOT NULL,
    出院科室 VARCHAR(255) NOT NULL,
    出院日期 DATE NOT NULL,
    所属病区 VARCHAR(255) NOT NULL,
    主要诊断编码 VARCHAR(255) NOT NULL,
    主要诊断说明 TEXT NOT NULL,
    全部诊断 TEXT NOT NULL,
    主手术代码 VARCHAR(255) NOT NULL comment '连接手术目标表的编码字段',
    主手术名称 TEXT NOT NULL,
    全部手术操作 TEXT NOT NULL,
    住院天数 INT NOT NULL,
    总费用 DECIMAL(18, 2) NOT NULL,
    总药费 DECIMAL(18, 2) NOT NULL,
    抗菌药物费用 DECIMAL(18, 2) NOT NULL,
    手术治疗费 DECIMAL(18, 2) NOT NULL,
    总材料费 DECIMAL(18, 2) NOT NULL,
    手术用一次性医用材料费 DECIMAL(18, 2) NOT NULL,
    治疗结果 VARCHAR(255) NOT NULL,
    抢救次数 INT NOT NULL,
    成功次数 INT NOT NULL,
    输血次数 INT NOT NULL,
    带组医师 VARCHAR(255) NOT NULL,
    带组医师工号 VARCHAR(255) NOT NULL,
    PRIMARY KEY (病案号),
    INDEX idx_gender (性别),
    INDEX idx_discharge_date (出院日期)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS 国考三级手术目录 (
    编码 VARCHAR(255) NOT NULL,
    手术操作名称 TEXT NOT NULL,
    PRIMARY KEY (编码)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS 国考四级手术目录 (
    编码 VARCHAR(255) NOT NULL,
    手术操作名称 TEXT NOT NULL,
    PRIMARY KEY (编码)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS 国考微创手术目录 (
    编码 VARCHAR(255) NOT NULL,
    手术操作名称 TEXT NOT NULL,
    PRIMARY KEY (编码)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
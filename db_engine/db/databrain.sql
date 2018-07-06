DROP TABLE IF EXIST csv_reader_info;
CREATE TABLE csv_reader_info( 
id int NOT NULL AUTO_INCREMENT,
	project_id varchar(10) NOT NULL, 
	component_id varchar(50) NOT NULL, 
	magic_name varchar(30) NOT NULL,  
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXIST csv_reader_infotype;
CREATE TABLE csv_reader_infotype ( 
	project_id varchar(10) NOT NULL, 
	component_id varchar(50) NOT NULL, 
	field varchar(30) NOT NULL, 
	field_type varchar(10) NOT NULL, 
	date_format varchar(20), 
	selected tinyint(1) NOT NULL, 
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

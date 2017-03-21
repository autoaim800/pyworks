create table t_raws(
         shop_name varchar(20),
         cat_title varchar(200),
         page_url text,
             prod_brand varchar(64),
             prod_name varchar(64),
             pack_size varchar(20),
         retail_price varchar(10),
         unit_price varchar(30),
         save_price varchar(10),
            img_url text,
            cr_date DATETIME,
         primary key (shop_name, prod_brand, prod_name, pack_size)
        );

--*********************************************************************************************
--**  Product Model 
--**
--**  The product model is comprised of the following data models:
--**
--**     Product and Granule Model
--**        - product_granule_view
--**            - granule_imagery
--**            - granule
--**        - product_operation_view
--**            - product
--**            - product_operation
--**
--**     Product Archive Model
--**        - product_meta_history_view
--**           - product
--**           - product_meta_history
--**        - product_archive_view
--**            - product_archive
--**            - archive_view
--**                - product_archive
--**                - product_archive_reference
--**        - product_reference_view
--**           - product
--**           - product_reference
--**        - product_data_day_view
--**           - product
--**           - product_data_day
--**
--**     Product Contact Model
--**        - product_contact_view
--**            - product_contact
--**            - contact_provider_view (see create_imagery_provider.sql)
--**                 - contact 
--**                 - provider
--**                 - provider_resource_view
--**                     - provider
--**                     - provider_resource
--**
--**     Product Elements Model
--**        - product_element_view
--**            - product_element
--**            - product_element_dd_view
--**                - product_element
--**                - element_dd
--**        - product_datetime_view
--**            - product
--**            - product_datetime
--**        - product_character_view
--**            - product
--**            - product_character
--**        - product_integer_view
--**            - product
--**            - product_integer
--**        - product_real_view
--**            - product
--**            - product_real
--*********************************************************************************************


--*********************************************************************************************
-- Product and Granule Model
--*********************************************************************************************

--------------------------------------------------
-- product_granule_view
--------------------------------------------------
DROP VIEW IF EXISTS product_granule_view CASCADE;
CREATE VIEW product_granule_view AS
SELECT

   -- granule_imagery
   granule_imagery.product_id as product_id,

   -- granule
   string_agg(granule.id::int8::text,         ',' order by granule.id) as product_granule_id_list,
   string_agg(granule.version::int8::text,    ',' order by granule.id) as product_granule_version_list,
   string_agg(granule.dataset_id::int8::text, ',' order by granule.id) as product_granule_dataset_id_list,
   string_agg(granule.metadata_endpoint,      ',' order by granule.id) as product_granule_metadata_endpoint_list,
   string_agg(granule.remote_granule_ur,      ',' order by granule.id) as product_granule_remote_granule_ur_list

FROM granule_imagery
LEFT JOIN granule ON granule.id = granule_imagery.granule_id
GROUP BY granule_imagery.product_id;
SELECT COUNT(*) AS product_granule_view_count FROM product_granule_view;
SELECT * FROM product_granule_view LIMIT 5;

---------------------------------------------------------------------------
-- product_operation_view
---------------------------------------------------------------------------
DROP VIEW IF EXISTS product_operation_view CASCADE;
CREATE VIEW product_operation_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_operation
   string_agg(product_operation.version::int8::text,    ',' order by product_operation.id) as product_operation_version_list,
   string_agg(product_operation.agent,                  ',' order by product_operation.id) as product_operation_agent_list,
   string_agg(product_operation.operation,              ',' order by product_operation.id) as product_operation_list,
   string_agg(product_operation.command,                ',' order by product_operation.id) as product_operation_command_list,
   string_agg(product_operation.arguments,              ',' order by product_operation.id) as product_operation_arguments_list,
   string_agg(product_operation.start_time::int8::text, ',' order by product_operation.id) as product_operation_start_time_list,
   string_agg(product_operation.stop_time::int8::text,  ',' order by product_operation.id) as product_operation_stop_time_list,
   string_agg(('1970-01-01 00:00:00 GMT'::timestamp + ((product_operation.start_time/1000)::text)::interval)::timestamp::text,
                                                        ',' order by product_operation.id) as product_operation_start_time_string_list,
   string_agg(('1970-01-01 00:00:00 GMT'::timestamp + ((product_operation.stop_time/1000)::text)::interval)::timestamp::text,
                                                        ',' order by product_operation.id) as product_operation_stop_time_string_list
FROM product
LEFT JOIN product_operation ON product_operation.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_operation_view_count FROM product_operation_view;
SELECT * FROM product_operation_view LIMIT 5;

--*********************************************************************************************
-- Product Archive Model 
--*********************************************************************************************

--------------------------------------------------
-- product_meta_history_view
--------------------------------------------------
DROP VIEW IF EXISTS product_meta_history_view CASCADE;
CREATE VIEW product_meta_history_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_meta_history
   product_meta_history.version                     as product_meta_history_version,
   product_meta_history.version_id                  as product_meta_history_version_id,
   product_meta_history.revision_history            as product_meta_history_revision_history,
   product_meta_history.last_revision_date          as product_meta_history_last_revision_date,
   product_meta_history.creation_date               as product_meta_history_creation_date,
   ('1970-01-01 00:00:00 GMT'::timestamp + ((product_meta_history.last_revision_date/1000)::text)::interval)
                                                    as product_meta_history_last_revision_date_string,
   ('1970-01-01 00:00:00 GMT'::timestamp + ((product_meta_history.creation_date/1000)::text)::interval)
                                                    as product_meta_history_creation_date_string
FROM product 
LEFT JOIN product_meta_history ON product_meta_history.product_id = product.id
GROUP BY product.id,
         product_meta_history.version,
         product_meta_history.version_id,
         product_meta_history.revision_history,
         product_meta_history.last_revision_date,
         product_meta_history.creation_date;
   
SELECT COUNT(*) AS product_meta_history_view_count FROM product_meta_history_view;
SELECT * FROM product_meta_history_view LIMIT 5;

--------------------------------------------------
-- product_archive_view
--------------------------------------------------
DROP VIEW IF EXISTS archive_view CASCADE;
CREATE VIEW archive_view AS
SELECT

   -- product_archive
   product_archive.id,
   product_archive.product_id      as product_id,
   product_archive.version         as version,     
   product_archive.name            as name,     
   product_archive.type            as type,     
   product_archive.file_size       as file_size,     
   product_archive.checksum        as checksum,     
   product_archive.compress_flag   as compress_flag,     
   product_archive.status          as status,     

   -- product_archive_reference
   string_agg(product_archive_reference.description, ';' order by product_archive_reference.id) as reference_descriptions,
   string_agg(product_archive_reference.name,        ';' order by product_archive_reference.id) as reference_names,
   string_agg(product_archive_reference.type,        ';' order by product_archive_reference.id) as reference_types,
   string_agg(product_archive_reference.status,      ';' order by product_archive_reference.id) as reference_status

FROM product_archive LEFT JOIN product_archive_reference ON product_archive_reference.product_archive_id = product_archive.id
GROUP BY product_archive.id;
SELECT COUNT(*) AS archive_view_count FROM archive_view;
SELECT * FROM archive_view LIMIT 5;

DROP VIEW IF EXISTS product_archive_view CASCADE;
CREATE VIEW product_archive_view AS
SELECT

   -- product
   product.id as product_id,

   -- archive_view
   string_agg(archive_view.name,                         ',' order by archive_view.id) as product_archive_name_list,
   string_agg(archive_view.type,                         ',' order by archive_view.id) as product_archive_type_list,
   string_agg(archive_view.version::int8::text,          ',' order by archive_view.id) as product_archive_version_list,
   string_agg(archive_view.file_size::int8::text,        ',' order by archive_view.id) as product_archive_file_size_list,
   string_agg(archive_view.checksum,                     ',' order by archive_view.id) as product_archive_checksum_list,
   string_agg(archive_view.compress_flag::boolean::text, ',' order by archive_view.id) as product_archive_compress_flag_list, 
   string_agg(archive_view.status,                       ',' order by archive_view.id) as product_archive_status_list, 
   string_agg(archive_view.reference_descriptions,       ',' order by archive_view.id) as product_archive_reference_description_list, 
   string_agg(archive_view.reference_names,              ',' order by archive_view.id) as product_archive_reference_name_list, 
   string_agg(archive_view.reference_types,              ',' order by archive_view.id) as product_archive_reference_type_list, 
   string_agg(archive_view.reference_status,             ',' order by archive_view.id) as product_archive_reference_status_list
FROM product
LEFT JOIN archive_view ON archive_view.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_archive_view_count FROM product_archive_view;
SELECT * FROM product_archive_view LIMIT 5;

---------------------------------------------------------------------------
-- product_reference_view
---------------------------------------------------------------------------
DROP VIEW IF EXISTS product_reference_view;
CREATE VIEW product_reference_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_reference
   string_agg(product_reference.version::int8::text, ',' order by product_reference.id) as product_reference_version_list,
   string_agg(product_reference.type,                ',' order by product_reference.id) as product_reference_type_list,
   string_agg(product_reference.name,                ',' order by product_reference.id) as product_reference_name_list,
   string_agg(product_reference.path,                ',' order by product_reference.id) as product_reference_path_list,
   string_agg(product_reference.description,         ',' order by product_reference.id) as product_reference_description_list,
   string_agg(product_reference.status,              ',' order by product_reference.id) as product_reference_status_list

FROM product
LEFT JOIN product_reference ON product_reference.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_reference_view_count FROM product_reference_view;
SELECT * FROM product_reference_view LIMIT 5;

--------------------------------------------------
-- product_data_day_view
--------------------------------------------------
DROP VIEW IF EXISTS product_data_day_view CASCADE;
CREATE VIEW product_data_day_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_data_day
   string_agg(product_data_day.version::int8::text, ',' order by product_data_day.id) as product_data_day_version_list,
   string_agg(product_data_day.data_day::int8::text, ',' order by product_data_day.id) as product_data_day_list,
   string_agg(('1970-01-01 00:00:00 GMT'::timestamp + ((product_data_day.data_day/1000)::text)::interval)::timestamp::text,
               ',' order by product_data_day.id) as product_data_day_string_list
FROM product 
LEFT JOIN product_data_day ON product_data_day.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_data_day_view_count FROM product_data_day_view;
SELECT * FROM product_data_day_view LIMIT 5;

--*********************************************************************************************
-- Contact Provider Model 
--*********************************************************************************************

--------------------------------------------------
-- product_contact_view
--------------------------------------------------
DROP VIEW IF EXISTS product_contact_view CASCADE;
CREATE VIEW product_contact_view AS
SELECT

   -- product_contact
   product_contact.product_id as product_id,

   -- contact_provider_view 
   string_agg(contact_provider_view.contact_version::int8::text,                   
              ',' order by contact_provider_view.contact_id) as product_contact_version_list,
   string_agg(contact_provider_view.contact_role,                   
              ',' order by contact_provider_view.contact_id) as product_contact_role_list,
   string_agg(contact_provider_view.contact_first_name,             
              ',' order by contact_provider_view.contact_id) as product_contact_first_name_list,
   string_agg(contact_provider_view.contact_last_name,              
              ',' order by contact_provider_view.contact_id) as product_contact_last_name_list,
   string_agg(contact_provider_view.contact_middle_name,            
              ',' order by contact_provider_view.contact_id) as product_contact_middle_name_list,
   string_agg(contact_provider_view.contact_address,                
              ',' order by contact_provider_view.contact_id) as product_contact_address_list,
   string_agg(contact_provider_view.contact_notify_type,            
              ',' order by contact_provider_view.contact_id) as product_contact_notify_type_list,
   string_agg(contact_provider_view.contact_email,                  
              ',' order by contact_provider_view.contact_id) as product_contact_email_list,
   string_agg(contact_provider_view.contact_phone,                  
              ',' order by contact_provider_view.contact_id) as product_contact_phone_list,
   string_agg(contact_provider_view.contact_fax,                    
              ',' order by contact_provider_view.contact_id) as product_contact_fax_list,
   string_agg(contact_provider_view.provider_long_name,             
              ',' order by contact_provider_view.contact_id) as product_contact_provider_long_name_list,
   string_agg(contact_provider_view.provider_short_name,            
              ',' order by contact_provider_view.contact_id) as product_contact_provider_short_name_list,
   string_agg(contact_provider_view.provider_type,                  
              ',' order by contact_provider_view.contact_id) as product_contact_provider_type_list,
   string_agg(contact_provider_view.provider_resource_description_list, 
              ',' order by contact_provider_view.contact_id) as product_contact_provider_resource_descriptions_list,
   string_agg(contact_provider_view.provider_resource_name_list,        
              ',' order by contact_provider_view.contact_id) as product_contact_provider_resource_names_list,
   string_agg(contact_provider_view.provider_resource_path_list,        
              ',' order by contact_provider_view.contact_id) as product_contact_provider_resource_paths_list,
   string_agg(contact_provider_view.provider_resource_type_list,        
              ',' order by contact_provider_view.contact_id) as product_contact_provider_resource_types_list

FROM product_contact
LEFT JOIN contact_provider_view ON contact_provider_view.contact_id = product_contact.contact_id
GROUP BY product_contact.product_id;
SELECT COUNT(*) AS product_contact_view_count FROM product_contact_view;
SELECT * FROM product_contact_view LIMIT 5;

--*********************************************************************************************
-- Products Elements Model
--*********************************************************************************************

--------------------------------------------------
-- product_element_view
--------------------------------------------------
DROP VIEW IF EXISTS product_element_dd_view CASCADE;
CREATE VIEW product_element_dd_view AS
SELECT

   -- product_element
   product_element.id,
   product_element.product_id,
   product_element.version                as product_element_version,
   product_element.obligation_flag        as product_element_obligation_flag,
   product_element.scope                  as product_element_scope,

   -- element_dd
   string_agg(element_dd.version::int8::text,    ';' order by element_dd.id) as product_element_dd_versions,
   string_agg(element_dd.type,                   ';' order by element_dd.id) as product_element_dd_types,
   string_agg(element_dd.description,            ';' order by element_dd.id) as product_element_dd_descriptions,
   string_agg(element_dd.scope,                  ';' order by element_dd.id) as product_element_dd_scopes,
   string_agg(element_dd.long_name,              ';' order by element_dd.id) as product_element_dd_long_names,
   string_agg(element_dd.short_name,             ';' order by element_dd.id) as product_element_dd_short_names,
   string_agg(element_dd.max_length::int8::text, ';' order by element_dd.id) as product_element_dd_max_lengths

FROM product_element
LEFT JOIN element_dd ON product_element.element_id = element_dd.id
GROUP BY product_element.id;
SELECT COUNT(*) AS product_element_dd_view_count FROM product_element_dd_view;
SELECT * FROM product_element_dd_view LIMIT 5;

DROP VIEW IF EXISTS product_element_view CASCADE;
CREATE VIEW product_element_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_element_dd_view
   string_agg(product_element_dd_view.product_element_version::int8::text,
              ',' order by product_element_dd_view.id) as product_element_version_list,
   string_agg(product_element_dd_view.product_element_obligation_flag::boolean::text,
              ',' order by product_element_dd_view.id) as product_element_obligation_flag_list,
   string_agg(product_element_dd_view.product_element_scope,
              ',' order by product_element_dd_view.id) as product_element_scope_list,
   string_agg(product_element_dd_view.product_element_dd_versions,                   
              ',' order by product_element_dd_view.id) as product_element_dd_version_list,
   string_agg(product_element_dd_view.product_element_dd_types,                   
              ',' order by product_element_dd_view.id) as product_element_dd_type_list,
   string_agg(product_element_dd_view.product_element_dd_descriptions,            
              ',' order by product_element_dd_view.id) as product_element_dd_description_list,
   string_agg(product_element_dd_view.product_element_dd_scopes,                  
              ',' order by product_element_dd_view.id) as product_element_dd_scope_list,
   string_agg(product_element_dd_view.product_element_dd_long_names,              
              ',' order by product_element_dd_view.id) as product_element_dd_long_name_list,
   string_agg(product_element_dd_view.product_element_dd_short_names,             
              ',' order by product_element_dd_view.id) as product_element_dd_short_name_list,
   string_agg(product_element_dd_view.product_element_dd_max_lengths, 
              ',' order by product_element_dd_view.id) as product_element_dd_max_length_list

FROM product
LEFT JOIN product_element_dd_view ON product_element_dd_view.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_element_view_count FROM product_element_view;
SELECT * FROM product_element_view LIMIT 5;

--------------------------------------------------
-- product_datetime_view
--------------------------------------------------

DROP VIEW IF EXISTS product_datetime_view CASCADE;
CREATE VIEW product_datetime_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_datetime
   string_agg(product_datetime.version::int8::text,
              ',' order by product_datetime.id) as product_datetime_version_list,
   string_agg(product_datetime.value_long::int8::text,
              ',' order by product_datetime.id) as product_datetime_value_list,
   string_agg(('1970-01-01 00:00:00 GMT'::timestamp +
              ((product_datetime.value_long/1000)::text)::interval)::timestamp::text,
              ',' order by product_datetime.id) as product_datetime_value_string_list

FROM product
LEFT JOIN product_datetime ON product_datetime.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_datetime_view_count FROM product_datetime_view;
SELECT * FROM product_datetime_view LIMIT 5;

--------------------------------------------------
-- product_character_view
--------------------------------------------------
DROP VIEW IF EXISTS product_character_view CASCADE;
CREATE VIEW product_character_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_character
   string_agg(product_character.version::int8::text,
              ',' order by product_character.id) as product_character_version_list,
   string_agg(product_character.value,
              ',' order by product_character.id) as product_character_value_list

FROM product
LEFT JOIN product_character ON product_character.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_character_view_count FROM product_character_view;
SELECT * FROM product_character_view LIMIT 5;

--------------------------------------------------
-- product_integer_view
--------------------------------------------------
DROP VIEW IF EXISTS product_integer_view CASCADE;
CREATE VIEW product_integer_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_integer
   string_agg(product_integer.version::int8::text,
              ',' order by product_integer.id) as product_integer_version_list,
   string_agg(product_integer.units,
              ',' order by product_integer.id) as product_integer_units_list,
   string_agg(product_integer.value::int::text,
              ',' order by product_integer.id) as product_integer_value_list

FROM product
LEFT JOIN product_integer ON product_integer.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_integer_view_count FROM product_integer_view;
SELECT * FROM product_integer_view LIMIT 5;

--------------------------------------------------
-- product_real_view
--------------------------------------------------
DROP VIEW IF EXISTS product_real_view CASCADE;
CREATE VIEW product_real_view AS
SELECT

   -- product
   product.id as product_id,

   -- product_real
   string_agg(product_real.version::int8::text,
              ',' order by product_real.id) as product_real_version_list,
   string_agg(product_real.units,
              ',' order by product_real.id) as product_real_units_list,
   string_agg(product_real.value::numeric::text,
              ',' order by product_real.id) as product_real_value_list

FROM product
LEFT JOIN product_real ON product_real.product_id = product.id
GROUP BY product.id;
SELECT COUNT(*) AS product_real_view_count FROM product_real_view;
SELECT * FROM product_real_view LIMIT 5;


--*********************************************************************************************
-- Product
--*********************************************************************************************

-----------------------------------------------------------------------------------------------
-- product_view
-----------------------------------------------------------------------------------------------
DROP VIEW IF EXISTS product_view CASCADE;
CREATE VIEW product_view AS 
SELECT 

   -- product
   product.id,
   product.id as product_id, 
   product.pt_id        as product_pt_id,
   product.partial_id   as product_partial_id,
   product.version      as product_version,
   product.revision     as product_revision,
   product.name         as product_name,
   product.rel_path     as product_rel_path,
   product.root_path    as product_root_path,
   product.status       as product_status,
   product.start_time   as product_start_time,
   product.stop_time    as product_stop_time,
   product.create_time  as product_create_time,
   product.archive_time as product_archive_time,
   '1970-01-01 00:00:00 GMT'::timestamp + ((product.start_time/1000)::text)::interval   AS product_start_time_string,
   '1970-01-01 00:00:00 GMT'::timestamp + ((product.stop_time/1000)::text)::interval    AS product_stop_time_string,
   '1970-01-01 00:00:00 GMT'::timestamp + ((product.create_time/1000)::text)::interval  AS product_create_time_string,
   '1970-01-01 00:00:00 GMT'::timestamp + ((product.archive_time/1000)::text)::interval AS product_archive_time_string,

   -- product_granule_view
   product_granule_id_list,
   product_granule_version_list,
   product_granule_dataset_id_list,
   product_granule_metadata_endpoint_list,
   product_granule_remote_granule_ur_list,

   -- product_operation_view
   product_operation_version_list,
   product_operation_agent_list,
   product_operation_list,
   product_operation_command_list,
   product_operation_arguments_list,
   product_operation_start_time_list,
   product_operation_stop_time_list,
   product_operation_start_time_string_list,
   product_operation_stop_time_string_list,

   -- product_meta_history_view
   product_meta_history_version,
   product_meta_history_version_id,
   product_meta_history_revision_history,
   product_meta_history_last_revision_date,
   product_meta_history_creation_date,
   product_meta_history_last_revision_date_string,
   product_meta_history_creation_date_string,

   -- product_archive_view
   product_archive_name_list,
   product_archive_type_list,
   product_archive_version_list,
   product_archive_file_size_list,
   product_archive_checksum_list,
   product_archive_compress_flag_list,
   product_archive_status_list,
   product_archive_reference_description_list,
   product_archive_reference_name_list,
   product_archive_reference_type_list,
   product_archive_reference_status_list,

   -- product_reference_view
   product_reference_version_list,
   product_reference_type_list,
   product_reference_name_list,
   product_reference_path_list,
   product_reference_description_list,
   product_reference_status_list,

   -- product_data_day
   product_data_day_version_list,
   product_data_day_list,
   product_data_day_string_list,

   -- product_contact_view
   product_contact_role_list,
   product_contact_version_list,
   product_contact_first_name_list,
   product_contact_last_name_list,
   product_contact_middle_name_list,
   product_contact_address_list,
   product_contact_notify_type_list,
   product_contact_email_list,
   product_contact_phone_list,
   product_contact_fax_list,
   product_contact_provider_long_name_list,
   product_contact_provider_short_name_list,
   product_contact_provider_type_list,
   product_contact_provider_resource_descriptions_list,
   product_contact_provider_resource_names_list,
   product_contact_provider_resource_paths_list,
   product_contact_provider_resource_types_list,

   -- product_element_view
   product_element_version_list,
   product_element_obligation_flag_list,
   product_element_scope_list,
   product_element_dd_version_list,
   product_element_dd_type_list,
   product_element_dd_description_list,
   product_element_dd_scope_list,
   product_element_dd_long_name_list,
   product_element_dd_short_name_list,
   product_element_dd_max_length_list,

   -- product_datetime_view
   product_datetime_version_list,
   product_datetime_value_list,
   product_datetime_value_string_list,

   -- product_character_view
   product_character_version_list,
   product_character_value_list,

   -- product_integer_view
   product_integer_version_list,
   product_integer_value_list,
   product_integer_units_list,

   -- product_real_view
   product_real_version_list,
   product_real_value_list,
   product_real_units_list

FROM
   product,
   product_granule_view,
   product_operation_view,
   product_meta_history_view,
   product_archive_view,
   product_reference_view,
   product_data_day_view,
   product_contact_view,
   product_element_view,
   product_datetime_view,
   product_character_view,
   product_integer_view,
   product_real_view
WHERE
   product.id = product_granule_view.product_id AND
   product.id = product_operation_view.product_id AND
   product.id = product_meta_history_view.product_id AND
   product.id = product_archive_view.product_id AND
   product.id = product_reference_view.product_id AND
   product.id = product_data_day_view.product_id AND
   product.id = product_contact_view.product_id AND
   product.id = product_element_view.product_id AND
   product.id = product_datetime_view.product_id AND
   product.id = product_character_view.product_id AND
   product.id = product_integer_view.product_id AND
   product.id = product_real_view.product_id;

SELECT COUNT(*) AS product_view_count FROM product_view;
SELECT * FROM product_view LIMIT 5;
